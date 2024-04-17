import os
import tempfile

import pytest
from unittest.mock import Mock, patch
from util.type_and_docstyle_checking import (run_command, find_modified_python_files,
                                             check_files, has_errors)

# Example content for testing subprocess and os functionality
modified_files_output = "script1.py\nscript2.py"
mypy_output = "Success: no issues found in 2 source files"
pydocstyle_output = ""

def is_tool_installed(name):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which
    return which(name) is not None

@pytest.fixture(scope="session", autouse=True)
def check_dependencies():
    """Ensure that all necessary dependencies are installed."""
    tools = ["mypy", "pydocstyle"]
    missing_tools = [tool for tool in tools if not is_tool_installed(tool)]
    if missing_tools:
        pytest.fail(f"Missing tools required for tests: {', '.join(missing_tools)}", pytrace=False)

@pytest.fixture
def mock_subprocess_run(mocker):
    """Mock for subprocess.run."""
    mock = mocker.patch('subprocess.run')
    mock.return_value = Mock(stdout=modified_files_output, stderr='')
    return mock

@pytest.fixture
def mock_os_getenv(mocker):
    """Mock for os.getenv."""
    mocker.patch('os.getenv', return_value="fake_ref")

def test_run_command(mock_subprocess_run):
    """Test run_command function."""
    output = run_command("echo Hello")
    assert output == "script1.py\nscript2.py"
    mock_subprocess_run.assert_called_once_with("echo Hello", text=True, shell=True, capture_output=True)

def test_find_modified_python_files(mock_subprocess_run, mock_os_getenv):
    """Test finding modified Python files."""
    files = find_modified_python_files()
    assert files == ["script1.py", "script2.py"]

def test_run_mypy(mock_subprocess_run):
    """Test running mypy."""
    mock_subprocess_run.return_value.stdout = mypy_output
    result = run_mypy(["script1.py", "script2.py"])
    assert "no issues found" in result

def test_run_pydocstyle(mock_subprocess_run):
    """Test running pydocstyle."""
    mock_subprocess_run.return_value.stdout = pydocstyle_output
    result = run_pydocstyle(["script1.py", "script2.py"])
    assert result == ""

def test_has_errors():
    """Test error detection."""
    assert not has_errors(mypy_output)
    assert has_errors("error: failed to do something")

def test_check_files_no_modification(mock_subprocess_run, capsys):
    """Test check_files with no files modified."""
    mock_subprocess_run.return_value.stdout = ""
    check_files([])
    captured = capsys.readouterr()
    assert "No Python files were modified." in captured.out

def test_check_files_with_errors(mock_subprocess_run, capsys):
    """Test check_files function when errors are found."""
    mock_subprocess_run.side_effect = [
        Mock(stdout="script1.py script2.py", stderr=''),
        Mock(stdout="error: issue found in script1.py", stderr=''),
        Mock(stdout="", stderr='')
    ]
    with pytest.raises(SystemExit) as e:
        check_files(["script1.py", "script2.py"])
    assert e.type == SystemExit
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "Errors detected in mypy or pydocstyle" in captured.out



def create_temp_py_file(content: str, file_name: str):
    """Helper function to create a temporary Python file with given content."""
    with open(f"{file_name}.py", 'w') as f:
        f.write(content)
    return f.name

@pytest.fixture
def temp_python_files():
    """Fixture to create Python files with deliberate mypy and pydocstyle issues."""
    # This file will have a type hint issue
    mypy_file = create_temp_py_file(
        content="""
def test_func(x):
    return x + 1
                """,
        file_name="mypy_file"
    )

    # This file will have a docstring style issue
    pydocstyle_file = create_temp_py_file(
        content="""
def test_func():
    \"\"\"This is a docstring\"\"\"
    return
            """,
        file_name="pydocstyle_file"
    )

    yield [mypy_file, pydocstyle_file]  # Provide the file paths to the test
    os.unlink(mypy_file)  # Clean up files after test
    os.unlink(pydocstyle_file)

def test_mypy_and_pydocstyle_issues(temp_python_files):
    check_files(temp_python_files)
    # # Run mypy and check for errors
    # mypy_result = run_mypy(temp_python_files)
    # assert "error:" in mypy_result
    #
    # # Run pydocstyle and check for errors
    # pydocstyle_result = run_pydocstyle(temp_python_files)
    # assert "D400" in pydocstyle_result  # Example check for a specific pydocstyle error code