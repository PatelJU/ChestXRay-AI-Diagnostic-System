"""
Basic tests for ChestXRay AI Diagnostic System
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_python_version():
    """Ensure Python version is 3.9 or higher."""
    assert sys.version_info >= (3, 9), "Python 3.9 or higher is required"


def test_imports():
    """Test that main modules can be imported."""
    try:
        # Test AI module imports
        from ai.model_manager import ModelManager
        from ai.report_generator import ReportGenerator
        from ai.heatmap_generator import HeatmapGenerator
        from ai.medical_report_generator import MedicalReportGenerator
        
        # Test GUI module imports (may fail in headless environment, which is OK)
        try:
            from gui.main_window import MainWindow
        except:
            pass  # GUI imports may fail in CI environment
        
        assert True, "All core modules imported successfully"
    except ImportError as e:
        assert False, f"Failed to import modules: {e}"


def test_config_exists():
    """Test that configuration directory exists."""
    import os
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config')
    assert os.path.exists(config_path), "Config directory should exist"


def test_model_directory_exists():
    """Test that model directory exists."""
    import os
    model_path = os.path.join(os.path.dirname(__file__), '..', 'already_trained_model')
    assert os.path.exists(model_path), "Model directory should exist"


def test_requirements_file_exists():
    """Test that requirements.txt exists."""
    import os
    req_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    assert os.path.exists(req_path), "requirements.txt should exist"
    
    # Check that file is not empty
    with open(req_path, 'r') as f:
        content = f.read()
        assert len(content) > 0, "requirements.txt should not be empty"
        assert 'torch' in content, "requirements.txt should contain torch"
        assert 'torchvision' in content, "requirements.txt should contain torchvision"


def test_main_file_exists():
    """Test that main.py exists and contains expected content."""
    import os
    main_path = os.path.join(os.path.dirname(__file__), '..', 'main.py')
    assert os.path.exists(main_path), "main.py should exist"
    
    with open(main_path, 'r') as f:
        content = f.read()
        assert 'MedicalAIApp' in content, "main.py should contain MedicalAIApp class"
        assert 'ChestXRay AI Diagnostic System' in content, "main.py should contain app title"
