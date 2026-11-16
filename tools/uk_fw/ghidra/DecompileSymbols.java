// Decompile selected functions of the imported program to C.
//
// Runs headless inside Ghidra; driven by tools/uk_fw/decompile.py. Argument 1 is
// the output directory, argument 2 is a filter: "ALL", a name substring, or a
// comma-separated list of addresses (as written in the retained listings, e.g.
// 0x190c70). Function bodies are written one file each, with the entry address and
// the signature in a header so a reader can match the original listing.
//@category Ioniq

import java.io.File;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;

public class DecompileSymbols extends GhidraScript {

    private static final int DEFAULT_MAX_FUNCTIONS = 4000;
    private static final int DEFAULT_TIMEOUT_SECONDS = 90;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            println("usage: DecompileSymbols <outdir> <ALL|name-substring|0xaddr,...>");
            return;
        }
        File outDir = new File(args[0]);
        if (!outDir.isDirectory() && !outDir.mkdirs()) {
            println("cannot create " + outDir);
            return;
        }
        String filter = args[1];
        int maxFunctions = DEFAULT_MAX_FUNCTIONS;
        if (args.length > 2) {
            try {
                maxFunctions = Integer.parseInt(args[2]);
            }
            catch (NumberFormatException ignored) {
                maxFunctions = DEFAULT_MAX_FUNCTIONS;
            }
        }
        if (maxFunctions <= 0) {
            maxFunctions = Integer.MAX_VALUE;
        }
        // Optional "index/count" slice so several workers can share one analysis
        // without opening the same project: each takes every count-th function.
        int timeoutSeconds = DEFAULT_TIMEOUT_SECONDS;
        if (args.length > 4) {
            try {
                timeoutSeconds = Integer.parseInt(args[4]);
            }
            catch (NumberFormatException ignored) {
                timeoutSeconds = DEFAULT_TIMEOUT_SECONDS;
            }
        }
        if (timeoutSeconds <= 0) {
            timeoutSeconds = DEFAULT_TIMEOUT_SECONDS;
        }
        int sliceIndex = 0;
        int sliceCount = 1;
        if (args.length > 3 && args[3].contains("/")) {
            String[] parts = args[3].split("/");
            try {
                sliceIndex = Integer.parseInt(parts[0]);
                sliceCount = Math.max(1, Integer.parseInt(parts[1]));
            }
            catch (NumberFormatException ignored) {
                sliceIndex = 0;
                sliceCount = 1;
            }
        }
        List<String> addresses = new ArrayList<>();
        for (String part : filter.split(",")) {
            String trimmed = part.trim();
            if (trimmed.toLowerCase().startsWith("0x")) {
                addresses.add(trimmed);
            }
        }

        if ("LIST".equalsIgnoreCase(filter)) {
            // Inventory without decompiling: entry, name, body size, and whether the
            // function already has a C file. Lets a completion report be counted.
            File listFile = new File(outDir, "functions.tsv");
            int withBody = 0;
            int done = 0;
            int thunks = 0;
            int iterated = 0;
            try (PrintWriter list = new PrintWriter(listFile, "UTF-8")) {
                list.println("entry\tname\tbody_bytes\thas_c_file");
                for (Function function : currentProgram.getFunctionManager()
                        .getFunctions(true)) {
                    iterated++;
                    boolean hasBody = function.getBody() != null
                        && function.getBody().getNumAddresses() > 0;
                    if (function.isThunk()) {
                        thunks++;
                    }
                    boolean written = new File(outDir, fileName(function)).isFile();
                    if (hasBody) {
                        withBody++;
                    }
                    if (written) {
                        done++;
                    }
                    list.println(function.getEntryPoint() + "\t" + function.getName()
                        + "\t" + function.getBody().getNumAddresses() + "\t" + written);
                }
            }
            println("inventory: functions="
                + currentProgram.getFunctionManager().getFunctionCount()
                + " iterated=" + iterated
                + " withBody=" + withBody + " withC=" + done
                + " thunks=" + thunks);
            return;
        }

        java.util.Set<String> missingEntries = new java.util.HashSet<>();
        if ("MISSING".equalsIgnoreCase(filter)) {
            // Decompile exactly the entries the inventory marked as unanswered,
            // bypassing the resume predicate that has been disagreeing with it.
            File inventory = new File(outDir, "functions.tsv");
            if (!inventory.isFile()) {
                println("MISSING needs functions.tsv; run --select LIST first");
                return;
            }
            try (java.io.BufferedReader reader = new java.io.BufferedReader(
                    new java.io.FileReader(inventory))) {
                String line;
                boolean header = true;
                while ((line = reader.readLine()) != null) {
                    if (header) {
                        header = false;
                        continue;
                    }
                    String[] columns = line.split("\\t");
                    if (columns.length >= 4 && "false".equals(columns[3])) {
                        missingEntries.add(columns[0].trim().toLowerCase());
                    }
                }
            }
            println("MISSING: " + missingEntries.size() + " entries from the inventory");
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(false);
        if (!decompiler.openProgram(currentProgram)) {
            println("decompiler refused the program");
            return;
        }

        FunctionManager functions = currentProgram.getFunctionManager();
        if (!addresses.isEmpty()) {
            println("layout: imageBase=" + currentProgram.getImageBase()
                + " min=" + currentProgram.getMinAddress()
                + " max=" + currentProgram.getMaxAddress()
                + " functions=" + functions.getFunctionCount());
        }
        java.util.Set<Function> targets = new java.util.LinkedHashSet<>();
        if (!addresses.isEmpty()) {
            // A listing address can name a call target, a body offset, or a virtual
            // address in a program Ghidra loaded at a different image base, so each
            // candidate is resolved through containing/at/before, not by equality.
            for (String candidate : addresses) {
                long value = Long.parseUnsignedLong(candidate.substring(2), 16);
                resolveAddress(functions, value, targets);
                resolveAddress(functions, currentProgram.getImageBase().getOffset() + value, targets);
                if (value > currentProgram.getImageBase().getOffset()) {
                    resolveAddress(functions, value - currentProgram.getImageBase().getOffset(),
                                   targets);
                }
            }
        }

        int written = 0;
        int skipped = 0;
        int failed = 0;
        long visited = 0;
        java.util.Iterator<Function> iterator = targets.isEmpty()
            ? functions.getFunctions(true) : targets.iterator();
        while (iterator.hasNext()) {
            Function function = iterator.next();
            long position = visited++;
            if (sliceCount > 1 && (position % sliceCount) != sliceIndex) {
                continue;
            }
            if (written >= maxFunctions) {
                println("stopped at " + maxFunctions + " functions");
                break;
            }
            if (targets.isEmpty() && !selected(function, filter, addresses)) {
                continue;
            }
            // Resume: a finished file is never redone, so repeated passes converge and
            // an interrupted run costs only the functions it had not reached.
            File already = new File(outDir, fileName(function));
            if (already.isFile() && already.length() > 0) {
                skipped++;
                continue;
            }
            DecompileResults result =
                decompiler.decompileFunction(function, timeoutSeconds, monitor);
            if (!result.decompileCompleted()) {
                failed++;
                String reason = result.getErrorMessage();
                if (reason == null) {
                    reason = "(no message)";
                }
                try (PrintWriter failure = new PrintWriter(new java.io.FileWriter(
                        new File(outDir, "failures.tsv"), true))) {
                    failure.println(function.getEntryPoint() + "\t"
                        + function.getName() + "\t"
                        + reason.replaceAll("[\\t\\r\\n]+", " "));
                }
                if (failed <= 20) {
                    println("failed " + function.getEntryPoint() + " : " + reason);
                }
                continue;
            }
            write(outDir, function, result.getDecompiledFunction().getC());
            written++;
        }

        println("decompiled " + written + " function(s), skipped " + skipped
            + ", failed " + failed + ", iterated " + visited + " from " + filter);
        decompiler.dispose();
    }

    private void resolveAddress(FunctionManager functions, long offset,
                                java.util.Set<Function> targets) {
        if (offset < 0 || offset > 0xFFFFFFFFL) {
            return;
        }
        Address address = currentProgram.getAddressFactory().getDefaultAddressSpace()
            .getAddress(offset);
        Function function = functions.getFunctionContaining(address);
        if (function == null) {
            function = functions.getFunctionAt(address);
        }
        if (function == null) {
            function = currentProgram.getListing().getFunctionContaining(address);
        }
        if (function == null) {
            // An address from a retained listing can sit outside whatever the analysis
            // reached (a 143 MB binary is routinely time-limited). Disassemble and create
            // the function on demand so the address stays decompilable.
            try {
                if (currentProgram.getListing().getInstructionAt(address) == null) {
                    disassemble(address);
                }
                function = createFunction(address, null);
            }
            catch (Exception exception) {
                println("cannot create a function at " + address + ": " + exception);
            }
        }
        if (function == null) {
            // A retained listing address can point a few bytes away from the analysed
            // entry, so fall back to the nearest entry at or below it.
            long best = Long.MIN_VALUE;
            for (Function candidate : functions.getFunctions(true)) {
                long entry = candidate.getEntryPoint().getOffset();
                if (entry <= offset && entry > best) {
                    best = entry;
                    function = candidate;
                }
            }
            if (function != null) {
                println("resolved " + offset + " to the nearest entry at " + best);
            }
        }
        if (function != null) {
            targets.add(function);
        }
    }

    private boolean selected(Function function, String filter, List<String> addresses) {
        if (!addresses.isEmpty()) {
            Address entry = function.getEntryPoint();
            for (String candidate : addresses) {
                if (entry.toString().equalsIgnoreCase(candidate)
                    || entry.toString().toLowerCase().endsWith(candidate.substring(2).toLowerCase())) {
                    return true;
                }
            }
            return false;
        }
        if ("ALL".equalsIgnoreCase(filter)) {
            return true;
        }
        return function.getName().toLowerCase().contains(filter.toLowerCase());
    }

    /** Deterministic, filesystem-safe name shared by the skip check and the write. */
    private String fileName(Function function) {
        String name = function.getName().replaceAll("[^A-Za-z0-9_.-]", "_");
        // C++ mangled names blow past the filesystem's 255-byte limit; keep the head
        // and a stable hash so the file is short, unique and reproducible.
        String head = name.length() > 60 ? name.substring(0, 60) : name;
        java.util.zip.CRC32 crc = new java.util.zip.CRC32();
        crc.update(name.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        return String.format("%s_%s_%08x.c", function.getEntryPoint(), head, crc.getValue());
    }

    private void write(File outDir, Function function, String code) throws Exception {
        String file = fileName(function);
        try (PrintWriter writer = new PrintWriter(new File(outDir, file), "UTF-8")) {
            writer.println("/* " + currentProgram.getName()
                + " | " + function.getEntryPoint()
                + " | " + function.getPrototypeString(false, false) + " */");
            writer.println(code);
        }
    }
}
