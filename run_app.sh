#!/bin/bash
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export PYTHONPATH="/opt/homebrew/lib/python3.12/site-packages:$PYTHONPATH"
/opt/homebrew/bin/python3.12 app.py
