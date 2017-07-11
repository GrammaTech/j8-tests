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

/* Soot call graph adapter
 * Tested with Soot 3.0.0
 * See https://github.com/GrammaTech/j8-tests/blob/master/Readme.md#callgraph-ir 
 * for a detailed description of the call graph ir
 */
import java.io.File;
import java.util.Iterator;
import soot.*;
import soot.jimple.toolkits.callgraph.*;
import soot.options.Options;

public class SootCGAdapter {
    // args == [jre path, app jar 1, ..., app jar n, entrypoint]
    public static void main(String[] args) {
        String jre_jars = args[0];

        // Build the class path (we have all the components separated out, but
        // soot wants a ':' separated string
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < args.length - 1; i++)
            sb.append(args[i]).append(File.pathSeparatorChar);
        sb.append(jre_jars).append(File.separatorChar).append("rt.jar");
        sb.append(File.pathSeparatorChar);
        sb.append(jre_jars).append(File.separatorChar).append("jce.jar");
        Options.v().set_soot_classpath(sb.toString());

        // Main class is the final arguments
        Options.v().classes().add(args[args.length - 1]);

        Options.v().set_whole_program(true);
        Scene.v().loadNecessaryClasses();
        PackManager.v().runPacks();

        CallGraph cg = Scene.v().getCallGraph();
        for (Iterator<Edge> it = cg.iterator(); it.hasNext(); ) {
            Edge e = it.next();
            System.out.println(toString(e.src()) + " -> " + toString(e.tgt()));
        }
    }

    public static String toString(SootMethod m) {
        return m.getDeclaringClass().getName()
                + "."
                + m.getName()
                + AbstractJasminClass.jasminDescriptorOf(m.makeRef());
    }
}
