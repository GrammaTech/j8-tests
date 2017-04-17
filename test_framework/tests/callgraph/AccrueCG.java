import java.util.Iterator;

import analysis.AnalysisUtil;
import analysis.pointer.analyses.*;
import analysis.pointer.engine.*;
import analysis.pointer.graph.*;
import analysis.pointer.registrar.*;
import analysis.pointer.statements.*;
import util.OrderedPair;

import com.ibm.wala.ipa.callgraph.CGNode;
import com.ibm.wala.util.graph.Graph;

public class AccrueCG {
    public static void main(String[] args) throws Exception /* XXX? */
    {
        StringBuilder sb = new StringBuilder();
        for(int i=0;i<args.length-1;i++)
            sb.append(args[i]).append(":");
        sb.append("/usr/local/java/jre/lib/rt.jar:/usr/local/java/jre/lib/jce.jar");
        AnalysisUtil.init(
            sb.toString() /* classpath */,
            args[args.length-1] /* entry point */,
            "." /* output dir */,
            1 /* threads ?*/,
            false /* disable signatures */,
            false /* disableObjectClone */);
        
        PointsToAnalysis analysis = new PointsToAnalysisSingleThreaded(
            new TypeSensitive(2,1)
        );
                
        StatementRegistrationPass pass = new StatementRegistrationPass(
            new StatementFactory(),
            // These options are based on an email from Steve Chong on 2017-03-30
            // (he uses this for DaCap)
            false /* singleGenEx */,
            true /* singleThrowable */,
            true /* singlePrimArray */,
            false /* singleString */,
            true /* singleWrappers */,
            true /* singleSwing */,
            true /* useDefaultNativeSignatures */
        );
        
        pass.run();
        StatementRegistrar registrar = pass.getRegistrar();
        PointsToGraph ptg = analysis.solve(registrar);
        
        Graph<CGNode> g = ptg.getCallGraph();
        for (Iterator<CGNode> it = g.iterator(); it.hasNext();) {
            CGNode n = it.next();
            for (Iterator<CGNode> it2 = g.getSuccNodes(n); it2.hasNext();) {
                CGNode s = it2.next();
                System.out.println(toString(n) + " -> " + toString(s));
            }
        }
    }

    public static String toString(CGNode n) {
        return n.getMethod().getSignature();
    }
}
