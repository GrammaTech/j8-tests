import edu.kit.joana.wala.core.PDG;
import edu.kit.joana.wala.core.Main;
import edu.kit.joana.wala.core.NullProgressMonitor;
import edu.kit.joana.wala.core.SDGBuilder;
import edu.kit.joana.ifc.sdg.graph.SDG;

import com.ibm.wala.util.CancelException;
import com.ibm.wala.util.WalaException;
import com.ibm.wala.util.collections.Pair;
import com.ibm.wala.util.graph.Graph;
import com.ibm.wala.util.graph.GraphIntegrity.UnsoundGraphException;

import java.io.File;
import java.io.IOException;
import java.util.Iterator;

public class JoanaCGAdapter {
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
        Pair<SDG, SDGBuilder> p = Main.computeAndKeepBuilder(
            System.err, 
            cfg, 
            false, 
            NullProgressMonitor.INSTANCE);
        SDGBuilder b = p.snd;
        Graph<PDG> cg = b.createCallGraph();

        for (Iterator<PDG> it = cg.iterator(); it.hasNext(); ) {
            PDG n = it.next();
            for (Iterator<PDG> it2 = cg.getSuccNodes(n); it2.hasNext(); ) {
                PDG s = it2.next();
                System.out.println(toString(n) + " -> " + toString(s));
            }
        }
    }

    public static String toString(PDG n) {
        return n.cgNode.getMethod().getSignature();
    }
}
