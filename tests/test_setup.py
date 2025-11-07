"""
Setup validation tests for SpendSense project infrastructure.

These tests verify that all setup and configuration is correct according
to Story 1.1 acceptance criteria.
"""

import os
import pathlib
import json
import pytest
import yaml


# Test Constants
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
SPENDSENSE_DIR = PROJECT_ROOT / "spendsense"
TESTS_DIR = PROJECT_ROOT / "tests"
DATA_DIR = PROJECT_ROOT / "data"


@pytest.mark.unit
class TestGitIgnore:
    """Test AC1: Repository initialized with .gitignore for Python/Node.js"""

    def test_gitignore_exists(self):
        """Verify .gitignore file exists."""
        gitignore_path = PROJECT_ROOT / ".gitignore"
        assert gitignore_path.exists(), ".gitignore file should exist"

    def test_gitignore_python_cache(self):
        """Verify .gitignore excludes Python cache files."""
        gitignore_path = PROJECT_ROOT / ".gitignore"
        content = gitignore_path.read_text()
        assert "__pycache__/" in content
        assert "*.py[cod]" in content

    def test_gitignore_venv(self):
        """Verify .gitignore excludes virtual environment."""
        gitignore_path = PROJECT_ROOT / ".gitignore"
        content = gitignore_path.read_text()
        assert "venv/" in content

    def test_gitignore_node_modules(self):
        """Verify .gitignore excludes Node modules."""
        gitignore_path = PROJECT_ROOT / ".gitignore"
        content = gitignore_path.read_text()
        assert "node_modules/" in content

    def test_gitignore_env_files(self):
        """Verify .gitignore excludes environment files."""
        gitignore_path = PROJECT_ROOT / ".gitignore"
        content = gitignore_path.read_text()
        assert ".env" in content


@pytest.mark.unit
class TestReadme:
    """Test AC2: README.md created with project overview and setup instructions"""

    def test_readme_exists(self):
        """Verify README.md file exists."""
        readme_path = PROJECT_ROOT / "README.md"
        assert readme_path.exists(), "README.md file should exist"

    def test_readme_has_title(self):
        """Verify README contains project title."""
        readme_path = PROJECT_ROOT / "README.md"
        content = readme_path.read_text()
        assert "SpendSense" in content

    def test_readme_has_overview(self):
        """Verify README contains overview section."""
        readme_path = PROJECT_ROOT / "README.md"
        content = readme_path.read_text()
        assert "## Overview" in content or "## About" in content

    def test_readme_has_prerequisites(self):
        """Verify README contains prerequisites section."""
        readme_path = PROJECT_ROOT / "README.md"
        content = readme_path.read_text()
        assert "Prerequisites" in content or "Requirements" in content

    def test_readme_has_setup_instructions(self):
        """Verify README contains setup instructions with commands."""
        readme_path = PROJECT_ROOT / "README.md"
        content = readme_path.read_text()
        # Should contain setup commands
        assert ("pip install" in content or "requirements.txt" in content)
        assert ("npm install" in content or "package.json" in content)


@pytest.mark.unit
class TestDirectoryStructure:
    """Test AC3: Directory structure created matching technical architecture"""

    @pytest.mark.parametrize("module_name", [
        "ingest",
        "features",
        "personas",
        "recommend",
        "guardrails",
        "ui",
        "eval",
        "api",
        "db",
        "config"
    ])
    def test_spendsense_modules_exist(self, module_name):
        """Verify all required spendsense submodules exist."""
        module_path = SPENDSENSE_DIR / module_name
        assert module_path.exists(), f"spendsense/{module_name}/ should exist"
        assert module_path.is_dir(), f"spendsense/{module_name}/ should be a directory"

    @pytest.mark.parametrize("module_name", [
        "ingest",
        "features",
        "personas",
        "recommend",
        "guardrails",
        "eval",
        "api",
        "db",
        "config"
    ])
    def test_python_init_files_exist(self, module_name):
        """Verify __init__.py files exist for Python packages."""
        init_path = SPENDSENSE_DIR / module_name / "__init__.py"
        assert init_path.exists(), f"spendsense/{module_name}/__init__.py should exist"

    def test_tests_directory_exists(self):
        """Verify tests/ directory exists."""
        assert TESTS_DIR.exists(), "tests/ directory should exist"
        assert TESTS_DIR.is_dir(), "tests/ should be a directory"

    @pytest.mark.parametrize("test_subdir", ["integration", "e2e"])
    def test_test_subdirectories_exist(self, test_subdir):
        """Verify test subdirectories exist."""
        test_path = TESTS_DIR / test_subdir
        assert test_path.exists(), f"tests/{test_subdir}/ should exist"

    @pytest.mark.parametrize("data_subdir", ["synthetic", "sqlite", "parquet", "logs"])
    def test_data_directories_exist(self, data_subdir):
        """Verify data/ subdirectories exist."""
        data_path = DATA_DIR / data_subdir
        assert data_path.exists(), f"data/{data_subdir}/ should exist"


@pytest.mark.unit
class TestDependencies:
    """Test AC4: Dependency files created with core libraries"""

    def test_requirements_txt_exists(self):
        """Verify requirements.txt exists."""
        req_path = PROJECT_ROOT / "requirements.txt"
        assert req_path.exists(), "requirements.txt should exist"

    @pytest.mark.parametrize("package,version", [
        ("fastapi", "0.104"),
        ("pydantic", "2.5"),
        ("pytest", "7.4"),
        ("pyarrow", "10"),
        ("pyyaml", "6.0")
    ])
    def test_requirements_contains_core_packages(self, package, version):
        """Verify requirements.txt contains required packages with versions."""
        req_path = PROJECT_ROOT / "requirements.txt"
        content = req_path.read_text().lower()
        assert package in content, f"{package} should be in requirements.txt"
        assert version in content, f"Version constraint for {package} should include {version}"

    def test_package_json_exists(self):
        """Verify package.json exists for frontend."""
        pkg_path = SPENDSENSE_DIR / "ui" / "package.json"
        assert pkg_path.exists(), "spendsense/ui/package.json should exist"

    def test_package_json_valid_format(self):
        """Verify package.json is valid JSON."""
        pkg_path = SPENDSENSE_DIR / "ui" / "package.json"
        with open(pkg_path) as f:
            data = json.load(f)  # Will raise if invalid JSON
        assert "dependencies" in data or "devDependencies" in data

    @pytest.mark.parametrize("package,version", [
        ("react", "18"),
        ("vite", "5"),
        ("typescript", "5"),
        ("tailwindcss", "3")
    ])
    def test_package_json_contains_frontend_deps(self, package, version):
        """Verify package.json contains required frontend dependencies."""
        pkg_path = SPENDSENSE_DIR / "ui" / "package.json"
        with open(pkg_path) as f:
            data = json.load(f)

        # Check in dependencies or devDependencies
        all_deps = {}
        if "dependencies" in data:
            all_deps.update(data["dependencies"])
        if "devDependencies" in data:
            all_deps.update(data["devDependencies"])

        assert package in all_deps, f"{package} should be in package.json"
        assert version in all_deps[package], f"{package} version should include {version}"


@pytest.mark.unit
class TestSetupScript:
    """Test AC5: One-command setup script created and documented in README"""

    def test_setup_script_exists(self):
        """Verify setup script exists."""
        setup_path = PROJECT_ROOT / "scripts/setup.sh"
        assert setup_path.exists(), "scripts/setup.sh should exist"

    def test_setup_script_is_executable(self):
        """Verify setup script has execute permissions."""
        setup_path = PROJECT_ROOT / "scripts/setup.sh"
        assert os.access(setup_path, os.X_OK), "scripts/setup.sh should be executable"

    def test_setup_script_creates_venv(self):
        """Verify setup script includes venv creation."""
        setup_path = PROJECT_ROOT / "scripts/setup.sh"
        content = setup_path.read_text()
        assert "venv" in content.lower(), "Setup script should create virtual environment"

    def test_setup_script_installs_dependencies(self):
        """Verify setup script installs dependencies."""
        setup_path = PROJECT_ROOT / "scripts/setup.sh"
        content = setup_path.read_text()
        assert "pip install" in content, "Setup script should install Python dependencies"
        assert "npm install" in content, "Setup script should install frontend dependencies"

    def test_readme_documents_setup_script(self):
        """Verify README documents the setup script."""
        readme_path = PROJECT_ROOT / "README.md"
        content = readme_path.read_text()
        assert "./scripts/setup.sh" in content or "scripts/setup.sh" in content


@pytest.mark.unit
class TestTestFramework:
    """Test AC6: Basic test framework configured with example test"""

    def test_pytest_ini_exists(self):
        """Verify pytest.ini configuration exists."""
        pytest_ini = PROJECT_ROOT / "pytest.ini"
        assert pytest_ini.exists(), "pytest.ini should exist"

    def test_pytest_ini_has_test_discovery(self):
        """Verify pytest.ini contains test discovery settings."""
        pytest_ini = PROJECT_ROOT / "pytest.ini"
        content = pytest_ini.read_text()
        assert "python_files" in content or "testpaths" in content

    def test_example_test_exists(self):
        """Verify example test file exists."""
        example_test = TESTS_DIR / "test_example.py"
        assert example_test.exists(), "tests/test_example.py should exist"

    def test_example_test_has_tests(self):
        """Verify example test file contains test functions."""
        example_test = TESTS_DIR / "test_example.py"
        content = example_test.read_text()
        assert "def test_" in content, "Example test should contain test functions"


@pytest.mark.unit
class TestConfiguration:
    """Test AC7: Configuration file system established using YAML"""

    def test_config_directory_exists(self):
        """Verify config/ directory exists."""
        config_dir = SPENDSENSE_DIR / "config"
        assert config_dir.exists(), "spendsense/config/ should exist"

    def test_yaml_config_file_exists(self):
        """Verify YAML configuration file exists."""
        config_file = SPENDSENSE_DIR / "config" / "settings.yaml"
        assert config_file.exists(), "spendsense/config/settings.yaml should exist"

    def test_yaml_config_valid_format(self):
        """Verify YAML configuration is valid."""
        config_file = SPENDSENSE_DIR / "config" / "settings.yaml"
        with open(config_file) as f:
            data = yaml.safe_load(f)  # Will raise if invalid YAML
        assert data is not None, "YAML config should contain data"


@pytest.mark.unit
class TestLogging:
    """Test AC8: Logging framework configured with structured output"""

    def test_logging_config_module_exists(self):
        """Verify logging configuration module exists."""
        logging_module = SPENDSENSE_DIR / "config" / "logging_config.py"
        assert logging_module.exists(), "spendsense/config/logging_config.py should exist"

    def test_logging_module_imports(self):
        """Verify logging module can be imported."""
        # This test verifies the module has valid Python syntax
        from spendsense.config import logging_config
        assert hasattr(logging_config, "configure_logging")
        assert hasattr(logging_config, "get_logger")

    def test_logging_configuration_works(self):
        """Verify logging can be configured and used."""
        from spendsense.config.logging_config import configure_logging, get_logger

        # Configure logging
        configure_logging(level="DEBUG", format_type="text")

        # Get logger and test it works
        logger = get_logger("test")
        logger.info("Test log message")  # Should not raise


@pytest.mark.integration
class TestSetupIntegration:
    """Test AC9: All setup executes successfully (integration test)"""

    def test_all_core_components_present(self):
        """Verify all core components are present for a working setup."""
        # This is a meta-test that checks all critical pieces exist
        checks = [
            (PROJECT_ROOT / ".gitignore").exists(),
            (PROJECT_ROOT / "README.md").exists(),
            (PROJECT_ROOT / "requirements.txt").exists(),
            (PROJECT_ROOT / "scripts/setup.sh").exists(),
            (PROJECT_ROOT / "pytest.ini").exists(),
            (SPENDSENSE_DIR / "ingest").exists(),
            (SPENDSENSE_DIR / "features").exists(),
            (SPENDSENSE_DIR / "config" / "settings.yaml").exists(),
            (TESTS_DIR / "test_example.py").exists(),
        ]
        assert all(checks), "All core setup components should be present"

    def test_python_package_structure_valid(self):
        """Verify spendsense is a valid Python package."""
        # Attempt to import the package
        import spendsense
        assert spendsense.__name__ == "spendsense"
