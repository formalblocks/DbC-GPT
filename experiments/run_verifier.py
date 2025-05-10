#!/usr/bin/env python3
"""
Simple runner script for the verifier.
"""
import sys
import os

# Add the current directory to the path so we can import the verifier package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from verifier.main import main

if __name__ == "__main__":
    main() 