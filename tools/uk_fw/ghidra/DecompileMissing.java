// Decompile exactly the functions an inventory marked as unanswered.
//
// Written as its own script because the general one grew a resume predicate that
// disagreed with the inventory for AppNavi. This one trusts functions.tsv only:
// args are <outdir> <functions.tsv> <slice i/n> <timeout seconds>.
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
import ghidra.program.model.listing.Function;

public class DecompileMissing extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            println("usage: DecompileMissing <outdir> <functions.tsv> [i/n] [timeout]");
            return;
        }
        File outDir = new File(args[0]);
        File inventory = new File(args[1]);
        int sliceIndex = 0;
        int sliceCount = 1;
        int timeoutSeconds = 90;
        if (args.length > 2 && args[2].contains("/")) {
            String[] parts = args[2].split("/");
            sliceIndex = Integer.parseInt(parts[0]);
            sliceCount = Math.max(1, Integer.parseInt(parts[1]));
        }
        if (args.length > 3) {
            timeoutSeconds = Integer.parseInt(args[3]);
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
        println("missing entries: " + missing.size() + ", slice " + sliceIndex + "/"
            + sliceCount);

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(false);
        if (!decompiler.openProgram(currentProgram)) {
            println("decompiler refused the program");
            return;
        }

        int written = 0;
        int failed = 0;
        int position = 0;
        for (Function function : currentProgram.getFunctionManager().getFunctions(true)) {
            String entry = function.getEntryPoint().toString().trim().toLowerCase();
            if (!missing.contains(entry)) {
                continue;
            }
            if ((position++ % sliceCount) != sliceIndex) {
                continue;
            }
            DecompileResults result =
                decompiler.decompileFunction(function, timeoutSeconds, monitor);
            if (!result.decompileCompleted()) {
                failed++;
                String reason = result.getErrorMessage();
                try (PrintWriter failure = new PrintWriter(new FileWriter(
                        new File(outDir, "missing-failures.tsv"), true))) {
                    failure.println(function.getEntryPoint() + "\t" + function.getName()
                        + "\t" + (reason == null ? "(none)" : reason.replaceAll("[\t\r\n]+", " ")));
                }
                continue;
            }
            String name = function.getName().replaceAll("[^A-Za-z0-9_.-]", "_");
            String head = name.length() > 60 ? name.substring(0, 60) : name;
            CRC32 crc = new CRC32();
            crc.update(name.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            File target = new File(outDir, String.format("%s_%s_%08x.c",
                function.getEntryPoint(), head, crc.getValue()));
            try (PrintWriter writer = new PrintWriter(target, "UTF-8")) {
                writer.println("/* " + currentProgram.getName() + " | "
                    + function.getEntryPoint() + " | "
                    + function.getPrototypeString(false, false) + " */");
                writer.println(result.getDecompiledFunction().getC());
            }
            written++;
        }
        println("missing pass: written " + written + ", failed " + failed
            + ", slice " + sliceIndex + "/" + sliceCount);
        decompiler.dispose();
    }
}
