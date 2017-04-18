import java.util.Iterator;

import soot.*;
import soot.jimple.toolkits.callgraph.*;
import soot.options.Options;

public class SootCG {
    public static String toString(SootMethod m)
    {
        return m.getDeclaringClass().getName() + "."
             + m.getName()
             + AbstractJasminClass.jasminDescriptorOf(m.makeRef());
    }
    public static void main(String[] args) {
        StringBuilder sb = new StringBuilder();
        for(int i=0;i<args.length-1;i++)
            sb.append(args[i]).append(":");
        sb.append("../../src/dependencies/rt.jar:../../src/dependencies/jce.jar");
        Options.v().set_soot_classpath(sb.toString());
        Options.v().classes().add(args[args.length-1]);
        Options.v().set_whole_program(true);
        Scene.v().loadNecessaryClasses();
        PackManager.v().runPacks();
        CallGraph cg = Scene.v().getCallGraph();
        for(Iterator<Edge> it = cg.iterator(); it.hasNext(); ) {
            Edge e = it.next();
            System.out.println(toString(e.src()) + " -> " + toString(e.tgt()));
        }
    }
}
