import pandas as pd
import importlib
import final_check; importlib.reload(final_check)
test = pd.read_csv('params_temp.csv')

final_check.final_check(test)

print (test.T)
