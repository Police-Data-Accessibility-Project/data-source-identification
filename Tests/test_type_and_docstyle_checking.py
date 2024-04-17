import os

import pytest
from unittest.mock import Mock
from util.type_and_docstyle_checking import (run_command, find_modified_python_files,
                                             check_files, has_errors)

# Example content for testing subprocess and os functionality
modified_files_output = "script1.py\nscript2.py"

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


def test_has_errors():
    """Test error detection."""
    assert not has_errors("Success: no issues found in 2 source files")
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
def test_func(x: int) -> int:
    return x + 1
                """,
        file_name="mypy_file"
    )

    # This file will have a docstring style issue
    pydocstyle_file = create_temp_py_file(
        content="""
\"\"\"This is a module docstring\"\"\"
def test_func():
    \"\"\"This is a function docstring\"\"\"
    return
            """,
        file_name="pydocstyle_file"
    )

    yield [mypy_file, pydocstyle_file]  # Provide the file paths to the test
    os.unlink(mypy_file)  # Clean up files after test
    os.unlink(pydocstyle_file)


def test_mypy_and_pydocstyle_issues(temp_python_files):
    mypy_errors, pydocstyle_errors = check_files(temp_python_files)
    assert len(mypy_errors) > 0
    assert len(pydocstyle_errors) > 0

    # Check that each set of errors does not include the file designed to be compliant
    for error in pydocstyle_errors:
        assert 'pydocstyle_file' not in error
    for error in mypy_errors:
        assert 'mypy_file' not in error
