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
