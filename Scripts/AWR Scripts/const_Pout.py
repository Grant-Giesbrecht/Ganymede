# Import Modules
from MWO import *
from matplotlib import pyplot as plt
import numpy as np
import MWO
import sys
import time
import timeit
from datetime import datetime
import win32com.client
from ganymede import *

############################# CONFIGURATION OPTIONS ############################

schema_name = "SweepSchema_3053_4x100"
plot_data_graph_name = "Script Values Plot";
freqs = np.linspace(8e9, 12e9, 25, endpoint=True);
scan_name_prefix = "3053_4x100"

max_opt_iter = 300
weight_Pout = 1000
weight_PAE = 1

Plevel_W = .2
Ptol_W = .01
target_PAE = 45

Pmax = 19
Pmin = 15
gamma_max = 1
gamma_min = .001
arg_max = 360
arg_min = .001

header_notes = ""

# Specify optimization variables
vars = []
vars.append(dict(Name=":Pin", Enabled=True, Maximum=Pmax, Minimum=Pmin, Constrained=True, Found=False))
vars.append(dict(Name=":MagGamma", Enabled=True, Maximum=gamma_max, Minimum=gamma_min, Constrained=True, Found=False))
vars.append(dict(Name=":ArgGamma", Enabled=True, Maximum=arg_max, Minimum=arg_min, Constrained=True))

############################# INITIALIZE CONNECTION ############################

# Initialize connection to Microwave Office
awrde = win32com.client.Dispatch("MWOApp.MWOffice")

# Check that schematic exists
if not awrde.Project.Schematics.Exists(schema_name):
	print(f"Cannot find schematic '{schema_name}' needed for sweep.\n\nAborting.")
	sys.exit()
else:
	print(f"-> Found schematic '{schema_name}'.")


############################# CONFIGURE OPTIMIZER ##############################

# Start from a clean slate
awrde.Project.OptGoals.RemoveAll()
print("-> Removed old optimizer goals.")

# Create optimizer goal (Minimum output power)
w = weight_Pout
L = 2
xStart = 7.99e9
xStop = 8.01e9
yStart = Plevel_W - Ptol_W
yStop = Plevel_W - Ptol_W
xUnit = MWO.mwUT_Frequency
yUnit = MWO.mwUT_Frequency
og_Plow = awrde.Project.OptGoals.AddGoal(f"{schema_name}.AP_HB", f"PT(PORT_2)", MWO.mwOGT_GreaterThan, w, L, xStart, xStop, xUnit, yStart, yStop, yUnit)

# Create optimizer goal (Maximum output power)
yStart = Plevel_W + Ptol_W
yStop = Plevel_W + Ptol_W
og_Plow = awrde.Project.OptGoals.AddGoal(f"{schema_name}.AP_HB", f"PT(PORT_2)", MWO.mwOGT_LessThan, w, L, xStart, xStop, xUnit, yStart, yStop, yUnit)

# Create optimizer goal (PAE)
w = weight_PAE
yStart = target_PAE
yStop = target_PAE
og_PAE = awrde.Project.OptGoals.AddGoal(f"{schema_name}.AP_HB", f"PAE(PORT_1,PORT_2)", MWO.mwOGT_GreaterThan, w, L, xStart, xStop, xUnit, yStart, yStop, yUnit)

# Print summary of optimizer goals
print(f"-> Created new optmizer goals.\n")
barprint("OPTIMIZATION GOALS")
printGoals(awrde)


####################### CONFIGURE OPTIMIZATION GOALS ###########################

# Check that optimization variables are correctly configured
for idx in range(1, awrde.Project.Optimizer.Variables.Count + 1):

	# Check if variable is listed in 'vars'
	vidx = 0
	found = False
	for v in vars:

		if v["Name"] == awrde.Project.Optimizer.Variables.Item(idx).Name:
			vf = v
			found = True
			break

		vidx += 1

	if not found:
		# Variable was not found, disbale and continue
		awrde.Project.Optimizer.Variables.Item(idx).Enabled = False
		continue


	# Copy parameters from 'vars' into AWRDE
	awrde.Project.Optimizer.Variables.Item(idx).Enabled = vf["Enabled"]
	awrde.Project.Optimizer.Variables.Item(idx).Maximum = vf["Maximum"]
	awrde.Project.Optimizer.Variables.Item(idx).Minimum = vf["Minimum"]
	awrde.Project.Optimizer.Variables.Item(idx).Constrained = vf["Constrained"]

	vf["Found"] = True
	vars[vidx] = vf

barprint("OPTIMIZATION VARIABLES")
printOptVars(awrde)

foundAll = True
for v in vars:

	if not v["Found"]:
		foundAll = False
		break

if not foundAll:
	print("\nSome optimization variables are missing!\nAborting.");
	sys.exit()
else:
	print("\n-> Optimization variables successfully configured.");

# Set maximum number of optimizer iterations
awrde.Project.Optimizer.MaxIterations = max_opt_iter

############################### CONFIGURE GRAPHS ###############################

# Find plot graph
g = None
for i in range(1, awrde.Project.Graphs.Count + 1):

	if awrde.Project.Graphs.Item(i).Name == plot_data_graph_name:
		g = awrde.Project.Graphs.Item(i)

# Check that plot graph exists
if g is None:
	print(f"Failed to find graph.\nAborting.")
	sys.exit()

# Loop over all values and run optimizer
data = []
for f in freqs:
	updateOptFreq(awrde, f)
	runOptimizer(awrde)

	saveOptResults(awrde, data, g)

ts = datetime.now().strftime("%d-%b-%Y %H%M")
# np.save(f"scan_{scan_name_prefix}_{ts}.npy", data)

#******************************* Save Data to DDF ******************************

# Reformat data into nice shape
ddf = sweepdict_to_ddf(data)

# Add sweep configuration data
ddf.add(max_opt_iter, "max_opt_iter", "Maximum number of optimizer iterations");
ddf.add(weight_Pout, "W_Pout", "Pout optimizer weight")
ddf.add(weight_PAE, "W_PAE", "PAE optimizer weight")
ddf.add(Plevel_W, "target_Pout", "[W] Target Pout for the optimizer")
ddf.add(Ptol_W, "tol_Pout", "[W] Tolerance for Pout in opt goal")
ddf.add(target_PAE, "target_PAE", "[%] Target for PAE for the optimizer")
ddf.add(Pmax, "Pmax", "[dBm] Max Pin the optimizer is permitted to try")
ddf.add(Pmin, "Pmin", "[dBm] Min Pin the optimizer is permitted to try")
ddf.add(gamma_max, "Gamma_max", "Maximum refl. coef. magnitude the optimizer is permitted to try")
ddf.add(gamma_min, "Gamma_min", "Minimum refl. coef. magnitude the optimizer is permitted to try")
ddf.add(arg_max, "Arg_max", "Maximum refl. coef. argument/angle the optimizer is permitted to try")
ddf.add(arg_min, "Arg_min", "Minimum refl. coef. argument/angle the optimizer is permitted to try")
ddf.add(ts, "timestamp", "Time when simulated sweep was completed")

# Add header
header_string = "Data saved from constant output power optimizer sweep. Created by `const_Pout.py`."
if len(header_notes) > 0:
	header_string = header_string + "\n\n" + header_notes;
ddf.setHeader(header_string);

ddf.save(f"scan_{scan_name_prefix}_{ts}.ddf")
