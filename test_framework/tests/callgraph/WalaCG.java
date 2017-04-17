/*******************************************************************************
 * Copyright (c) 2002 - 2006 IBM Corporation.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.Iterator;
import java.util.Properties;

import com.ibm.wala.core.tests.callGraph.CallGraphTestUtil;
import com.ibm.wala.examples.properties.WalaExamplesProperties;
import com.ibm.wala.ipa.callgraph.AnalysisCache;
import com.ibm.wala.ipa.callgraph.AnalysisOptions;
import com.ibm.wala.ipa.callgraph.AnalysisScope;
import com.ibm.wala.ipa.callgraph.CGNode;
import com.ibm.wala.ipa.callgraph.CallGraph;
import com.ibm.wala.ipa.callgraph.CallGraphStats;
import com.ibm.wala.ipa.callgraph.Entrypoint;
import com.ibm.wala.ipa.callgraph.impl.Util;
import com.ibm.wala.ipa.callgraph.propagation.LocalPointerKey;
import com.ibm.wala.ipa.cha.ClassHierarchy;
import com.ibm.wala.properties.WalaProperties;
import com.ibm.wala.types.ClassLoaderReference;
import com.ibm.wala.util.CancelException;
import com.ibm.wala.util.WalaException;
import com.ibm.wala.util.Predicate;
import com.ibm.wala.util.collections.HashSetFactory;
import com.ibm.wala.util.config.AnalysisScopeReader;
import com.ibm.wala.util.debug.Assertions;
import com.ibm.wala.util.graph.Graph;
import com.ibm.wala.util.io.CommandLine;
import com.ibm.wala.util.io.FileProvider;
import com.ibm.wala.util.io.FileUtil;
import com.ibm.wala.viz.DotUtil;
import com.ibm.wala.viz.PDFViewUtil;

import com.ibm.wala.examples.drivers.PDFTypeHierarchy;

public class WalaCG {
  public static String toString(CGNode n) {
    return n.getMethod().getSignature();
  }
  public static void main(String[] args) throws WalaException, IllegalArgumentException, CancelException, IOException {
    Graph<CGNode> g = buildPrunedCallGraph(args[0], new FileProvider().getFile( CallGraphTestUtil.REGRESSION_EXCLUSIONS));

    for (Iterator<CGNode> it = g.iterator(); it.hasNext();) {
      CGNode n = it.next();
      for (Iterator<CGNode> it2 = g.getSuccNodes(n); it2.hasNext();) {
        CGNode s = it2.next();
        System.out.println(toString(n) + " -> " + toString(s));
      }
    }
    
    
  }

  public static Graph<CGNode> buildPrunedCallGraph(String appJar, File exclusionFile) throws WalaException,
      IllegalArgumentException, CancelException, IOException {
    AnalysisScope scope = AnalysisScopeReader.makeJavaBinaryAnalysisScope(appJar, exclusionFile != null ? exclusionFile : new File(
        CallGraphTestUtil.REGRESSION_EXCLUSIONS));

    ClassHierarchy cha = ClassHierarchy.make(scope);

    Iterable<Entrypoint> entrypoints = com.ibm.wala.ipa.callgraph.impl.Util.makeMainEntrypoints(scope, cha);
    AnalysisOptions options = new AnalysisOptions(scope, entrypoints);

    com.ibm.wala.ipa.callgraph.CallGraphBuilder builder = Util.makeZeroCFABuilder(options, new AnalysisCache(), cha, scope);
    CallGraph cg = builder.makeCallGraph(options, null);

    //System.err.println(CallGraphStats.getStats(cg));

    Graph<CGNode> g = pruneForAppLoader(cg);

    return g;
  }

  public static Graph<CGNode> pruneForAppLoader(CallGraph g) throws WalaException {
    return PDFTypeHierarchy.pruneGraph(g, new ApplicationLoaderFilter());
  }

  private static class ApplicationLoaderFilter extends Predicate<CGNode> {

    @Override public boolean test(CGNode o) {
      if (o instanceof CGNode) {
        CGNode n = (CGNode) o;
        return n.getMethod().getDeclaringClass().getClassLoader().getReference().equals(ClassLoaderReference.Application);
      } else if (o instanceof LocalPointerKey) {
        LocalPointerKey l = (LocalPointerKey) o;
        return test(l.getNode());
      } else {
        return false;
      }
    }
  }
}
