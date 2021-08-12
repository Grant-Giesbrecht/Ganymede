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

def printOptVars(awrde, indent="", rel_indent="  "):
	''' Print all optimization variables '''

	for idx in range(1, awrde.Project.Optimizer.Variables.Count + 1):
		print(f"{indent}Variable {idx}:")
		print(f"{indent}{rel_indent}Name: {awrde.Project.Optimizer.Variables.Item(idx).Name}")
		print(f"{indent}{rel_indent}: {awrde.Project.Optimizer.Variables.Item(idx).Enabled}")
		print(f"{indent}{rel_indent}: {awrde.Project.Optimizer.Variables.Item(idx).Constrained}")
		print(f"{indent}{rel_indent}: {awrde.Project.Optimizer.Variables.Item(idx).Maximum}")
		print(f"{indent}{rel_indent}: {awrde.Project.Optimizer.Variables.Item(idx).Minimum}")
		print(f"{indent}{rel_indent}: {awrde.Project.Optimizer.Variables.Item(idx).Nominal}")
		print(f"{indent}{rel_indent}: {awrde.Project.Optimizer.Variables.Item(idx).Step}")

def printGoals(awrde, indent="", rel_indent="  "):
    ''' Print all optimization goals in the MWO object `awrde`. '''

    for idx in range(1, awrde.Project.OptGoals.Count + 1):
        print(f"{indent}Goal {idx}:")
        printGoal(awrde, idx, f"{indent}{rel_indent}")

def printGoal(awrde, idx, indent=""):
    '''Print the goal in index `idx` in the MWO object `awrde`. '''

    print(f"{indent}Circuit: {awrde.Project.OptGoals.Item(idx).CircuitName}")
    print(f"{indent}Cost: {awrde.Project.OptGoals.Item(idx).Cost}")
    print(f"{indent}Enable: {awrde.Project.OptGoals.Item(idx).Enable}")
    print(f"{indent}LVal: {awrde.Project.OptGoals.Item(idx).LVal}")
    print(f"{indent}Measurement: {awrde.Project.OptGoals.Item(idx).Measurement}")
    print(f"{indent}Measurement Name: {awrde.Project.OptGoals.Item(idx).MeasurementName}")
    print(f"{indent}Name: {awrde.Project.OptGoals.Item(idx).Name}")
    print(f"{indent}Tag: {awrde.Project.OptGoals.Item(idx).Tag}")
    print(f"{indent}Type: {awrde.Project.OptGoals.Item(idx).Type}")
    print(f"{indent}Weight: {awrde.Project.OptGoals.Item(idx).Weight}")
    print(f"{indent}xStart: {awrde.Project.OptGoals.Item(idx).xStart}")
    print(f"{indent}xStop: {awrde.Project.OptGoals.Item(idx).xStop}")
    print(f"{indent}yStart: {awrde.Project.OptGoals.Item(idx).yStart}")
    print(f"{indent}yStop: {awrde.Project.OptGoals.Item(idx).yStop}")


def runOptimizer(awrde):

	if awrde.Project.Optimizer.Running:
		print("Cannot start optimzier because it is already running!\nAborting.")
		sys.exit()

	awrde.Project.Optimizer.Start()

	st = time.time()
	while awrde.Project.Optimizer.Running:

		num_iter = str(awrde.Project.Optimizer.MaxIterations)
		width = len(num_iter)

		print(f"\r*** OPTIMIZER RUNNING *** (Time Elapsed: {format(round(time.time()-st, 2), '.2f').zfill(6)} s, Iteration: {str(awrde.Project.Optimizer.Iteration).zfill(width)}/{num_iter})", end="")
		time.sleep(0.1)

	et = time.time()
	print(f"\r*** OPTIMIZER FINISHED *** (Time Elapsed: {format(round(time.time()-st, 2), '.2f').zfill(6)} s, Iteration: {str(awrde.Project.Optimizer.Iteration).zfill(width)}/{awrde.Project.Optimizer.MaxIterations})")

def updateOptFreq(awrde, f, idx=1, delta=1):

	print(f"-> Changing frequency to {f/1e9} GHz")

	# Change project frequencies (b/c otherwise optimizer will run every freq)
	awrde.Project.Frequencies.Clear()
	awrde.Project.Frequencies.AddMultiple([f])

	# Change optimizer goal frequency
	awrde.Project.OptGoals(idx).xStart = f - delta
	awrde.Project.OptGoals(idx).xStop = f + delta

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
