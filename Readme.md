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

Once a tool has been run on an application and we have obtained the IR (such as a call graph serialization), we run multiple **test evaluators** on this IR. Every test evaluator compares some portion of the IR against a known **ground truth** For example, a test evaluator might check if a node corresponding to method `foo()` is present in the call graph. If the test evaluator determines that the IR matches the ground truth, the appropriate test passes, otherwise it fails.

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

* Describe each application here, giving at least:
  * general info such as purpose (e.g. "this is a mail server application")
  * size in MB/LOC as appropriate
  * source where it was obtained, ideally with a link
  * rationale for inclusion in test suite (e.g. particulars on use of J8 features)
  * any other relevant info such as entrypoint classes for tools that require them

<a name="provided-tests"/> 

## Provided Test Families and Tests

* Describe every IR in detail, giving at least:
  * a high-level description of the IR, what information it contains and why it was chosen
  * one high-level paragraph describing the test family associated with this IR. Don't add information that is redundant wrt comments in the code, but give an overview of what we test (e.g. "our call graph tests include testing for feaures such as: including a particular method, graph connectedness in the presence of lambdas, etc, etc"...)
  * a lower-level specification of the IR with examples if appropriate
  * any info that the user would find relevant when writing an adapter (note this is NOT the place to document how to write an adapter, here just put any features unique to that specific IR that may help someone writing an adapter, such as "don't forget to print full method names including package information").

### Call Graph IR

The call graph IR is a plain text file with one call graph edge per line. Each edge is represented as <tt>_node_ -> _node_</tt>, where _node_ is <tt>full.class.name(method_descriptor)</tt>. For example:

<tt>com.contoso.Foo.bar([Ljava/lang/String;)V -> com.contoso.Baz.quux(I)V</tt>

for a call from method com.contoso.Foo.bar(String) to com.contoso.Baz.quux(int)

Each adapter is expected to output the entire call graph (all edges) for the
application it is analyzing reachable from the entry point provide (however,
it may ignore the entry point and output additional edges which aren't
reachable from the entry point).

... more soon ...

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
cd j8-tests/test_framework/
```

* Running the system
```
python setup.py --tool <Tool1> --tool_path <path_to_tool1> --tool <Tool2> --tool_path <path_to_tool2>
```
If user wishes to skip the setup, they can directly run pytest by invoking
```
pytest --tool <Tool1> --tool_path <path_to_tool1>
```

This would run the all test, the tool and tool_path combination will build all adapters for the tools, and run all the test evaluation for all the applications found in src/apps directory. 

<a name="extending"/>

## Extending the test suite

### Adding a new tool
* How to write adapter

### Adding a new application jar
* Should be easy, only need ground truth

### Adding a new test metric/evaluator

### Adding a new IR 
* Will need adapters for every tool and new test evaluators
