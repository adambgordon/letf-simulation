from helper import getAbsPath

PATH = getAbsPath()

exec(open(PATH+'/logic/run_simulation.py').read())
exec(open(PATH+'/logic/run_aggregation.py').read())
