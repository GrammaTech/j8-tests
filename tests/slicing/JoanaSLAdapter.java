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

/* JOANA slicing adapter
 * Tested with JOANA git hash: b4bfc6092b427411b1bdf232dd39bce0c6fdcb41
 * See https://github.com/GrammaTech/j8-tests/blob/master/Readme.md#slicing-ir
 * for a detailed description of the slicing protocol
 */
import com.ibm.wala.ipa.callgraph.CGNode;
import com.ibm.wala.ipa.callgraph.CallGraph;
import com.ibm.wala.types.*;
import com.ibm.wala.util.CancelException;
import com.ibm.wala.util.WalaException;
import com.ibm.wala.util.collections.Pair;
import com.ibm.wala.util.graph.GraphIntegrity.UnsoundGraphException;
import edu.kit.joana.ifc.sdg.graph.*;
import edu.kit.joana.ifc.sdg.graph.slicer.*;
import edu.kit.joana.wala.core.Main;
import edu.kit.joana.wala.core.NullProgressMonitor;
import edu.kit.joana.wala.core.PDG;
import edu.kit.joana.wala.core.SDGBuilder;
import java.io.*;
import java.util.*;

public class JoanaSLAdapter {
    // args == [jre path, app jar 1, ..., app jar n, entrypoint]
    public static void main(String[] args)
            throws WalaException, IllegalArgumentException, CancelException, UnsoundGraphException,
                    IOException {

        // Build the class path
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < args.length - 1; i++) {
            if (i != 1) sb.append(File.pathSeparatorChar);
            sb.append(args[i]);
        }

        Main.Config cfg =
                new Main.Config(
                        "Test Adapter",
                        // (entry point is a method, not a class, so we tack on main)
                        args[args.length - 1] + ".main([Ljava/lang/String;)V",
                        sb.toString(),
                        SDGBuilder.PointsToPrecision.TYPE_BASED, // 0-CFA
                        // FieldPropagation.FLAT is what MainGUI::RunSDG does by default...
                        SDGBuilder.FieldPropagation.FLAT);
        Pair<SDG, SDGBuilder> cons =
                Main.computeAndKeepBuilder(System.err, cfg, false, NullProgressMonitor.INSTANCE);

        // We're using a vanilla context insensitive backwards slicer
        // (TODO: Check other slicing algorithms?)
        Slicer slicer = new ContextInsensitiveBackward(cons.fst);

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
                // Convert each node descriptor (class signature + formal no) to an
                // SDGNode
                SDGNode src = desc2node(cons, line.substring(0, p));
                SDGNode dst = desc2node(cons, line.substring(p + 4));
                // Slice back from dst, and check if src is in the slice
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
    }

    public static SDGNode desc2node(Pair<SDG, SDGBuilder> cons, String desc) {
        CallGraph cg = cons.snd.getWalaCallGraph();
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
        // PointsToPrecision.TYPE_BASED is context insensitive, but if we
        // have a context sensitive call graph we'll need to handle it here
        // (probblay by returning a Set<SDGNode>
        if(nodes.isEmpty())
            throw new Error(m + " not found in call graph");
        if (nodes.size() != 1)
            throw new UnsupportedOperationException("context sensitivity not supported");
        CGNode node = nodes.iterator().next(); /* XXX context sensitivity? */

        // Find the PDG for this method (cons.snd == SDGBuilder)
        PDG pdg = cons.snd.getPDGforMethod(node);

        // Finally, get the PDGNode for the forma, then lookup the
        // corresponding SDGNode (con.fst == SDG)
        return cons.fst.getNode(pdg.params[formal_no].getId());
    }
}
