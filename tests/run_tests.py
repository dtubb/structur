#!/usr/bin/env python3
"""
Test runner for structur.py
Run this script to execute all unit tests.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import structur
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and run tests
from test_structur import TestStructurFunctions

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestStructurFunctions)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful()) 