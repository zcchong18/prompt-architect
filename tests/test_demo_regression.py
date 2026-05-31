import pytest
from scripts.demo_regression import run_demo


def test_demo_regression_integration():
    """Verify the regression demo runs and correctly detects the broken prompt."""
    run_demo()
