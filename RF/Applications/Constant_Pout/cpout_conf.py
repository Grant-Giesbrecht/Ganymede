# This script will assume that the MWO project it's being used with has no other
# functions.
#
# Created on 9-8-2021
# G. Giesbrecht


# Import Modules
from MWO import *
from matplotlib import pyplot as plt
from numpy import *
import MWO

# Initialize connection to Microwave Office
import win32com.client
awrde = win32com.client.Dispatch("MWOApp.MWOffice")
print(awrde)


# Create Goals
#
# Example output:
# 	Goal 2
# 	    Circuit: Schema1
# 	    Cost: 0.0
# 	    Enable: True
# 	    LVal: 2.0999999046325684
# 	    Measurement: <COMObject <unknown>>
# 	    Measurement Name: Schema1:DB(|S(1,1)|)
# 	    Name: Schema1:Schema1:DB(|S(1,1)|)<1 [w=1.5, L=2.1, Range=8e+09..1.2e+10]
# 	    Tag:
# 	    Type: 1
# 	    Weight: 1.5
# 	    xStart: 8000000000.0
# 	    xStop: 12000000000.0
# 	    yStart: 1.0
# 	    yStop: 1.0

# Start from a clean slate
awrde.Project.OptGoals.RemoveAll()

# Create optimizer goal
w = 1
L = 2
xStart = 7.99e9
xStop = 8.01e9
yStart = 1
yStop = 1
xUnit = MWO.mwUT_Frequency
yUnit = MWO.mwUT_Frequency
og = awrde.Project.OptGoals.AddGoal("Schema1", "Schema1:DB(|S(1,1)|)", MWO.mwOGT_LessThan, w, L, xStart, xStop, xUnit, yStart, yStop, yUnit)
