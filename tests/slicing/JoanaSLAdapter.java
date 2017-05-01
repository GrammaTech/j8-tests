import edu.kit.joana.wala.core.PDG;
import edu.kit.joana.wala.core.PDGNode;
import edu.kit.joana.wala.core.Main;
import edu.kit.joana.wala.core.NullProgressMonitor;
import edu.kit.joana.wala.core.SDGBuilder;
import edu.kit.joana.ifc.sdg.graph.*;
import edu.kit.joana.ifc.sdg.graph.slicer.*;

import com.ibm.wala.ipa.callgraph.CallGraph;
import com.ibm.wala.ipa.callgraph.CGNode;
import com.ibm.wala.util.CancelException;
import com.ibm.wala.util.WalaException;
import com.ibm.wala.util.collections.Pair;
import com.ibm.wala.util.graph.Graph;
import com.ibm.wala.util.graph.GraphIntegrity.UnsoundGraphException;
import com.ibm.wala.types.*;

import java.io.*;
import java.util.*;

public class JoanaSLAdapter {
    // args == [jre path, app jar 1, ..., app jar n, entrypoint]
    public static void main(String[] args)
            throws WalaException, IllegalArgumentException, CancelException, UnsoundGraphException, IOException {
            
        // Build the class path
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < args.length - 1; i++) {
            if(i != 1)
                sb.append(File.pathSeparatorChar);
            sb.append(args[i]);
        }
        
        Main.Config cfg = new Main.Config(
            "Test Adapter",
            args[args.length - 1] + ".main([Ljava/lang/String;)V",
            sb.toString(),
            SDGBuilder.FieldPropagation.FLAT);
        Pair<SDG, SDGBuilder> cons = Main.computeAndKeepBuilder(
            System.err, 
            cfg, 
            false, 
            NullProgressMonitor.INSTANCE);
            
        
        Slicer slicer = new ContextInsensitiveBackward(cons.fst);
        
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line;
        while ((line = br.readLine()) != null) {
            int p = line.indexOf(" -> ");
            Object res;
            if (p == -1) {
                System.err.println("bad query: " + line);
                continue;
            }
            try {
                SDGNode src = desc2node(cons, line.substring(0, p));
                SDGNode dst = desc2node(cons, line.substring(p + 4));
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

        /*Graph<PDG> cg = b.createCallGraph();

        for (Iterator<PDG> it = cg.iterator(); it.hasNext(); ) {
            PDG n = it.next();
            for (Iterator<PDG> it2 = cg.getSuccNodes(n); it2.hasNext(); ) {
                PDG s = it2.next();
                System.out.println(toString(n) + " -> " + toString(s));
            }
        }*/
    }

    public static SDGNode desc2node(Pair<SDG, SDGBuilder> cons, String desc) {
        CallGraph cg = cons.snd.getWalaCallGraph();
        int p, q;

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

        TypeReference t =
                TypeReference.findOrCreate(
                        ClassLoaderReference.Application, "L" + klass.replace('.', '/'));
        MethodReference m = MethodReference.findOrCreate(t, method, sig);
        Set<CGNode> nodes = cg.getNodes(m);
        CGNode node = nodes.iterator().next(); /* XXX context sensitivity? */
        PDG pdg = cons.snd.getPDGforMethod(node);

        return cons.fst.getNode(pdg.params[formal_no].getId());
    }
}
