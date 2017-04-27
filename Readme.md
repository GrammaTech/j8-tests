## Table of Contents  
[Overview and Terminology](#overview)  
[Architecture](#architecture)  
[Provided Applications](#provided-applications)  
[Provided Tests](#provided-tests)  
[Installing and Running our Framework](#setup)  
[Extending our Test Suite](#extending)  

<a name="overview"/> 

## Overview and Terminology

This system provides a test suite to assess Java 8 support in a number of popular bytecode analysis tools. The suite comes with existing tests but is also extensible as described in [this section](#extending).

We first give a high-level overview of our system and define some relevant terminology. A **tool** is a bytecode analysis tool; some example tools are WALA and Soot. An **application** is a jar file; the tools will analyze the bytecode contained in the applications.

Every tool-application pair can be tested for various kinds of functionality. Therefore, we have a notion of **test families**. A test family is a grouping of tests which test related functionality. Some examples of test families are tests for call graph construction and tests for slicing.

Every test family is associated with an **IR** or intermediate representation. The idea is that every tool, when run on an application, should provide output in a standardized format appropriate to the test family. For example, for the call graph construction test family, our IR is a serialization of the call graph. Every tool requires an **adapter** for every IR; the adapter is a piece of code that runs the tool and ensures its output matches the standardized format required by the IR.

Once a tool has been run on an application and we have obtained the IR (such as a call graph serialization), we run multiple **test evaluators** on this IR. Every test evaluator compares some portion of the IR against a known **ground truth**. For example, a test evaluator might check if a node corresponding to method `foo()` is present in the call graph. If the test evaluator determines that the IR matches the ground truth, the appropriate test passes, otherwise it fails.

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

A typical  test evaluator starts by building an appropriate adapter. Building the adapter requires knowing the correct classpath for the tool itself, since the adapter depends on the tool. The module `tests/utils.py` serves to convert the tool path (which the user passes in) to the required classpath for adapter building. Once the adapter is built, the test evaluator generates the IR for the application and compares it to the ground truth.

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
* Eclipse as a whole is massive (and likely not suitable for analysis with many existing
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

... more soon ...

#### Test Family



### Slicing IR/Queries

TODO

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
python setup.py --tool <Tool1> --tool_path <path_to_tool1> --tool <Tool2> --tool_path <path_to_tool2>
```
If the user wishes to skip the setup, they can directly run pytest by invoking
```
pytest --tool <Tool1> --tool_path <path_to_tool1>
```

<a name="extending"/>

## Extending the test suite

### Adding a new tool
To add a new tool, the following steps should be taken:
* Write an adapter (see below), which is a small Java class which interfaces
  between the testing infrastructure and the tool itself for one or more
  test families.
    * The call graph adapter  [this section](#call-graph)
    * The slicing adapter : TODO
* Setup the classpath rules and dependencies
   * The classpath for each tool is defined in <tt>tests/utils.py</tt>, in the function
     <tt>generate_classpath</tt> which takes the tool name and user provided
     path to the sandbox. This function should make a classpath suitable for
     compiling and running the adapter relative to the "root" of the
     installation provided by the user.

### Adding a new adapter
To add a new adapter (an interface between a tool and the testing system,
which generates an IR), the following steps should be taken:
* Write a Java class, which uses the tool (often using it like a library) to
  produce the IR for the test family the adapter is providing an interface
  for.
  * The class should live in
    <tt>tests/&lt;family&gt;/&lt;tool&gt;&lt;prefix&gt;.java</tt>
    where prefix is some short family specific identifier (like CG for call
    graph)
  * It should provide a main method which takes the following arguments:
    * The path to the testing system provided java runtime jars.
    * One or more paths to application jars
    * Finally, the name of the main class.
  * When invoked, it should emit the IR on stderr, and exit 0 (on success).

### Adding a new application jar
To add a new application jar, the following steps should be taken:
* Create a folder to host the jar files under src/apps directory
* Add all jars necessary to compile and run the adapter.
* Create <tt>src/apps/&lt;app&gt;/main&gt;</tt>, a pain text file whose sole contents is the
  name of the name of 'Main' class (the class containing the <tt>main(String[] args)</tt> 
  entry point.
* Add ground truth for one or more test families. The ground truth lives in
  in the directory for each individual test family <tt>tests/&lt;family&gt;</tt>
  usually named <tt>&lt;prefix&gt;_&lt;app&gt;</tt>.


### Adding a new test metric/evaluator
There are three types of evaluator to be added
* Evaluator to test for the adapter, this would check if the adapter can be compiled
* A new test extension to use existing adapter/IR
    * Any new test will have the signature test_foo(adapter, app), this ensures test is called
    * The test must follow pytest rule of assert based testing, that is assert to test
* Add a new test family
    * All the test family should be under test directory


### Adding a new IR

* A 'IR' is a way for a tool to communicate with the test
  infrastructure. It is emitted by an adapter (see above) and evaluated by
  the evaluator. A well designed IR should be tool independent, and
  communicate enough information to verify multiple properties of the tool.
* Adding an 'IR' amounts to writing a new adapter for one or more tools (see
  above) and writing an evaluator (also see above) for some property of that
  IR.


### Documentation guidelines

When extending the test suite, add documentation to cover at least the following details.

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


