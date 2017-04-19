import analysis.AnalysisUtil;
import analysis.pointer.analyses.*;
import analysis.pointer.engine.*;
import analysis.pointer.graph.*;
import analysis.pointer.registrar.*;
import analysis.pointer.statements.*;
import com.ibm.wala.ipa.callgraph.CGNode;
import com.ibm.wala.util.WalaException;
import com.ibm.wala.util.graph.Graph;
import java.io.File;
import java.io.IOException;
import java.util.Iterator;

public class AccrueCG {
    // args == [jre path, app jar 1, ..., app jar n, entrypoint]
    public static void main(String[] args) throws WalaException, IOException {
        String jre_jars = args[0];

        // Build the class path (we have all the components separated out, but
        // Accrue wants a ':' separated string
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < args.length - 1; i++) sb.append(args[i]).append(File.separatorChar);
        sb.append(jre_jars).append(File.separatorChar).append("rt.jar");
        sb.append(File.separatorChar);
        sb.append(jre_jars).append(File.separatorChar).append("jce.jar");

        AnalysisUtil.init(
                sb.toString() /* classpath */,
                args[args.length - 1] /* entry point */,
                "." /* output dir */,
                1 /* threads ?*/,
                false /* disable signatures */,
                false /* disableObjectClone */);

        PointsToAnalysis analysis = new PointsToAnalysisSingleThreaded(new TypeSensitive(2, 1));

        StatementRegistrationPass pass =
                new StatementRegistrationPass(
                        new StatementFactory(),
                        // These options are based on an email from Steve Chong on 2017-03-30
                        // (he uses this for DaCap)
                        false /* singleGenEx */,
                        true /* singleThrowable */,
                        true /* singlePrimArray */,
                        false /* singleString */,
                        true /* singleWrappers */,
                        true /* singleSwing */,
                        true /* useDefaultNativeSignatures */);

        pass.run();
        StatementRegistrar registrar = pass.getRegistrar();
        PointsToGraph ptg = analysis.solve(registrar);

        Graph<CGNode> g = ptg.getCallGraph();
        for (Iterator<CGNode> it = g.iterator(); it.hasNext(); ) {
            CGNode n = it.next();
            for (Iterator<CGNode> it2 = g.getSuccNodes(n); it2.hasNext(); ) {
                CGNode s = it2.next();
                System.out.println(toString(n) + " -> " + toString(s));
            }
        }
    }

    public static String toString(CGNode n) {
        return n.getMethod().getSignature();
    }
}
