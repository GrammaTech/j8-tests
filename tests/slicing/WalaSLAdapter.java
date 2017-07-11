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

/* WALA slicing adapter
 * Tested with WALA 1.4.1
 * See https://github.com/GrammaTech/j8-tests/blob/master/Readme.md#slicing-ir
 * for a detailed description of the slicing protocol
 */
import com.ibm.wala.core.tests.callGraph.CallGraphTestUtil;
import com.ibm.wala.ipa.callgraph.AnalysisCacheImpl;
import com.ibm.wala.ipa.callgraph.AnalysisOptions;
import com.ibm.wala.ipa.callgraph.AnalysisScope;
import com.ibm.wala.ipa.callgraph.CGNode;
import com.ibm.wala.ipa.callgraph.CallGraph;
import com.ibm.wala.ipa.callgraph.CallGraphBuilder;
import com.ibm.wala.ipa.callgraph.Entrypoint;
import com.ibm.wala.ipa.callgraph.impl.Util;
import com.ibm.wala.ipa.callgraph.propagation.PointerAnalysis;
import com.ibm.wala.ipa.cha.ClassHierarchy;
import com.ibm.wala.ipa.cha.ClassHierarchyFactory;
import com.ibm.wala.ipa.slicer.*;
import com.ibm.wala.types.*;
import com.ibm.wala.util.CancelException;
import com.ibm.wala.util.WalaException;
import com.ibm.wala.util.io.FileProvider;
import java.io.*;
import java.io.File;
import java.io.IOException;
import java.util.*;
import java.util.jar.JarFile;

public class WalaSLAdapter {
    // args == [jre path, app jar 1, ..., app jar n, entrypoint]
    public static void main(String[] args)
            throws WalaException, IllegalArgumentException, CancelException, IOException {

        String jre_jars = args[0];

        // This mostly reimplements the meat of
        // AnalysisScopeReader.makeJavaBinaryAnalysisScope
        // We roll this ourselves so we can ensure *our* rt.jar is used, regardless
        // of the jvm being used or wala.properties
        AnalysisScope scope = AnalysisScope.createJavaAnalysisScope();
        ClassLoaderReference primordial = scope.getPrimordialLoader();
        scope.addToScope(primordial, new JarFile(new File(jre_jars, "rt.jar")));
        scope.addToScope(primordial, new FileProvider().getJarFileModule("primordial.jar.model"));
        ClassLoaderReference application = scope.getApplicationLoader();
        for (int i = 1; i < args.length - 1; i++)
            scope.addToScope(application, new JarFile(args[i], false));

        ClassHierarchy cha = ClassHierarchyFactory.make(scope);

        Iterable<Entrypoint> entrypoints = Util.makeMainEntrypoints(scope, cha);

        AnalysisOptions options = new AnalysisOptions(scope, entrypoints);

        CallGraphBuilder builder =
                Util.makeZeroCFABuilder(options, new AnalysisCacheImpl(), cha, scope);

        CallGraph cg = builder.makeCallGraph(options, null);

        PointerAnalysis pa = builder.getPointerAnalysis();

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
                // Statement
                Statement src = desc2stmt(cg, line.substring(0, p));
                Statement dst = desc2stmt(cg, line.substring(p + 4));
                // Slice back from dst, and check if src is in the slice
                Collection<Statement> slice =
                        Slicer.computeBackwardSlice(
                                dst,
                                cg,
                                pa,
                                null /* instance key */,
                                Slicer.DataDependenceOptions.FULL,
                                Slicer.ControlDependenceOptions.NONE);
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

    public static Statement desc2stmt(CallGraph cg, String desc) {
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
        // This should never happen with the ZeroCFABuilder, but if we ever do
        // have a context sensitive call graph we'll need to handle it here
        // (probblay by returning a Set<Statement>
        if(nodes.isEmpty())
            throw new Error(m + " not found in call graph");
        if (nodes.size() != 1)
            throw new UnsupportedOperationException("context sensitivity not supported");
        CGNode node = nodes.iterator().next(); /* XXX context sensitivity? */

        // Create a new statement for the formal (statement equality is not
        // based on identity), NB: formals are one based
        return new ParamCallee(node, formal_no + 1);
    }
}
