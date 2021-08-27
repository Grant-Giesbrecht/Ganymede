import re
import time
from pyddf import *
import win32com.client
from colorama import Fore, Back, Style

# mwOptGoalType
mwOGT_Equals = 0
mwOGT_LessThan = 1
mwOGT_GreaterThan = 2

# mwUnitType
mwUT_None = 0
mwUT_Frequency = 1
mwUT_Capacitance = 2
mwUT_Inductance =  3
mwUT_Resistance = 4
mwUT_Conductance = 5
mwUT_Length = 6
mwUT_LengthEnglish = 7
mwUT_Temperature = 8
mwUT_Angle = 9
mwUT_Time = 10
mwUT_Voltage = 11
mwUT_Current = 12
mwUT_PowerLog = 13
mwUT_Power = 14
mwUT_DB = 15
mwUT_String = 16
mwUT_Scaler = 17
mwUT_DBOnlyPower = 18
mwUT_WattsOnlyPower = 19
mwUT_TextOnly = 20



def runOptimizer(awrde):

	if awrde.Project.Optimizer.Running:
		print("Cannot start optimzier because it is already running!\nAborting.")
		sys.exit()

	awrde.Project.Optimizer.Start()

	width = 0
	st = time.time()
	while awrde.Project.Optimizer.Running:

		num_iter = str(awrde.Project.Optimizer.MaxIterations)
		width = len(num_iter)

		print(f"\r*** OPTIMIZER RUNNING *** (Time Elapsed: {format(round(time.time()-st, 2), '.2f').zfill(6)} s, Iteration: {str(awrde.Project.Optimizer.Iteration).zfill(width)}/{num_iter})", end='', flush=True)
		time.sleep(0.1)

	et = time.time()
	print(f"\r*** OPTIMIZER FINISHED *** (Time Elapsed: {format(round(time.time()-st, 2), '.2f').zfill(6)} s, Iteration: {str(awrde.Project.Optimizer.Iteration).zfill(width)}/{awrde.Project.Optimizer.MaxIterations})")

def updateOptFreq(awrde, f, idx=-1, delta=1):

	print(f"-> Changing frequency to {f/1e9} GHz")

	# Change project frequencies (b/c otherwise optimizer will run every freq)
	awrde.Project.Frequencies.Clear()
	awrde.Project.Frequencies.AddMultiple([f])

	if idx != -1:
		# Change optimizer goal frequency
		awrde.Project.OptGoals(idx).xStart = f - delta
		awrde.Project.OptGoals(idx).xStop = f + delta
	else:
		for idx in range(1, awrde.Project.OptGoals.Count + 1):
			# Change optimizer goal frequency
			awrde.Project.OptGoals(idx).xStart = f - delta
			awrde.Project.OptGoals(idx).xStop = f + delta


def updateElementParameter(awrde, schemaName:str, elementName:str, parameterName:str, value):

	schemaIdx = -1
	elmtIdx = -1
	paramIdx = -1

	# Get schema index
	for si in range(1, awrde.Project.Schematics.Count + 1):
		if awrde.Project.Schematics.Item(si).Name == schemaName:
			schemaIdx = si
			break;
	if schemaIdx == -1:
		return f"Failed to find schematic with name '{schemaName}'."

	# Get element index
	for ei in range(1, awrde.Project.Schematics.Item(schemaIdx).Elements.Count+1):
		if awrde.Project.Schematics.Item(schemaIdx).Elements.Item(ei).Name == elementName:
			elmtIdx = ei
			break
	if elmtIdx == -1:
		return f"Failed to find element with name '{elementName}'."

	# Get parameter index
	for pi in range(1, awrde.Project.Schematics.Item(schemaIdx).Elements.Item(elmtIdx).Parameters.Count + 1):
		if awrde.Project.Schematics.Item(schemaIdx).Elements.Item(ei).Parameters.Item(pi).Name == parameterName:
			paramIdx = pi
			break
	if paramIdx == -1:
		return f"Failed to find parameter with name '{parameterName}'."

	awrde.Project.Schematics.Item(schemaIdx).Elements.Item(elmtIdx).Parameters.Item(paramIdx).ValueAsDouble = value

def printParams(awrde, schemaName:str, elementName:str, indent:str="", subindent:str="  "):

	schemaIdx = -1
	elmtIdx = -1
	paramIdx = -1

	print(f"{indent}Parameters for [Sch:'{schemaName}', El:'{elementName}']:")
	# Get schema index
	for si in range(1, awrde.Project.Schematics.Count + 1):
		if awrde.Project.Schematics.Item(si).Name == schemaName:
			schemaIdx = si
			break;
	if schemaIdx == -1:
		return f"Failed to find schematic with name '{schemaName}'."

	# Get element index
	for ei in range(1, awrde.Project.Schematics.Item(schemaIdx).Elements.Count+1):
		if awrde.Project.Schematics.Item(schemaIdx).Elements.Item(ei).Name == elementName:
			elmtIdx = ei
			break
	if elmtIdx == -1:
		return f"Failed to find element with name '{elementName}'."

	# Get parameter index
	for pi in range(1, awrde.Project.Schematics.Item(schemaIdx).Elements.Item(elmtIdx).Parameters.Count + 1):
		print(f"{indent}{subindent}{awrde.Project.Schematics.Item(schemaIdx).Elements.Item(ei).Parameters.Item(pi).Name}")


def saveOptResults(awrde, data, g):

	# Create output dictionary
	nd = dict()

	# Scan over each optimization variable and save to dictionary
	for idx in range(1, awrde.Project.Optimizer.Variables.Count + 1):
		nd[awrde.Project.Optimizer.Variables.Item(idx).Name] = awrde.Project.Optimizer.Variables.Item(idx).Nominal

	# Scan over each value in graph and save to dictionary
	for idx in range(1, g.Measurements.Count + 1):
		nd[g.Measurements.Item(idx).Name] = g.Measurements.Item(idx).TraceValues(1)

	data.append(nd)

def sweepdict_to_ddf(dl):

	ddf = DDFIO()

	# Check for empty list
	if len(dl) < 1:
		return ddf

	# Check that is an array of dictionaries
	if type(dl[0]) is not dict:
		raise ValueError("Input must be an array of dictionaries")

	# Get keys
	keys = list(dl[0].keys())

	# Check that all elements have the same keys
	for d in dl:
		if keys != list(d.keys()):
			raise ValueError("Input list of dictionaries must all have the same keys")
	print(f"Keys: {d.keys()}")

	# Initialize interim dictionary
	interim = {key: [] for key in keys}
	interim["freq"] = []

	# Scan over each input dictionary
	for d in dl:

		allow_f = True

		# Scan over each key
		for k in keys:

			if type(d[k]) == tuple: # If tuple, save first param as freq (but only once for all tuples), second as data for key
				if allow_f:
					interim["freq"].append(d[k][0][0])
					allow_f = False
				interim[k].append(d[k][0][1])
			else:
				interim[k].append(d[k])

	print(interim)

	for k in list(interim.keys()):
		if not ddf.add(interim[k], makeValidName(k), ""):
			print(ddf.err())

	return ddf

class OptGoal:
	''' This class describes an optimizer goal for AWR. The objective is not to
	list the optimizer goals defined in a project, but to describe a goal in
	python and apply those goals fresh to AWR.'''

	def __init__(self):

		# Human readable name for easier referencing (optional)
		self.rdname = ""

		self.xStart = -1
		self.xStop = -1
		self.yStart = -1
		self.yStop = -1
		self.xUnit = -1
		self.yUnit = -1
		self.L = 2
		self.w = 1
		self.circSimName = "" #Example: "SweepSchema_4950_8x100.AP_HB"
		self.measName = "" #Example: "PT(PORT_2)", "PAE(PORT_1, PORT_2)"
		self.comparison = mwOGT_Equals #Options: mwOGT_GreaterThan, mwOGT_LessThan, mwOGT_Equals

	def set(self, x0=None, x1=None, xU=None, y0=None, y1=None, yU=None, L=None, w=None, circSim=None, measName=None, comparison=None, rdname=None):
		''' Set one or more parameters in one line '''

		if x0 is not None:
			self.xStart = x0
		if x1 is not None:
			self.xStop = x1
		if xU is not None:
			self.xUnit = xU
		if y0 is not None:
			self.yStart = y0
		if y1 is not None:
			self.yStop = y1
		if yU is not None:
			self.yUnit = yU
		if L is not None:
			self.L = L
		if w is not None:
			self.w = w
		if circSim is not None:
			self.circSimName = circSim
		if measName is not None:
			self.measName = measName
		if comparison is not None:
			self.comparison = comparison
		if rdname is not None:
			self.rdname = rdname


class AWRVariable:
	''' Describes a variable/equation in AWR. The goal is to locate an equation
	or variable already defined in an AWR schematic, global definition, etc and
	allow the script to easily adjust its value, enable optimization, etc. '''

	def __init__(self, schematic, name):

		# Human readable name for easier referencing (ie. in output data)
		self.rdname = ""

		self.disptxt = name # Name as appears in AWR schematics (ie. as is in Equation.DisplayText field)
		self.name = name # Name as appears in optimizer variable list (ie. as in OptVariable.Name field)
		self.schema = schematic # Schematic in which it is defined

		self.maximum = None
		self.minimum = None
		self.constrained = True
		self.optEnabled = True

		# self.found = False

	def set(self, rdname=None, disptxt=None, name=None, schema=None, maximum=None, minimum=None, constrained=None, enabled=None):
		''' Set one or more parameters in one line '''

		if rdname is not None:
			self.rdname = rdname
		if disptxt is not None:
			self.disptxt = disptxt
		if name is not None:
			self.name = name
		if schema is not None:
			self.schema = schema
		if maximum is not None:
			self.maximum = maximum
		if minimum is not None:
			self.minimum = minimum
		if constrained is not None:
			self.constrained = constrained
		if enabled is not None:
			self.enabled = enabled


class AWRProject:

	def __init__(self):

		self.awrde = None
		self.cs = "-> " # CLI message symbol
		self.cse = "-> ERORR: " #CLI error message symbol
		self.csd = "\tDEBUG: " #CLI debug message symbol'
		self.csw = "-> WARNING:" #CLI warning message symbol
		self.log = []

		self.meas_names = {}

		# Variables described in Python to find and optimize in the AWR project
		self.variables = []

		# Opt goals defined in Python to apply to the AWR project
		self.optGoals = []

	def getMeasName(self, ms:str):

		if ms in self.meas_names:
			return self.meas_names[ms]
		else:
			return ms

	def connect(self):

		# Initialize connection to Microwave Office
		self.awrde = win32com.client.Dispatch("MWOApp.MWOffice")

	def schema(self, name):

		si = self.getSchemaIdx(name)
		if si == -1:
			return None

		return self.awrde.Project.Schematics.Item(si)

	def eqn(self, schema, disptxt):

		(si, ei) = self.getEqIdx(schema, disptxt)
		if si == -1 or ei == -1:
			return None

		return self.schema(schema).Equations.Item(ei)

	def graph(self, graph_name):

		gi = self.getGraphIdx(graph_name)
		if gi == -1:
			return None

		return self.awrde.Project.Graphs.Item(gi)

	def optVar(self, ov_name):

		self.debug(f"OPTVAR() Search for '{ov_name}'.")

		ov_name = ov_name.replace("=", "(?<!=)=(?!=)")

		for idx in range(1, self.awrde.Project.Optimizer.Variables.Count + 1):
			if bool(re.match(ov_name, self.awrde.Project.Optimizer.Variables.Item(idx).Name)):
				self.debug("OPTVAR() Found item at index '{idx}'.")
				return self.awrde.Project.Optimizer.Variables.Item(idx)
			else:
				mm_name = self.awrde.Project.Optimizer.Variables.Item(idx).Name
				self.debug(f"OPTVAR: {mm_name} was not a match")
		self.warning("OPTVAR() Failed to locate item!")
		return None

	def getSchemaIdx(self, schema_name):

		idx = -1

		for si in range(1, self.awrde.Project.Schematics.Count + 1):

			schema_name = schema_name.replace("=", "(?<!=)=(?!=)")
			if bool(re.match(schema_name, self.awrde.Project.Schematics.Item(si).Name)):
				idx = si
				break;

		return idx

	def getEqIdx(self, schema_name, eq_disptxt):

		idx = -1

		# Get schematic index
		si = self.getSchemaIdx(schema_name)
		if si == -1:
			return (-1, -1)

		# Find equation
		eq_disptxt = eq_disptxt.replace("=", "(?<!=)=(?!=)")
		for ei in range(1, self.awrde.Project.Schematics.Item(si).Equations.Count + 1):

			if bool(re.match(eq_disptxt, self.awrde.Project.Schematics.Item(si).Equations.Item(ei).DisplayText)):
				idx = ei
				break

		return (si, ei)

	def getAWRScriptModule(self, script_name):

		for gsi in range(1, self.awrde.Project.Application.GlobalScripts.Count+1):
			if self.awrde.Project.Application.GlobalScripts.Item(gsi).Name == script_name:
				return self.awrde.Project.Application.GlobalScripts.Item(gsi)

		return None

	def getAWRScriptRoutine(self, script_name, routine_name):

		# Get script
		awrscript = self.getAWRScriptModule(script_name)
		if awrscript is None:
			return None

		# Get Routine
		for ri in range(1, awrscript.Routines.Count+1):
			if awrscript.Routines.Item(ri).Name == routine_name:
				return awrscript.Routines.Item(ri)


	def getGraphIdx(self, graph_name):

		idx = -1

		graph_name = graph_name.replace("=", "(?<!=)=(?!=)")

		# Find plot graph
		for gi in range(1, self.awrde.Project.Graphs.Count + 1):

			if bool(re.match(graph_name, self.awrde.Project.Graphs.Item(gi).Name)):
				idx = gi
				break

		return idx

	def findSchematic(self, schema_name, silent=True):

		# Check that schematic exists
		if not self.awrde.Project.Schematics.Exists(schema_name):
			self.msg(f"Cannot find required schematic '{schema_name}'.\n\nAborting.", silent=silent)
			return False
		else:
			self.msg(f"Found schematic '{schema_name}'.", silent=silent)
			return True

	def applyGoals(self, silent=True):
		''' Delete all AWR Optimizer Goals and apply the goals in self.optGoals
		to the AWR project '''

		# Clear prior goals
		self.awrde.Project.OptGoals.RemoveAll()

		# Loop over all goals and apply them
		for g in self.optGoals:
			# Add goal
			self.awrde.Project.OptGoals.AddGoal(g.circSimName, g.measName, g.comparison, g.w, g.L, g.xStart, g.xStop, g.xUnit, g.yStart, g.yStop, g.yUnit)

		self.msg(f"Successfully applied {len(self.optGoals)} optimizer goals.", silent=silent)

		return True

	def getVariableMatch(self, awrname:str):

		if awrname[0] == ":": #Expect of the form ':<NAME>'

			#Look for match of remainder of name
			idx = -1
			for index, item in enumerate(self.variables):
				if item.name == awrname[1:]:
					idx = index
					break

			if idx == -1:
				return None

			return self.variables[idx]

		elif "\\" in awrname: #Expect of the form '<schema>\<name>'

			si = awrname.find("\\")

			#Look for match of schematic and name
			idx = -1
			for index, item in enumerate(self.variables):
				if item.name == awrname[si+1:] and item.schema == awrname[0:si]:
					idx = index
					break

			if idx == -1:
				return None

			return self.variables[idx]

	def turnOffOptVariables(self):

		for ovidx in range(self.awrde.Project.Optimizer.Variables.Count, 0, -1):

			ov = self.awrde.Project.Optimizer.Variables.Item(ovidx)
			ov.Enabled = False
			#
			# # Check if optimizer variable is not listed in self.variables...
			# if any(x.name == ov.Name for x in self.variables):
			# 	# Remove if not listed
			# 	ov.Enabled = False

	def applyOptVariables(self, silent:bool=True):

		''' Applies all variables in self.variables to the AWR project '''

		# Ensure all variables are enabled for optimization (if requested)
		#
		# For each variable...
		for v in self.variables:

			# Locate schematic and equation
			eq = self.eqn(v.schema, v.disptxt)

			# Set to optimize (if requested)
			if v.optEnabled:
				eq.Optimize = True
				self.debug(f"Optimize ON for Eq. '{eq.DisplayText}'")
			else:
				self.debug(f"Optimize OFF for Eq. '{eq.DisplayText}'")
			# # Try to change value in schematic to nominal
			# ei = eq.DisplayText.find("=")
			# if ei != -1:
			# 	nv = (v.maximum + v.minimum)/2
			# 	eq.DisplayText = eq.DisplayText[0:ei] + f"={str(nv)}"

		# Run through optimizer variables and configure all
		for ovidx in range(1, self.awrde.Project.Optimizer.Variables.Count+1):

			ov = self.awrde.Project.Optimizer.Variables.Item(ovidx)

			# Check if optimizer variable is not listed in self.variables...
			if any(x.name == ov.Name for x in self.variables):
				# Remove if not listed
				self.debug(f"Removing unlisted '{ov.Name}' from optimizer list")
				ov.Enabled = False
				continue

			# Find AWRVariable matching optimizer variable
			awrv = self.getVariableMatch(ov.Name)
			if awrv is None:
				self.debug(f"Failed to find matching variable")
				return False
				#
				# Next steps:
				#	1. Replace the block below with this block (currently being written).
				#	2. Must creat 'getVariableMatch()' which mactches a variable (w/ schematic and
				#      name) to the weird format from AWR (sometimes comes with a colon. Sometimes
				#      schematic then backslash).
				#	3. Continue troubleshooting the code (const_Pout_R2.py) until the scans are
				#	   working correctly.

			# #START_REPLACE
			# idx = -1
			# for index, item in enumerate(self.variables):
			# 	if item.name == ov.Name:
			# 		idx = index
			# 		break
			# #END_REPLACE

			# Configure optimization variable
			ov.Constrained = awrv.constrained
			ov.Maximum = awrv.maximum
			ov.Minimum = awrv.minimum
			ov.Nominal = (awrv.minimum + awrv.maximum)/2

		self.msg(f"Successfully applied {len(self.variables)} optimization variables.", silent=silent)

		# Return - Great success
		return True

	def updateOptFreq(self, f, idx=-1, delta=1, silent=True):

		self.msg(f"Changing frequency to {f/1e9} GHz", silent=silent)

		# Change project frequencies (b/c otherwise optimizer will run every freq)
		self.awrde.Project.Frequencies.Clear()
		self.awrde.Project.Frequencies.AddMultiple([f])

		if idx != -1:
			# Change optimizer goal frequency
			self.awrde.Project.OptGoals(idx).xStart = f - delta
			self.awrde.Project.OptGoals(idx).xStop = f + delta
		else:
			for idx in range(1, self.awrde.Project.OptGoals.Count + 1):
				# Change optimizer goal frequency
				self.awrde.Project.OptGoals(idx).xStart = f - delta
				self.awrde.Project.OptGoals(idx).xStop = f + delta

	def setMaxIterations(self, mi:int):
		self.awrde.Project.Optimizer.MaxIterations = mi

	def runOptimizer(self, silent=True):

		# Verify optimizer is not already running
		if self.awrde.Project.Optimizer.Running:
			self.err("Cannot start optimzier because it is already running!\nAborting.", silent=silent)
			return False

		# Start optimizer
		self.awrde.Project.Optimizer.Start()

		# Wait for optimizer to finish. Print updates in the interim
		width = 0
		st = time.time()
		while self.awrde.Project.Optimizer.Running:

			num_iter = str(self.awrde.Project.Optimizer.MaxIterations)
			width = len(num_iter)

			if not silent:
				print(f"\r*** OPTIMIZER RUNNING *** (Time Elapsed: {format(round(time.time()-st, 2), '.2f').zfill(6)} s, Iteration: {str(self.awrde.Project.Optimizer.Iteration).zfill(width)}/{num_iter})", end='', flush=True)
			time.sleep(0.1)

		et = time.time()

		if not silent:
			print(f"\r*** OPTIMIZER FINISHED *** (Time Elapsed: {format(round(time.time()-st, 2), '.2f').zfill(6)} s, Iteration: {str(self.awrde.Project.Optimizer.Iteration).zfill(width)}/{self.awrde.Project.Optimizer.MaxIterations})")

		return True

	def saveOptResults(self, data, g):

		# Create output dictionary
		nd = dict()

		# Scan over each variable, save to a dictionary if optimized
		for v in self.variables:

			nom = self.optVar(":"+v.name) #TODO: This is a hack and needs a better solution!
			if nom is None:
				self.debug("Failed to locate optimization variable in save routine.")
			else:
				nd[v.rdname] = nom.Nominal
		# # Scan over each optimization variable and save to dictionary
		# for idx in range(1, self.awrde.Project.Optimizer.Variables.Count + 1):
		# 	nd[self.awrde.Project.Optimizer.Variables.Item(idx).Name] = awrde.Project.Optimizer.Variables.Item(idx).Nominal

		for idx in range(1, g.Measurements.Count + 1):
			nd[self.getMeasName(g.Measurements.Item(idx).Name)] = g.Measurements.Item(idx).TraceValues(1)

		# # Scan over each value in graph and save to dictionary
		# for idx in range(1, g.Measurements.Count + 1):
		# 	nd[g.Measurements.Item(idx).Name] = g.Measurements.Item(idx).TraceValues(1)

		data.append(nd)

	def msg(self, m:str, silent:bool=False, bold:bool=False):

		if not silent:
			if not bold:
				print(f"{self.cs}{m}")
			else:
				print(Back.WHITE+Fore.BLACK+Style.DIM+f"\t{self.cs}{m}"+Style.RESET_ALL)
		self.log.append(m)

	def err(self, m:str, silent:bool=False):

		if not silent:
			print(Fore.RED+f"{self.cse}{m}"+Style.RESET_ALL)

		self.log.append(m)

	def debug(self, m:str, silent:bool=False):

		if not silent:
			print(Fore.BLUE+Back.WHITE+f"{self.csd}{m}"+Style.RESET_ALL)

		self.log.append(m)

	def warning(self, m:str, silent:bool=False):

		if not silent:
			print(Fore.BLACK + Back.RED +f"{self.csw}" + Style.RESET_ALL + Fore.YELLOW + f"{m}"+Style.RESET_ALL)

	def printOptVars(self, loc:str="REM", indent="", rel_indent="  "):
		''' Print all optimization variables '''

		if loc.upper() == "REM" or loc.upper() == "REMOTE":

			for idx in range(1, self.awrde.Project.Optimizer.Variables.Count + 1):
				print(f"{indent}Optimization Variable {idx}:           (Remote)")
				print(f"{indent}{rel_indent}Name: {self.awrde.Project.Optimizer.Variables.Item(idx).Name}")
				print(f"{indent}{rel_indent}Enabled: {self.awrde.Project.Optimizer.Variables.Item(idx).Enabled}")
				print(f"{indent}{rel_indent}Constrained: {self.awrde.Project.Optimizer.Variables.Item(idx).Constrained}")
				print(f"{indent}{rel_indent}Max: {self.awrde.Project.Optimizer.Variables.Item(idx).Maximum}")
				print(f"{indent}{rel_indent}Min: {self.awrde.Project.Optimizer.Variables.Item(idx).Minimum}")
				print(f"{indent}{rel_indent}Nominal: {self.awrde.Project.Optimizer.Variables.Item(idx).Nominal}")
				print(f"{indent}{rel_indent}Step: {self.awrde.Project.Optimizer.Variables.Item(idx).Step}")

		else:

			for idx, v in enumerate(self.variables):

				print(f"{indent}Optimization Variable {idx}:           (Local)")
				print(f"{indent}{rel_indent}Name: {v.name}")
				print(f"{indent}{rel_indent}Read Name: {v.rdname}")
				print(f"{indent}{rel_indent}Disp Text: {v.disptxt}")
				print(f"{indent}{rel_indent}Schematic: {v.schema}")
				print(f"{indent}{rel_indent}Max: {v.maximum}")
				print(f"{indent}{rel_indent}Min: {v.minimum}")
				print(f"{indent}{rel_indent}Constrained: {v.constrained}")
				print(f"{indent}{rel_indent}Opt. Enabled: {v.optEnabled}")


	def printGoals(self, indent="", rel_indent="  "):
		''' Print all optimization goals in the MWO object `awrde`. '''

		for idx in range(1, self.awrde.Project.OptGoals.Count + 1):
			print(f"{indent}Goal {idx}:")
			self.printGoal(idx, f"{indent}{rel_indent}")

	def printGoal(self, idx, indent=""):
		'''Print the goal in index `idx` in the MWO object `awrde`. '''

		print(f"{indent}Circuit: {self.awrde.Project.OptGoals.Item(idx).CircuitName}")
		print(f"{indent}Cost: {self.awrde.Project.OptGoals.Item(idx).Cost}")
		print(f"{indent}Enable: {self.awrde.Project.OptGoals.Item(idx).Enable}")
		print(f"{indent}LVal: {self.awrde.Project.OptGoals.Item(idx).LVal}")
		print(f"{indent}Measurement: {self.awrde.Project.OptGoals.Item(idx).Measurement}")
		print(f"{indent}Measurement Name: {self.awrde.Project.OptGoals.Item(idx).MeasurementName}")
		print(f"{indent}Name: {self.awrde.Project.OptGoals.Item(idx).Name}")
		print(f"{indent}Tag: {self.awrde.Project.OptGoals.Item(idx).Tag}")
		print(f"{indent}Type: {self.awrde.Project.OptGoals.Item(idx).Type}")
		print(f"{indent}Weight: {self.awrde.Project.OptGoals.Item(idx).Weight}")
		print(f"{indent}xStart: {self.awrde.Project.OptGoals.Item(idx).xStart}")
		print(f"{indent}xStop: {self.awrde.Project.OptGoals.Item(idx).xStop}")
		print(f"{indent}yStart: {self.awrde.Project.OptGoals.Item(idx).yStart}")
		print(f"{indent}yStop: {self.awrde.Project.OptGoals.Item(idx).yStop}")

	def showAWRScripts(self, indent="", rel_indent="  ", showRoutines:bool=False):

		for gsi in range(1, self.awrde.Project.Application.GlobalScripts.Count+1):
			gsn = self.awrde.Project.Application.GlobalScripts.Item(gsi).Name
			if showRoutines:
				print(f"{indent}[{gsi}] {gsn}:")
				for gsri in range(1, self.awrde.Project.Application.GlobalScripts.Item(gsi).Routines.Count+1):
					gsrn = self.awrde.Project.Application.GlobalScripts.Item(gsi).Routines.Item(gsri).Name
					print(f"{indent}{rel_indent}({gsri}) {gsrn}")
			else:
				print(f"{indent}[{gsi}] {gsn}")
