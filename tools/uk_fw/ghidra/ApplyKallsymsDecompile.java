// Apply recovered kallsyms names to a freshly analysed vmlinux and decompile
// a priority set of security-relevant functions.
//
// Read-only with respect to the input image; all output goes to a caller-supplied
// directory. No code from the target is executed.
//
// @category Ioniq5

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.util.task.ConsoleTaskMonitor;

public class ApplyKallsymsDecompile extends GhidraScript {

    private PrintWriter appliedLog;
    private PrintWriter skippedLog;
    private int renamedFunctions = 0;
    private int createdLabels = 0;
    private int createdFunctions = 0;
    private int renamedDataSymbols = 0;
    private int aliasesCreated = 0;
    private int skipped = 0;
    private int outsideMemory = 0;
    private int failedFunctionCreate = 0;

    private static boolean isTextType(String typeChar) {
        return "tTwW".indexOf(typeChar.charAt(0)) >= 0;
    }

    /**
     * Ghidra's analyzers invent names such as DAT_00401000, LAB_.., PTR_..,
     * FUN_.., SUB_.. when an image is stripped. Those are placeholders and are
     * safe to replace with a recovered symbol name.
     */
    private static boolean isAutoName(String name) {
        String[] prefixes = { "DAT_", "LAB_", "PTR_", "UNK_", "SUB_", "FUN_",
            "JUMP_", "EXT_", "thunk_FUN_", "OFF_", "switchD_", "caseD_" };
        for (String prefix : prefixes) {
            if (name.startsWith(prefix)) {
                return true;
            }
        }
        return false;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 3) {
            printerr("usage: ApplyKallsymsDecompile <kallsyms.tsv> <outdir> <priority.txt>");
            return;
        }
        String tsvPath = args[0];
        String outDir = args[1];
        String priorityPath = args[2];
        int maxNewFunctions = args.length > 3 ? Integer.parseInt(args[3]) : 20000;

        new File(outDir).mkdirs();
        new File(outDir, "decompiled").mkdirs();
        appliedLog = new PrintWriter(new FileWriter(new File(outDir, "symbols-applied.tsv")));
        skippedLog = new PrintWriter(new FileWriter(new File(outDir, "symbols-skipped.tsv")));
        Set<Long> renamedAddresses = new LinkedHashSet<>();

        Memory memory = currentProgram.getMemory();
        List<String[]> rows = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(tsvPath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.isEmpty()) {
                    continue;
                }
                int tab = line.indexOf('\t');
                if (tab <= 0) {
                    continue;
                }
                rows.add(new String[] { line.substring(0, tab), line.substring(tab + 1) });
            }
        }
        println("kallsyms rows read: " + rows.size());

        // Pass 1: rename existing functions, label everything else, and create
        // functions for text symbols that analysis missed.
        for (String[] row : rows) {
            long value = Long.parseUnsignedLong(row[0], 16);
            Address address = toAddr(value);
            if (address == null || !memory.contains(address)) {
                outsideMemory++;
                continue;
            }
            String rawName = row[1];
            if (rawName.isEmpty()) {
                skipped++;
                continue;
            }
            String typeChar = rawName.substring(0, 1);
            String name = rawName.substring(1);
            if (name.isEmpty()) {
                skipped++;
                continue;
            }

            Function function = getFunctionAt(address);
            if (function != null) {
                if (renamedAddresses.contains(value)) {
                    // Second kallsyms entry at the same entry point: keep as alias.
                    try {
                        createLabel(address, name, true, SourceType.IMPORTED);
                        aliasesCreated++;
                        appliedLog.println(row[0] + "\t" + name + "\talias");
                    }
                    catch (Exception exception) {
                        skipped++;
                        skippedLog.println(row[0] + "\t" + rawName + "\talias:" + exception.getMessage());
                    }
                    continue;
                }
                try {
                    function.setName(name, SourceType.IMPORTED);
                    renamedAddresses.add(value);
                    renamedFunctions++;
                    appliedLog.println(row[0] + "\t" + name + "\tfunction-renamed");
                }
                catch (Exception exception) {
                    skipped++;
                    skippedLog.println(row[0] + "\t" + rawName + "\trename:" + exception.getMessage());
                }
                continue;
            }

            Symbol existing = getSymbolAt(address);
            if (existing != null) {
                if (isAutoName(existing.getName()) && !renamedAddresses.contains(value)) {
                    try {
                        existing.setName(name, SourceType.IMPORTED);
                        renamedAddresses.add(value);
                        renamedDataSymbols++;
                        appliedLog.println(row[0] + "\t" + name + "\tauto-symbol-renamed");
                        continue;
                    }
                    catch (Exception exception) {
                        skipped++;
                        skippedLog.println(row[0] + "\t" + rawName + "\tauto-rename:" + exception.getMessage());
                        continue;
                    }
                }
                skipped++;
                skippedLog.println(row[0] + "\t" + rawName + "\texisting-symbol");
                continue;
            }

            if (isTextType(typeChar) && createdFunctions < maxNewFunctions) {
                Function created = null;
                try {
                    created = createFunction(address, name);
                }
                catch (Exception exception) {
                    failedFunctionCreate++;
                }
                if (created != null) {
                    renamedAddresses.add(value);
                    createdFunctions++;
                    appliedLog.println(row[0] + "\t" + name + "\tfunction-created");
                    continue;
                }
            }

            try {
                createLabel(address, name, true, SourceType.IMPORTED);
                renamedAddresses.add(value);
                createdLabels++;
                appliedLog.println(row[0] + "\t" + name + "\tlabel");
            }
            catch (Exception exception) {
                skipped++;
                skippedLog.println(row[0] + "\t" + rawName + "\tlabel:" + exception.getMessage());
            }
        }
        appliedLog.close();
        skippedLog.close();

        // Pass 2: decompile the priority functions.
        List<String> priority = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(priorityPath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (!line.isEmpty() && !line.startsWith("#")) {
                    priority.add(line);
                }
            }
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        decompiler.openProgram(currentProgram);

        PrintWriter index = new PrintWriter(new FileWriter(new File(outDir, "decompile-index.tsv")));
        PrintWriter callers = new PrintWriter(new FileWriter(new File(outDir, "callers.tsv")));
        PrintWriter callees = new PrintWriter(new FileWriter(new File(outDir, "callees.tsv")));

        int decompiled = 0;
        int missing = 0;
        for (String name : priority) {
            Function function = resolve(name);
            if (function == null) {
                missing++;
                index.println("MISSING\t\t" + name);
                println("priority function not found: " + name);
                continue;
            }
            Address entry = function.getEntryPoint();
            String safe = name.replaceAll("[^A-Za-z0-9_.-]", "_");
            File target = new File(new File(outDir, "decompiled"), safe + ".c");
            DecompileResults results = decompiler.decompileFunction(function, 120,
                new ConsoleTaskMonitor());
            try (PrintWriter writer = new PrintWriter(new FileWriter(target))) {
                writer.println("// " + function.getName() + " @ " + entry);
                writer.println("// signature: " + function.getPrototypeString(false, false));
                writer.println();
                if (results != null && results.decompileCompleted()) {
                    writer.println(results.getDecompiledFunction().getC());
                    decompiled++;
                }
                else {
                    writer.println("// DECOMPILATION FAILED: "
                        + (results == null ? "null result" : results.getErrorMessage()));
                }
            }
            for (Function caller : function.getCallingFunctions(monitor)) {
                callers.println(function.getName() + "\t" + caller.getName() + "\t"
                    + caller.getEntryPoint());
            }
            for (Function callee : function.getCalledFunctions(monitor)) {
                callees.println(function.getName() + "\t" + callee.getName() + "\t"
                    + callee.getEntryPoint());
            }
            index.println("OK\t" + entry + "\t" + name);
        }
        index.close();
        callers.close();
        callees.close();
        decompiler.dispose();

        FunctionIterator allFunctions = currentProgram.getFunctionManager().getFunctions(true);
        int totalFunctions = 0;
        while (allFunctions.hasNext()) {
            allFunctions.next();
            totalFunctions++;
        }

        try (PrintWriter stats = new PrintWriter(new FileWriter(new File(outDir, "stats.txt")))) {
            stats.println("program=" + currentProgram.getName());
            stats.println("executable=" + currentProgram.getExecutableSHA256());
            stats.println("kallsyms_rows=" + rows.size());
            stats.println("renamed_functions=" + renamedFunctions);
            stats.println("renamed_auto_symbols=" + renamedDataSymbols);
            stats.println("aliases_created=" + aliasesCreated);
            stats.println("created_functions=" + createdFunctions);
            stats.println("created_labels=" + createdLabels);
            stats.println("failed_function_create=" + failedFunctionCreate);
            stats.println("skipped=" + skipped);
            stats.println("outside_memory=" + outsideMemory);
            stats.println("total_functions_after=" + totalFunctions);
            stats.println("priority_requested=" + priority.size());
            stats.println("priority_decompiled=" + decompiled);
            stats.println("priority_missing=" + missing);
        }
        println("STATS renamed=" + renamedFunctions + " created_fn=" + createdFunctions
            + " labels=" + createdLabels + " decompiled=" + decompiled + " missing=" + missing);
    }

    private Function findByName(String name) {
        for (Function function : currentProgram.getFunctionManager().getFunctions(true)) {
            if (function.getName().equals(name)) {
                return function;
            }
        }
        return null;
    }

    /**
     * Resolve a priority name to a Function, creating one at the labelled
     * address when analysis never treated it as a function (common for syscall
     * entry points and static helpers reachable only through tables).
     */
    private Function resolve(String name) throws Exception {
        Function existing = findByName(name);
        if (existing != null) {
            return existing;
        }
        var symbols = currentProgram.getSymbolTable().getSymbols(name);
        while (symbols.hasNext()) {
            Symbol symbol = symbols.next();
            Address address = symbol.getAddress();
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                return containing;
            }
            if (containing != null) {
                println("NOTE " + name + " is inside " + containing.getName()
                    + " at " + containing.getEntryPoint());
                return null;
            }
            Function created = createFunction(address, name);
            if (created != null) {
                println("created function on demand: " + name + " @ " + address);
                return created;
            }
        }
        return null;
    }
}
