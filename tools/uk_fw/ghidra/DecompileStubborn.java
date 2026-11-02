// Last pass over functions the decompiler refuses: retry after re-disassembling the
// entry, and if it still refuses, emit a disassembly listing so every body-bearing
// function has an artifact and the reason is recorded with it.
//
// args: <outdir> <functions.tsv> <slice i/n> <timeout seconds>
//@category Ioniq

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.CRC32;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;

public class DecompileStubborn extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            println("usage: DecompileStubborn <outdir> <functions.tsv> [i/n] [timeout]");
            return;
        }
        File outDir = new File(args[0]);
        File inventory = new File(args[1]);
        int sliceIndex = 0;
        int sliceCount = 1;
        int timeoutSeconds = 1800;
        String spec = args.length > 2 ? args[2] : "";
        int slash = spec.indexOf('/');
        if (slash > 0) {
            sliceIndex = Integer.parseInt(spec.substring(0, slash));
            int declared = Integer.parseInt(spec.substring(slash + 1));
            if (declared > 0) {
                sliceCount = declared;
            }
        }
        if (args.length > 3) {
            int requested = Integer.parseInt(args[3]);
            if (requested > 0) {
                timeoutSeconds = requested;
            }
        }

        List<String> missing = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(inventory))) {
            String line;
            boolean header = true;
            while ((line = reader.readLine()) != null) {
                if (header) {
                    header = false;
                    continue;
                }
                String[] columns = line.split("\t");
                if (columns.length >= 4 && "false".equals(columns[3])) {
                    missing.add(columns[0].trim().toLowerCase());
                }
            }
        }
        println("stubborn entries: " + missing.size() + ", slice " + sliceIndex + "/"
            + sliceCount);

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(false);
        if (!decompiler.openProgram(currentProgram)) {
            println("decompiler refused the program");
            return;
        }

        int recovered = 0;
        int listed = 0;
        int position = 0;
        for (Function function : currentProgram.getFunctionManager().getFunctions(true)) {
            String entryText = function.getEntryPoint().toString().trim().toLowerCase();
            if (!missing.contains(entryText)) {
                continue;
            }
            if ((position++ % sliceCount) != sliceIndex) {
                continue;
            }
            DecompileResults result =
                decompiler.decompileFunction(function, timeoutSeconds, monitor);
            ghidra.program.model.address.AddressSetView bodyCopy = function.getBody();
            String nameCopy = function.getName();
            Address entryCopy = function.getEntryPoint();
            if (!result.decompileCompleted()) {
                // One non-destructive retry: clear and re-disassemble the existing body
                // in place. The earlier version deleted the function first, which left
                // the program without it when the rebuild failed - that is what turned
                // a decompiler refusal into a missing function.
                try {
                    clearListing(bodyCopy);
                    for (Address address : bodyCopy.getAddresses(true)) {
                        if (getInstructionAt(address) == null) {
                            disassemble(address);
                        }
                    }
                    Function recreated = createFunction(entryCopy, nameCopy);
                    Function current =
                        currentProgram.getFunctionManager().getFunctionAt(entryCopy);
                    if (current != null) {
                        function = current;
                        result = decompiler.decompileFunction(function, timeoutSeconds, monitor);
                    }
                    else if (recreated != null) {
                        function = recreated;
                        result = decompiler.decompileFunction(function, timeoutSeconds, monitor);
                    }
                }
                catch (Exception exception) {
                    println("retry failed at " + entryCopy + ": " + exception);
                }
            }
            if (function != null && result.decompileCompleted()) {
                write(outDir, function, result.getDecompiledFunction().getC());
                recovered++;
                continue;
            }
            // Still refused: publish the disassembly with the exact reason, so the
            // inventory closes with a documented artifact instead of a hole.
            String reason = result == null ? "(no result)" : result.getErrorMessage();
            if (function == null) {
                // Nothing to hand to writeListing: publish from the captured body so the
                // inventory still gets an artifact for this entry.
                writeBodyListing(outDir, entryCopy, nameCopy, bodyCopy, reason);
                listed++;
            }
            else {
                listed++;
                writeListing(outDir, function, reason);
                try (PrintWriter record = new PrintWriter(new FileWriter(
                        new File(outDir, "listing-fallbacks.tsv"), true))) {
                    record.println(function.getEntryPoint() + "\t" + function.getName()
                        + "\t" + (reason == null ? "(none)" : reason.replaceAll("[\t\r\n]+", " ")));
                }
            }
        }
        println("stubborn pass: recovered " + recovered + ", listed " + listed
            + ", slice " + sliceIndex + "/" + sliceCount);
        decompiler.dispose();
    }

    private String baseName(Function function) {
        String name = function.getName().replaceAll("[^A-Za-z0-9_.-]", "_");
        String head = name.length() > 60 ? name.substring(0, 60) : name;
        CRC32 crc = new CRC32();
        crc.update(name.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        return String.format("%s_%s_%08x", function.getEntryPoint(), head, crc.getValue());
    }

    private void write(File outDir, Function function, String code) throws Exception {
        File target = new File(outDir, baseName(function) + ".c");
        try (PrintWriter writer = new PrintWriter(target, "UTF-8")) {
            writer.println("/* " + currentProgram.getName() + " | " + function.getEntryPoint()
                + " | " + function.getPrototypeString(false, false) + " */");
            writer.println(code);
        }
    }

    private void writeBodyListing(File outDir, Address entry, String name,
                                  ghidra.program.model.address.AddressSetView body,
                                  String reason) throws Exception {
        String safe = name.replaceAll("[^A-Za-z0-9_.-]", "_");
        String head = safe.length() > 60 ? safe.substring(0, 60) : safe;
        CRC32 crc = new CRC32();
        crc.update(safe.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        File target = new File(outDir, String.format("%s_%s_%08x.asm", entry, head,
            crc.getValue()));
        try (PrintWriter writer = new PrintWriter(target, "UTF-8")) {
            writer.println("; " + currentProgram.getName() + " | " + entry + " | " + name);
            writer.println("; decompiler refused: "
                + (reason == null ? "(no message)" : reason));
            writer.println("; listing published from the analysed body captured before the retry");
            for (Instruction instruction : currentProgram.getListing()
                    .getInstructions(body, true)) {
                writer.println(instruction.getAddress() + "  " + instruction);
            }
        }
    }

    private void writeListing(File outDir, Function function, String reason) throws Exception {
        File target = new File(outDir, baseName(function) + ".asm");
        try (PrintWriter writer = new PrintWriter(target, "UTF-8")) {
            writer.println("; " + currentProgram.getName() + " | " + function.getEntryPoint()
                + " | " + function.getName());
            writer.println("; decompiler refused: "
                + (reason == null ? "(no message)" : reason));
            writer.println("; listing of the analysed body, published so the function is"
                + " not a hole in the inventory");
            for (Instruction instruction : currentProgram.getListing()
                    .getInstructions(function.getBody(), true)) {
                writer.println(instruction.getAddress() + "  " + instruction);
            }
        }
    }
}
