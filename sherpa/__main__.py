"""
Allows Sherpa to be run as a module: python -m sherpa
Useful as a reliable fallback on Windows when the sherpa.exe
entry point has sys.argv issues with editable installs.
"""

from sherpa.cli import main

if __name__ == "__main__":
    main()
