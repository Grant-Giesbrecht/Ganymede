# Import Modules
import copy
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
from os import path

schema_name = "SweepSchema_4950_8x100"
scan_name_prefix = "4950_8x100"
plot_data_graph_name = "Script Values Plot 4950_8x100";

freqs = np.linspace(8e9, 12e9, 5, endpoint=True);

max_opt_iter = 300
weight_Pout = 1
weight_PAE = 1

Plevel_W = .2
Ptol_W = .01
target_PAE = 50

Pmax = 20
Pmin = 15
gamma_max = 1
gamma_min = .001
arg_max = 360
arg_min = .001

header_notes = ""

# Create project and verify schematic is present
proj = AWRProject()
proj.connect()
if not proj.findSchematic(schema_name, silent=False):
	proj.msg(f"Failed to find schematic {schema_name}. Aborting.")
	sys.exit()

#**************** Create Optimization Goals and Add to Project *****************

g1 = OptGoal()
g1.set(rdname="PAE Goal", x0=7.99e9, x1=8.01e9, xU=MWO.mwUT_Frequency)
g1.set(comparison=MWO.mwOGT_GreaterThan, y0=target_PAE, y1=target_PAE, yU=MWO.mwUT_Frequency)
g1.set(circSim=f"{schema_name}.AP_HB", measName="PAE(PORT_1,PORT_2)", L=2, w=weight_PAE)

g2 = copy.deepcopy(g1)
g2.set(rdname="Pload High", comparison=MWO.mwOGT_LessThan, y0=Plevel_W+Ptol_W, y1=Plevel_W+Ptol_W)
g2.set(measName=f"PT(PORT_2)", w=weight_Pout)

g3 = copy.deepcopy(g2)
g3.set(rdname="Pload Low", comparison=MWO.mwOGT_GreaterThan, y0=Plevel_W-Ptol_W, y1=Plevel_W-Ptol_W)

proj.optGoals.append(g1)
proj.optGoals.append(g2)
proj.optGoals.append(g3)

# Tell project class to clear AWR project goals and apply these goals from Python
if not proj.applyGoals(silent=False):
	proj.msg("Failed to apply optimizer goals. Aborting.")
	sys.exit()

#********** Find Optimization Variables and Configure for Optimizer ************

v1 = AWRVariable(schema_name, "Pin=*")
v1.set(rdname="Pin", name="Pin", maximum=20, minimum=15)

v2 = AWRVariable(schema_name, "MagGamma=*")
v2.set(rdname="MagGamma", schema=schema_name, name="MagGamma", maximum=gamma_max, minimum=gamma_min)

v3 = AWRVariable(schema_name, "ArgGamma=*")
v3.set(rdname="ArgGamma", schema=schema_name, name="ArgGamma", maximum=arg_max, minimum=arg_min)

proj.variables.append(v1)
proj.variables.append(v2)
proj.variables.append(v3)


proj.warning(f"The optimization variables are NOT being overwritten in AWR. They must be configured manually!")
# if not proj.applyOptVariables(silent=False):
# 	proj.msg("Failed to apply optimizer variables. Aborting.")
# 	sys.exit()

#******************** Locate Graphs (For gathering data) ***********************

g = proj.graph(plot_data_graph_name)
if g is None:
	proj.msg(f"Failed to find graph {plot_data_graph_name}. Aborting.")
	sys.exit()

#******************************** Run Optimizer ********************************

proj.setMaxIterations(max_opt_iter)

data = []

for f in freqs:

	proj.updateOptFreq(f, silent=False)
	proj.runOptimizer(silent=False)

	proj.saveOptResults(data, g)

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
