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

/* WALA call graph adapter
 * Tested with WALA 1.4.1
 * See https://github.com/GrammaTech/j8-tests/blob/master/Readme.md#callgraph-ir 
 * for a detailed description of the call graph ir
 */
import com.ibm.wala.core.tests.callGraph.CallGraphTestUtil;
import com.ibm.wala.ipa.callgraph.AnalysisCache;
import com.ibm.wala.ipa.callgraph.AnalysisCacheImpl;
import com.ibm.wala.ipa.callgraph.AnalysisOptions;
import com.ibm.wala.ipa.callgraph.AnalysisScope;
import com.ibm.wala.ipa.callgraph.CGNode;
import com.ibm.wala.ipa.callgraph.CallGraph;
import com.ibm.wala.ipa.callgraph.CallGraphBuilder;
import com.ibm.wala.ipa.callgraph.Entrypoint;
import com.ibm.wala.ipa.callgraph.impl.Util;
import com.ibm.wala.ipa.cha.ClassHierarchy;
import com.ibm.wala.ipa.cha.ClassHierarchyFactory;
import com.ibm.wala.types.ClassLoaderReference;
import com.ibm.wala.types.*;
import com.ibm.wala.util.CancelException;
import com.ibm.wala.util.WalaException;
import com.ibm.wala.util.io.FileProvider;
import java.io.File;
import java.io.IOException;
import java.util.Iterator;
import java.util.jar.JarFile;

public class WalaCGAdapter {
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

        for (Iterator<CGNode> it = cg.iterator(); it.hasNext(); ) {
            CGNode n = it.next();
            for (Iterator<CGNode> it2 = cg.getSuccNodes(n); it2.hasNext(); ) {
                CGNode s = it2.next();
                System.out.println(toString(n) + " -> " + toString(s));
            }
        }
    }

    public static String toString(CGNode n) {
        return n.getMethod().getSignature();
    }
}
