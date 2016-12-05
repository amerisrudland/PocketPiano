import pickle
import time
#Saves local variables in files

#loads a variable from save and prints it
loadedVariable = pickle.load ( open( "save.p", "rb"))
print '{0}'.format(loadedVariable)

myVariable = 'initialized'
pickle.dump(myVariable,open("save.p", "wb"))

time.sleep(30)


