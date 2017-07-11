/*
 * This material is based upon work supported by the United States Air Force
 * and DARPA under Contract No. FA8750-15-C-0082. Any opinions, findings and
 * conclusions or recommendations expressed in this material are those of
 * the author(s) and do not necessarily reflect the views of the United
 * States Air Force and DARPA.
 *
 *
 * Copyright 2017 GrammaTech, Inc.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 * contributors may be used to endorse or promote products derived from this
 * software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * If you are interested in making contributions, then please contact
 * info@grammatech.com
 */

/* Accrue Bytecode slicing adapter
 * Tested with accrue git hash: 925169e596cfde0685dc4c16e5c99f3c1bc5e3f0
 * See https://github.com/GrammaTech/j8-tests/blob/master/Readme.md#slicing-ir 
 * for a detailed description of the slicing protocol
 */
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
                System.getProperty("java.io.tmpdir") /* output dir */,
                1 /* threads ?*/,
                false /* disable signatures */,
                false /* disableObjectClone */);

        // The following recipie for slicing was taken mostly from AccrueAnalysisMain (in the "pdg" case)

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

        // ProgramDependenceGraph is basically a Set<PDGNode>,Set<PDGEdge> pair.
        // It doesn't provide an interface for querying it. I believe it is intended
        // to be just serialized and used by the Pidgin web interface. We break it out
        // into a PDGNode -> Set<PDGEdge> map so we can more easily traverse it.
        Map<PDGNode, Collection<ProgramDependenceGraph.PDGEdge>> map = new HashMap<>();
        for (ProgramDependenceGraph.PDGEdge e : pdg.allEdges()) {
            Collection<ProgramDependenceGraph.PDGEdge> es = map.get(e.source);
            if (es == null) {
                es = new LinkedList<>();
                map.put(e.source, es);
            }
            es.add(e);
        }

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
                // Convert each node descriptor (class signature + formal no) to a
                // PDGNode
                PDGNode src = desc2node(cg, line.substring(0, p));
                PDGNode dst = desc2node(cg, line.substring(p + 4));
                // check is dst is reachable from src (see below)
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
        // If we have a context sensitive call graph we'll need to handle it
        // here (probblay by returning a Set<Statement>
        if (nodes.size() != 1)
            throw new UnsupportedOperationException("context sensitivity not supported");
        CGNode node = nodes.iterator().next();

        // Unfortunately PDGNodeFactory doesn't have a lookup/find method. Instead
        // we used find or create, and assert that we didn't create it (the description
        // string is ignored when matching existing nodes, so if we ever see *our*
        // description we must have created it.
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
    // by the cost of the PDG computation. Just keep following edges in our
    // PDGNode -> Set<PDGEdge> map. This uses O(n) stack space, but this
    // is fine for our current test cases. We'll probably need to make this
    // non-recursive if larger tests cases are added though.
    public static boolean checkPath(
            Map<PDGNode, Collection<ProgramDependenceGraph.PDGEdge>> g, PDGNode src, PDGNode dest) {
        Collection<ProgramDependenceGraph.PDGEdge> es = g.get(src);
        // If PDGNode isn't present it indicates that it has no outgoing edges
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
