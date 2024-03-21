from pathlib import Path

def getAbsPath():
    """Get the absolute path."""
    p = str(Path(__file__))
    return p[:p.find("/letf-simulator")]+"/letf-simulator"
