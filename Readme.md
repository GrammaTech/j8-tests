## Table of Contents  
[Overview and Terminology](#overview)  
[Architecture](#architecture)  
[Supported Tools and Provided Adapters](#provided-adapters)   
[Provided Applications](#provided-applications)    
[Provided Tests](#provided-tests)   
[Installing and Running our Framework](#setup)  
[Extending our Test Suite](#extending)  

<a name="overview"/> 

## Overview and Terminology

This system provides a test suite to assess Java 8 support in a number of popular bytecode analysis tools. The suite comes with existing tests but is also extensible as described in [this section](#extending).

We first give a high-level overview of our system and define some relevant terminology. A **tool** is a bytecode analysis tool; some example tools are [Soot](https://sable.github.io/soot/) and [WALA](http://wala.sourceforge.net/wiki/index.php/Main_Page). Our test suite does not include tools; we expect that the user has tools available on their system and wishes to run our test suite on those tools. An **application** is a jar file; the tools will analyze the bytecode contained in the applications. 

Every tool-application pair can be tested for various kinds of functionality. Therefore, we have a notion of **test families**. A test family is a grouping of tests which test related functionality. Some examples of test families are tests for call graph construction and tests for slicing.

Every test family is associated with an **IR** or intermediate representation. The idea is that every tool, when run on an application, should provide output in a standardized format appropriate to the test family. For example, for the call graph construction test family, our IR is a serialization of the call graph. Every tool requires an **adapter** for every IR; the adapter is a piece of code that runs the tool and ensures its output matches the standardized format required by the IR.

Once a tool has been run on an application and we have obtained the IR (such as a call graph serialization), we run multiple **tests** on this IR. Every test is associated with a **test evaluator** that compares the IR against a known **ground truth**. For example, a test evaluator might check if a node corresponding to method `foo()` is present in the call graph. If the test evaluator determines that the IR matches the ground truth, the appropriate test passes, otherwise it fails.

<a name="architecture"/>

## Architecture

Our testing framework is based on  [pytest](https://docs.pytest.org/en/latest/). Following the terminology from [the overview section](#overview), a test involves running an **adapter** for a **tool** on an **application**. This produces an **IR** which is fed into a **test evaluator** that compares it to a **ground truth**.

Our framework structure and architecture is illustrated by the sample directory structure below (contents of the `src` and `tests` directories are truncated for ease of presentation)
```bash
$ tree
|--- conftest.py
|--- pytest.ini
|--- setup.py
|--- src
|    |--- apps
|    |    |--- church
|    |    |--- eclipse
|    |--- dependencies
|    |    |--- jce.jar
|    |    |--- rt.jar
|    |--- tools
|--- tests
    |--- utils.py
    |--- conftest.py
    |--- callgraph
         |--- call_test.py
```

The files `pytest.ini`, `conftest.py` and `setup.py` provide top-level setup and configuration information. More information is available as comments in the files themselves.

The `src/apps` directory contains the applications and ground truth for each application. Our framework will run tests on all the applications found in this directory.

The `src/dependencies` subdirectory contains versions of the java libraries (`rt.jar`) used to generate the ground truth. If the tools and adapters are run on different versions of `rt.jar`, different results may be produced, resulting in spurious test failures. This directory is also the right place to add any dependencies required by the adapters.

The `tests` directory contains all material relevant to running individual tests. The high level workflow is that the user passes in a number of **tools** on the command line. For every tool, the user also passes in a **tool path** where the tool can be found (see examples [in this section](#setup)). At this point, the framework uses [fixture parametrization](https://docs.pytest.org/en/latest/parametrize.html) to pair up every tool with every **application**. The pairing up is accomplished in file `tests/conftest.py`.

For every **tool**/**application** pair, the system will run every **test family**. Every test family is associated with a subdirectory under `tests`, for example `tests/callgraph`. This subdirectory contains **adapters** and **test evaluators** for the test family.

A typical test evaluator starts by building an appropriate adapter. Building the adapter requires knowing the correct classpath for the tool itself, since the adapter depends on the tool. The function `generate_classpath` in module [`tests/utils.py`](https://github.com/GrammaTech/j8-tests/blob/master/tests/utils.py) converts user-provided information about the tool name and installation location to a classpath which is required for adapter building. Once the adapter is built, the test evaluator generates the IR for the application and compares it to the ground truth.

<a name="provided-adapters"/> 

## Supported Tools and Provided Adapters

### [WALA](http://wala.sourceforge.net)

WALA is a static analysis infrastructure for Java. In additional to being a
standalone library, it is an important component of many other Java static
analysis tools. We include adapters to test WALA's call graph and slicing
capabilities. WALA 1.4.1 is known to be compatable with the test
infrastructure (TODO last minute test again the latest release?).

### [Soot](https://sable.github.io/soot/)

Soot is a Java optimization, rewriting, and analysis framework. We include
adapters to test Soot's call graph capabilities. Vanilla Soot doesn't offer
slicing capabilities, so no slicing adapter is included, however, in the
future we plan on including slicing adapter to test
[soot-infoflow](https://blogs.uni-paderborn.de/sse/tools/flowdroid/). Soot
3.0.0 is known to be compatable with the test infrastucture (although as of
this writing some yet be merged fixes are required to handle some Java8
constructs).

### [Accrue](http://people.seas.harvard.edu/~chong/accrue.html) (Pidgin)

The Accrue Interprocedural Java Analysis Framework is a Java analysis
framework. It is the foundation of the Pidgin program analysis tool. (Pidgin
provide a way to query and test properties of the PDGs generated by Accrue).
We include adapters to test Accrue's call graph and slicing capabilities.
(TODO version)

### [JOANA](http://pp.ipd.kit.edu/projects/joana/)

JOANA is an information flow analysis infrastructure for Java. We include
adapters to test JOANA's call graph and slicing capabilities. JOANA doesn't
appear to have regular releases, so the adapters were developed against the
latest version of their git repo.
<tt>b4bfc6092b427411b1bdf232dd39bce0c6fdcb41</tt> from
https://github.com/joana-team/joana is known to be compatable with the
test infrastructure.

<a name="provided-applications"/> 

## Provided Applications


### Church

* 'Church' is a tiny program which implements [Church
   numerals](https://en.wikipedia.org/wiki/Church_encoding) in Java using lambdas.
   It was initially written as a lambda torture test, since it makes
   extensive use of lambdas with different forms of variable capture.
* It is only about one hundred lines of code and should be relatively fast to
  analyze with most tools.
* The source code (<tt>Church.java</tt>) lives alongsie the <tt>.jar</tt> in apps/church.
* The Church class (no package) has a main method which demonstrates the various operations. This is a suitable entry point for analysis and should provide good coverage of all features.

### Ant

* [Apache Ant](http://ant.apache.org/) is a build system for Java projects.
* It is about 200K lines of code and about 2MB of compiled class files.
* The source code is available at  https://git-wip-us.apache.org/repos/asf/ant.git. The provided 
  jars were build with <tt>193f24672b1d3f9ce11bd395b59e3ed93b5ecec6</tt> (shortly after 1.10.0).
* The latest (1.10) version of Ant requires Java 8; the code uses lambda expressions 
  and method references.
* <tt>org.apache.tools.ant.Main</tt> has a main method and is the primary driver for the build
  system. It is suitable as an entrypoint for analysis.

### Cassandra

* [Apache Cassandra](http://cassandra.apache.org/) is a database server.
* It is about 300K lines of code and about 5MB of compiled class files.
* The source code is available at  https://git-wip-us.apache.org/repos/asf/cassandra.git.
  The provided jars were built with <tt>3d90bb0cc74ca52fc6a9947a746695630ca7fc2a</tt>
  (3.10 development branch).
* Cassandra use lambda expressions and method references extensively.
* <tt>org.apache.cassandra.service.CassandraDaemon</tt> has a main method and is the
  primary driver for the database daemon. It is suitable as an entrypoint for analysis.

### Eclipse (subset)
* [Eclipse](https://eclipse.org) is a Java development environment and IDE.
* Eclipse as a whole is massive and likely not suitable for analysis with many existing
  tools. Our provided application is a small subcomponent - a launcher jar about 50KB in size.
* The source code is available at http://git.eclipse.org. The provided jar was pulled
  from a binary distribution of version 4.6.
* Eclipse uses lambda expressions and method references.
* <tt>org.eclipse.equinox.launcher.Main</tt> has a main method and is the entry point for
  the launcher jar. It is suitable as an entrypoint for analysis.

### OpenJDK Java8 Runtime

* [OpenJDK](http://openjdk.java.net/) is an implementation of Java. A substantial part
  of any Java implementation is the runtime library (which includes all the "built-in"
  functionality like java.lang, java.io, java.util, etc).
* The source code is available at http://hg.openjdk.java.net/. The provided jars were pulled
  from a binary distribution of 1.8.0_45.
* The Java8 runtime uses every new Java8 feature extensively, as API are often improved to take
  advantage of new features.
* There is no single entry point for the Java8 runtime, and it certainly isn't suitable
  for analysis as a whole. Instead small subsets or individual classes are typically analyzed.

### Jetty

* [Jetty](http://www.eclipse.org/jetty/) is a web server and servlet container.
* It is about 450K lines of code and about 1MB of jars. However, some components are dynamically loaded
  and were not included in the test suite.
* The source code is available at https://github.com/eclipse/jetty.project.git. The provided
  jars were built with <tt>0fc897233a0a83720d7d353b98224b662f152463</tt> (the 9.4.0
  development branch)
* Jetty uses lambda expressions and method references.
* <tt>org.eclipse.jetty.start.Main</tt> has a main method and is the primary driver for the
  server.

<a name="provided-tests"/>

## Provided Test Families and Tests

### Call Graph

#### IR

The call graph IR is a plain text file with one call graph edge per line. Each edge is represented as <tt>_node_ -> _node_</tt>, where _node_ is <tt>full.class.name(method_descriptor)</tt>. For example:

<tt>com.contoso.Foo.bar([Ljava/lang/String;)V -> com.contoso.Baz.quux(I)V</tt>

for a call from method com.contoso.Foo.bar(String) to com.contoso.Baz.quux(int)

Each adapter is expected to output the entire call graph (all edges) for the
application it is analyzing reachable from the entry point provide (however,
it may ignore the entry point and output additional edges which aren't
reachable from the entry point).

The IR is just a list of single edges. The test evaluator is expected to
perform higher level tests (like checking for paths, etc) on the call graph based on 
this lower level information.


#### Test Family



### Slicing IR/Queries

The slicing "ir" is slightly different than the call graph IR. For the slicing tests
you specify a query and an expected result. The query is in the format:

<tt>com.contoso.Foo.bar([Ljava/lang/String;)V:0 -> com.contoso.Baz.quux(I)V:1</tt>
<tt>com.contoso.Foo.bar([Ljava/lang/String;)V:1 -> com.contoso.Baz.quux(I)V:1</tt>

and the expected output is in the format:

<tt>com.contoso.Foo.bar([Ljava/lang/String;)V:0 -> com.contoso.Baz.quux(I)V:1: true</tt>
<tt>com.contoso.Foo.bar([Ljava/lang/String;)V:1 -> com.contoso.Baz.quux(I)V:1: true</tt>

The "query" asks if there is a data dependence between <tt>Foo.bar</tt>'s first formal 
and <tt>Baz.quux</tt>'s second formal. Only data (not control) dependencies should be
considered.

The query should be specified (one question per line) in the file
<tt>apps/&lt;app&gt;/ground_truth/slicing_query</tt>. The output is in the file 
<tt>apps/&lt;app&gt;/ground_truth/slicing_query</tt> and is exactly the question, repeated,
followed by a colon and "true" or "false" depending on if a dependency is expected or not.


<a name="setup"/>

## Installing and Running the Framework

The steps for setting up pytests are following.

* Installation
```bash
pip install -U pytest
```

* Get Source for the test framework
```bash
git clone https://github.com/GrammaTech/j8-tests.git
cd j8-tests/
```

* Running the system
```
python setup.py --tool <tool1>=<path_to_tool1> 
                [ --tool2 <tool2>=<path_to_tool2> ]
                [ --app app1 ] [ --app app2 ]
                [ -k test_<family> ]
                [ --log_output ]
```

  * <tt>--tool foo=/path/to/foo</tt> specifies the name of the tool and its path It must 
    be one of the supported tools (see below). The path is the location of the root of the 
    (compiled) source distribution of the tool. The approprite target/classes, etc
    paths will be added to the CLASSPATH for running the tool. Multiple <tt>--tool</tt> options
    can be present. All the given tools will be tested. Tool names should always be specified
    in all lower case (e.g. wala).
  * <tt>--app app</tt> specifies an application to test (that is analyze with each tool). If
    no <tt>--app</tt> options are given, all applications in the test suite will be run, 
    otherwise, only those specified will be run. Application names should always be specified
    in all lower case (e.g. ant).
  * <tt>-k test_&lt;family&gt;</tt> limits the test families that will be run. If no <tt>-k</tt>
    options are specified all test families will be run.
  * <tt>--log_output</tt> will generate a log file in <tt>log_run/</tt> containing diagnostic
    information potentially useful for diagnosing test infrastructure problems or failing
    tests.

<a name="extending"/>

## Extending the test suite

All the terminology in this section is defined in [the overview section](#overview). We sometimes use "family" as an abbreviation for "test family."

### Adding a new tool
If you wish to test a new tool with our test suite, you should:
* Write an adapter for each of the existing test families that you wish to apply to your tool. Relevant info for writing adapters for the existing IRs is as follows:
    * Call graph adapter  [this section](#call-graph)
    * Slicing adapter : TODO
* Set up the classpath rules and dependencies
   * The classpath for each tool is defined in [`tests/utils.py`](https://github.com/GrammaTech/j8-tests/blob/master/tests/utils.py), in the function `generate_classpath`. This function takes as input the tool name and the path (location) where the tool is installed, and generates a classpath suitable for compiling and running the adapter relative to the root of the user's installation. See the existing  `generate_classpath` function for examples.

### Adding a new adapter
If you are adding either a new IR/test family or a new tool and need to create a new adapter, you should:
* Write a Java class that uses the tool to produce the desired IR. Typically the adapter will use the tool as though it were a library.
  * The adapter should be named 
    <tt>tests/&lt;family&gt;/&lt;tool&gt;&lt;prefix&gt;Adapter.java</tt>
    where prefix is a short family-specific identifier (like CG for call graph)
  * The adapter should provide a main method which takes the following arguments:
    * The path to the java runtime jars. This path will be provided by the testing system
    * One or more paths to application jars
    * The name of the main class in the application, i.e., the class that contains <tt>main(String[] args)</tt>  and should be used as an entrypoint for analysis
  * When invoked, the adapter should emit the IR on stderr, and exit 0 (on success).
* Add a test to wrap the adapter compilation in the file <tt>/tests/&lt;family&gt;/adapter_test.py</tt> as seen in (TODO add example). This ensures that the adapter is actually built before we attempt to run any tests. If adapter compilation fails, pytests will not run any tests for that adapter.

### Adding a new application jar
To add a new application jar, you should:
* Create a subdirectory of `src/apps` and place the application jar file(s) there, including all jars necessary to compile and run the adapter.
* Create <tt>src/apps/&lt;app&gt;/main&gt;</tt>, a plain text file whose sole contents is the
  name of the main class, i.e.,the class that contains <tt>main(String[] args)</tt>  and should be used as an entrypoint for analysis.
* Add ground truth for one or more test families in the directory <tt>src/apps/&lt;app&gt;/ground_truth</tt>. The ground truth file should be named <tt>&lt;family&gt;_&lt;testid&gt;</tt>, where `family` is the name of the test family and `testid` is the name/identifier of an individual test in the family.
* Update the documentation as explained [below](#extending-documentation).

### Adding a new test/test evaluator
To add a new test to an existing test family, you should:
* Create a test evaluator in <tt>/tests/&lt;family&gt;</tt>. The test evaluator can be in a new file or it can be added as a new test function in an existing test file for the appropriate family. However, do not pollute the file <tt>/tests/&lt;family&gt;/adapter_test.py</tt> by adding "real" tests there; this file should only contain the test for adapter compilation.
* The test name and signature should follow the pattern below, where `family` is the name of the test family and `testid` is the name/identifier of the individual test.
```
def test_family_testid(adapter,app):
    xtest_family_testid(adapter,app)

@utils.change_dir(os.path.dirname(__file__))
def xtest_family_testid(adapter,app):
```
* TODO link to examples of test evaluators
* The test must follow the pytest pattern of [assert based testing](https://docs.pytest.org/en/latest/assert.html)
* Update the documentation as explained [below](#extending-documentation).

### Adding a new IR/test family

To add a new test family and associated IR, you should:
* Design the IR carefully so that it is tool-independent and contains enough information to verify multiple properties of the tool
* Add an adapter for one or more tools and the new IR, as explained above
* Add one or more tests/test evaluators, as explained above
* Update the documentation as explained [below](#extending-documentation).

<a name="extending-documentation"/>

### Documentation guidelines

When extending the test suite, add to this README documentation that covers at least the following details.

* When adding a new application
  * general info such as purpose (e.g. "this is a mail server application")
  * size in MB/LOC as appropriate
  * source where it was obtained, ideally with a link
  * rationale for inclusion in test suite (e.g. particulars on use of Java 8 features)
  * any other relevant info such as entrypoint classes for tools that require them

* When adding a new IR/test family
  * a high-level description of the IR, what information it contains and why it was chosen
  * one high-level paragraph describing the test family associated with this IR
  * a lower-level specification of the IR with examples if appropriate
  * any info about to the IR that the user would find relevant when writing an adapter
  * any info relevant to a user writing new tests using this IR, e.g. libraries/APIs that may be useful in processing the IR
  * any ideas for future tests using this IR

* When adding a new test
  * basic description (e.g. "check for presence of specific edges in the call graph")
  * motivation for test (features/analyses the test is addressing)
  * info on provided ground truth, including how it was generated and why it was chosen (process and motivation)


