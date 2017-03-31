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
python setup.py --tool <Tool1> --tool_path <path_to_tool1> --tool <Tool2>
--tool_path <path_to_tool2>
```
If user wishes to skip the setup, they can directly run pytest by invoking
```
pytest --tool <Tool1> --tool_path <path_to_tool1>
```

Our testing framework is based on
[pytest](https://docs.pytest.org/en/latest/). A test involves running an **adapter** for a
**tool** on an **application**. This produces an **IR** which is fed into a
**test evaluator** that compares it to a **ground truth**.
