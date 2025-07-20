#!/bin/bash
# Simple test runner for structur

echo "Running structur tests..."
python tests/run_tests.py

if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed!"
    exit 1
fi 