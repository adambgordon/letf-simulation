from pathlib import Path

def getAbsPath():
    p = str(Path(__file__).parent.parent)
    return p[:p.find("/letf-simulation")]+"/letf-simulation"
