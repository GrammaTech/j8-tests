/* JOANA slicing adapter
 * Tested with JOANA git hash: b4bfc6092b427411b1bdf232dd39bce0c6fdcb41
 * See https://github.com/GrammaTech/j8-tests/blob/master/Readme.md#slicing-ir
 * for a detailed description of the slicing protocol
 */
import com.ibm.wala.ipa.callgraph.CGNode;
import com.ibm.wala.ipa.callgraph.CallGraph;
import com.ibm.wala.types.*;
import com.ibm.wala.util.CancelException;
import com.ibm.wala.util.WalaException;
import com.ibm.wala.util.collections.Pair;
import com.ibm.wala.util.graph.GraphIntegrity.UnsoundGraphException;
import edu.kit.joana.ifc.sdg.graph.*;
import edu.kit.joana.ifc.sdg.graph.slicer.*;
import edu.kit.joana.wala.core.Main;
import edu.kit.joana.wala.core.NullProgressMonitor;
import edu.kit.joana.wala.core.PDG;
import edu.kit.joana.wala.core.SDGBuilder;
import java.io.*;
import java.util.*;

public class JoanaSLAdapter {
    // args == [jre path, app jar 1, ..., app jar n, entrypoint]
    public static void main(String[] args)
            throws WalaException, IllegalArgumentException, CancelException, UnsoundGraphException,
                    IOException {

        // Build the class path
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < args.length - 1; i++) {
            if (i != 1) sb.append(File.pathSeparatorChar);
            sb.append(args[i]);
        }

        Main.Config cfg =
                new Main.Config(
                        "Test Adapter",
                        // (entry point is a method, not a class, so we tack on main)
                        args[args.length - 1] + ".main([Ljava/lang/String;)V",
                        sb.toString(),
                        SDGBuilder.PointsToPrecision.TYPE_BASED, // 0-CFA
                        // FieldPropagation.FLAT is what MainGUI::RunSDG does by default...
                        SDGBuilder.FieldPropagation.FLAT);
        Pair<SDG, SDGBuilder> cons =
                Main.computeAndKeepBuilder(System.err, cfg, false, NullProgressMonitor.INSTANCE);

        // We're using a vanilla context insensitive backwards slicer
        // (TODO: Check other slicing algorithms?)
        Slicer slicer = new ContextInsensitiveBackward(cons.fst);

        // Read though each query (on standard input)
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line;
        while ((line = br.readLine()) != null) {
            // Split on " -> " (which separates the source and the target)
            int p = line.indexOf(" -> ");
            Object res;
            if (p == -1) {
                System.err.println("bad query: " + line);
                continue;
            }
            try {
                // Convert each node descriptor (class signature + formal no) to an
                // SDGNode
                SDGNode src = desc2node(cons, line.substring(0, p));
                SDGNode dst = desc2node(cons, line.substring(p + 4));
                // Slice back from dst, and check if src is in the slice
                Collection<SDGNode> slice = slicer.slice(dst);
                res = slice.contains(src);
            } catch (Exception e) {
                // catch-all exception handlers are usually bad, but we intentionally
                // don't want to skip all queries if one fails, for any reason
                res = e;
            }
            System.out.println(line + ": " + res);
        }
        br.close();
    }

    public static SDGNode desc2node(Pair<SDG, SDGBuilder> cons, String desc) {
        CallGraph cg = cons.snd.getWalaCallGraph();
        int p, q;

        // Break apart the descriptor string (class(method_sig):formal_no)
        p = desc.indexOf('(');
        if (p == -1) throw new IllegalArgumentException();
        q = desc.indexOf(':');
        if (p == -1) throw new IllegalArgumentException();
        String sig = desc.substring(p, q);
        int formal_no = Integer.parseInt(desc.substring(q + 1));
        q = desc.lastIndexOf('.', p - 1);
        if (q == -1) throw new IllegalArgumentException();
        String klass = desc.substring(0, q);
        String method = desc.substring(q + 1, p);

        // Lookup the WALA CGNode for the method
        TypeReference t =
                TypeReference.findOrCreate(
                        ClassLoaderReference.Application, "L" + klass.replace('.', '/'));
        MethodReference m = MethodReference.findOrCreate(t, method, sig);
        Set<CGNode> nodes = cg.getNodes(m);
        // PointsToPrecision.TYPE_BASED is context insensitive, but if we
        // have a context sensitive call graph we'll need to handle it here
        // (probblay by returning a Set<SDGNode>
        if(nodes.isEmpty())
            throw new Error(m + " not found in call graph");
        if (nodes.size() != 1)
            throw new UnsupportedOperationException("context sensitivity not supported");
        CGNode node = nodes.iterator().next(); /* XXX context sensitivity? */

        // Find the PDG for this method (cons.snd == SDGBuilder)
        PDG pdg = cons.snd.getPDGforMethod(node);

        // Finally, get the PDGNode for the forma, then lookup the
        // corresponding SDGNode (con.fst == SDG)
        return cons.fst.getNode(pdg.params[formal_no].getId());
    }
}
