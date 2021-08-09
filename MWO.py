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

def printGoals(awrde, indent=""):
    ''' Print all optimization goals in the MWO object `awrde`. '''
    
    for idx in range(1, awrde.Project.OptGoals.Count + 1):
        print(f"Goal {idx}")
        printGoal(awrde, idx, "    ")

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
    
    