import analysis.AnalysisUtil;
import analysis.dataflow.interprocedural.exceptions.*;
import analysis.dataflow.interprocedural.nonnull.*;
import analysis.dataflow.interprocedural.pdg.*;
import analysis.dataflow.interprocedural.pdg.graph.*;
import analysis.dataflow.interprocedural.pdg.graph.node.*;
import analysis.dataflow.interprocedural.reachability.*;
import analysis.pointer.analyses.*;
import analysis.pointer.engine.*;
import analysis.pointer.graph.*;
import analysis.pointer.registrar.*;
import analysis.pointer.statements.*;
import com.ibm.wala.ipa.callgraph.*;
import com.ibm.wala.ipa.callgraph.impl.BasicCallGraph;
import com.ibm.wala.types.*;
import com.ibm.wala.util.*;
import java.io.*;
import java.util.*;
import util.*;

public class AccrueSLAdapter {
    // args == [jre path, app jar 1, ..., app jar n, entrypoint]
    public static void main(String[] args) throws WalaException, IOException {
        String jre_jars = args[0];

        // Build the class path (we have all the components separated out, but
        // Accrue wants a ':' separated string
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < args.length - 1; i++) sb.append(args[i]).append(File.pathSeparatorChar);
        sb.append(jre_jars).append(File.separatorChar).append("rt.jar");
        sb.append(File.pathSeparatorChar);
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
        BasicCallGraph cg = ptg.getCallGraph();

        ReferenceVariableCache rvCache = registrar.getRvCache();
        ReachabilityInterProceduralDataFlow ra =
                new ReachabilityInterProceduralDataFlow(ptg, rvCache, null);
        ra.runAnalysis();
        ReachabilityResults rr1 = ra.getAnalysisResults();

        NonNullInterProceduralDataFlow nna = new NonNullInterProceduralDataFlow(ptg, rr1, rvCache);
        nna.runAnalysis();
        NonNullResults nnr = nna.getAnalysisResults();

        PreciseExceptionInterproceduralDataFlow pea =
                new PreciseExceptionInterproceduralDataFlow(ptg, nnr, rr1, rvCache);
        pea.runAnalysis();
        PreciseExceptionResults per = pea.getAnalysisResults();

        ra = new ReachabilityInterProceduralDataFlow(ptg, rvCache, per);
        ra.runAnalysis();
        ReachabilityResults rr2 = ra.getAnalysisResults();

        PDGInterproceduralDataFlow pdga =
                new PDGInterproceduralDataFlow(ptg, per, rr2, nnr, rvCache);
        pdga.runAnalysis();
        ProgramDependenceGraph pdg = pdga.getAnalysisResults();

        Map<PDGNode, Collection<ProgramDependenceGraph.PDGEdge>> map = new HashMap<>();
        for (ProgramDependenceGraph.PDGEdge e : pdg.allEdges()) {
            Collection<ProgramDependenceGraph.PDGEdge> es = map.get(e.source);
            if (es == null) {
                es = new LinkedList<>();
                map.put(e.source, es);
            }
            es.add(e);
        }

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
                PDGNode src = desc2node(cg, line.substring(0, p));
                PDGNode dst = desc2node(cg, line.substring(p + 4));
                res = checkPath(map, src, dst);
            } catch (Exception e) {
                // catch-all exception handlers are usually bad, but we intentionally
                // don't want to skip all queries if one fails, for any reason
                res = e;
            }
            System.out.println(line + ": " + res);
        }
        br.close();
    }

    public static PDGNode desc2node(BasicCallGraph cg, String desc) {
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
        CGNode node = nodes.iterator().next(); /* XXX assumes no context sensitivity */

        PDGNode formal =
                PDGNodeFactory.findOrCreateOther(
                        "__NOTFOUND__",
                        PDGNodeType.FORMAL_SUMMARY,
                        node,
                        node.getMethod().getParameterType(formal_no),
                        formal_no);
        if (formal.toString().equals("__NOTFOUND__"))
            throw new IllegalArgumentException("node not found in pdg");
        return formal;
    }

    // This is quite inefficient, but the cost of this is probably dwarfed
    // by the cost of the PDG computation
    public static boolean checkPath(
            Map<PDGNode, Collection<ProgramDependenceGraph.PDGEdge>> g, PDGNode src, PDGNode dest) {
        Collection<ProgramDependenceGraph.PDGEdge> es = g.get(src);
        if (es == null) return false;
        for (ProgramDependenceGraph.PDGEdge e : es) {
            PDGNode tgt = e.target;
            switch (e.type) {
                case EXP:
                case COPY:
                case MERGE:
                    if (tgt == dest || checkPath(g, tgt, dest)) return true;
                    break;
            }
        }
        return false;
    }
}