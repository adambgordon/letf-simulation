from helper import getAbsPath

PATH = getAbsPath()

exec(open(PATH+'/logic/simulate.py').read())
exec(open(PATH+'/logic/percentiles.py').read())
