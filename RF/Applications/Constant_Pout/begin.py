# Import Modules
from MWO import *
from matplotlib import pyplot as plt
import numpy as np
import MWO
import sys

############################# CONFIGURATION OPTIONS ############################

schema_name = "SweepSchema_3053_4x100"
freqs = np.linspace(8e9, 12e9, 5, endpoint=True);

################################################################################

# Initialize connection to Microwave Office
import win32com.client
awrde = win32com.client.Dispatch("MWOApp.MWOffice")

if not awrde.Project.Schematics.Exists(schema_name):
	print(f"Cannot find schematic '{schema_name}' needed for sweep.\n\nAborting.")
	sys.exit()
else:
	print(f"Found schematic '{schema_name}'.")

# Start from a clean slate
awrde.Project.OptGoals.RemoveAll()
print("Removed old optimizer goals.")

# Create optimizer goal
w = 1
L = 2
xStart = 7.99e9
xStop = 8.01e9
yStart = .2
yStop = .2
xUnit = MWO.mwUT_Frequency
yUnit = MWO.mwUT_Frequency
og = awrde.Project.OptGoals.AddGoal(schema_name, f"{schema_name}.AP_HB:PT(PORT_2)", MWO.mwOGT_Equals, w, L, xStart, xStop, xUnit, yStart, yStop, yUnit)

# Configure optimization variables

print(f"Created new optmizer goals.\n")
printGoals(awrde)
