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

/* JOANA call graph adapter
 * Tested with JOANA git hash: b4bfc6092b427411b1bdf232dd39bce0c6fdcb41
 * See https://github.com/GrammaTech/j8-tests/blob/master/Readme.md#callgraph-ir 
 * for a detailed description of the call graph ir
 */
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
            // (entry point is a method, not a class, so we tack on main)
            args[args.length - 1] + ".main([Ljava/lang/String;)V",
            sb.toString(),
            // FieldPropagation.FLAT is what MainGUI::RunSDG does by default...
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
