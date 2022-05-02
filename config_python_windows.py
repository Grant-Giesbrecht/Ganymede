import sys
import os
import subprocess

# Find path to python executable
python_path = sys.executable

# Remove exe name, keep just directory path
idx = python_path.rfind('\\')
python_path = python_path[:idx]

# Pip path will be python_path/Scripts
pip_path = python_path + '\\Scripts'

print("")
print("This assumes you installed Python via Python.com, not via Anaconda, windows")
print("store, etc. and allows you to access your delightful new executables via ")
print("powershell and the command prompt.")
print("")
print("Because Windows low-key sucks, permanently adding to the path programatically")
print("is a giant nightmare. Instead of going through that hellish journey, copy")
print("and paste the two paths below and add them to the 'Path' environment variable")
print("manually.")
print("");
print("To Set Environment Variables:")
print("Type 'Environment Variable' into the windows search, enter, then click the ")
print("'environment variables' button. Under 'system variables' click Edit, and paste in")
print("the paths below.")
print("")
print("Windows Knows Better Than to Cooperate:")
print("If Windows decides to open the windows store instead of python when you type")
print("'Python' in the command line, open the app execution aliases page ('aliases'")
print("in windows search ought to do the trick), and disable the two python aliases.")
print("")
print("    ------------------- Add these to your Path: -----------------")
print("")
print(f"\tPython path:\n\t\t {python_path}")
print(f"\tPip path:\n\t\t {pip_path}\n")
print("")
print("")
print("I wish you well in the perdition infamously known as 'Coding on Windows'.")
print("")
print("")
print("                 \"You'll never take me alive!!\"")
print("                              -Windows 9x/ME/XP/Vista/8/8.1/10/11")
print("")
# os.system(f'$env:Path += ";' + python_path + '"')
# os.system(f'$env:Path += ";{pip_path}"')

# print(f'$env:Path += ";' + python_path + '"')
# print(f'$env:Path += ";' + pip_path + '"')
# os.system(f'$env:Path += ";' + python_path + '"')
# os.system(f'$env:Path += ";' + pip_path + '"')

# os.system('(dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell')
#
# # Get original path
# # os.system("$oldpath = (Get-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH).path")
# # os.system('$newpath = "$oldpath;'+python_path+';'+pip_path)
# # os.system("Set-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH -Value $newPath")
#
# lines = ["$oldpath = (Get-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH).path"]
# lines.append('$newpath = "$oldpath;'+python_path+';'+pip_path+'"')
# lines.append("Set-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH -Value $newPath")
#
# with open('add_python_to_path.ps1', 'w') as f:
#     for line in lines:
#         f.write(line)
#         f.write('\n')
#
# # x = subprocess.check_output(['(dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell'])
# x = subprocess.run(['(dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell'], capture_output=True, shell=True)
# print(f"Captured: {x}")

# print("Added to path.")
