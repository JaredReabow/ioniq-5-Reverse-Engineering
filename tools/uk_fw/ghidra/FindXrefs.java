// List every reference to one or more addresses, with the containing function.
//
// Usage: FindXrefs.java 0xffffffff81a1e330 [more addresses...]
//
// Read-only: the analysis database is queried, nothing is modified.

// @category Ioniq5

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;

public class FindXrefs extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0) {
            println("usage: FindXrefs.java <address> [address...]");
            return;
        }
        for (String raw : args) {
            Address target = toAddr(raw);
            println("=== references to " + target + " ===");
            Reference[] refs = getReferencesTo(target);
            int count = 0;
            for (Reference ref : refs) {
                Address from = ref.getFromAddress();
                Function fn = getFunctionContaining(from);
                String where = fn == null
                        ? "(not in a function)"
                        : fn.getName() + " @ " + fn.getEntryPoint();
                println("  from " + from + "  type=" + ref.getReferenceType() + "  in " + where);
                count++;
            }
            println("  total: " + count);
        }
    }
}
