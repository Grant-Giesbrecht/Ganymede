import h5py
import time
import json
import numpy as np
from colorama import Fore, Style
import os
import sys
import string
from typing import Dict, Any, List
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.collections import PathCollection

def locate_drive(id:str, param:str="ID", filename="drive_id.txt", silence_output:bool=False):
	''' Returns the path to a drive containing the file `filename`, 
	which contains a line defining <param>=<id>. Used to identify a
	removable harddrive connected to various systems without trying
	to hardcode drive letters, expect a specific volumne name or similar.
	'''
	
	file_contents = f"{param}={id}"
	
	def bprint(s:str, silence:bool=False):
		if silence:
			return
		else:
			print(s)
	
	def scan_drives_windows(filename, file_contents):
		matching_drives = []
		# Check all potential drive letters (A to Z)
		for drive_letter in string.ascii_uppercase:
			drive = f"{drive_letter}:\\"
			if os.path.exists(drive):
				file_path = os.path.join(drive, filename)
				if os.path.isfile(file_path):
					try:
						with open(file_path, 'r', encoding='utf-8') as file:
							for line in file:
								if line.strip() == file_contents:
									matching_drives.append(drive)
									break
					except Exception as e:
						bprint(f"Error reading {file_path}: {e}", silence=silence_output)
		return matching_drives
	
	def scan_drives_unix(filename, file_contents):
		possible_mount_points = ['/mnt', '/media', '/Volumes']
		matching_mounts = []

		for mount_root in possible_mount_points:
			if os.path.exists(mount_root):
				for entry in os.listdir(mount_root):
					mount_path = os.path.join(mount_root, entry)
					if os.path.ismount(mount_path):
						file_path = os.path.join(mount_path, filename)
						if os.path.isfile(file_path):
							try:
								with open(file_path, 'r', encoding='utf-8') as file:
									for line in file:
										if line.strip() == file_contents:
											matching_mounts.append(mount_path)
											break
							except Exception as e:
								bprint(f"Error reading {file_path}: {e}", silence=silence_output)
		return matching_mounts
	
	if sys.platform == "win32":
		drives = scan_drives_windows(filename, file_contents=file_contents)
	elif sys.platform == "darwin" or sys.platform.startswith("linux"):
		drives = scan_drives_unix(filename, file_contents=file_contents)
	else:
		bprint(f"Unknown operating system: {sys.platform}", silence=silence_output)
		return None
	
	if len(drives) == 0:
		bprint(f"{Fore.RED}No matching drives found!{Style.RESET_ALL} Looking for file {Fore.YELLOW}{filename}{Style.RESET_ALL} with contents {Fore.GREEN}{file_contents}{Style.RESET_ALL}.", silence=silence_output)
		return None
	
	drv = drives[0]
	if len(drives) == 1:
		bprint(f"{Fore.GREEN}Found matching drive!{Style.RESET_ALL} Path = {Fore.YELLOW}{drv}{Style.RESET_ALL}.", silence=silence_output)
	else:
		bprint(f"{Fore.RED}Found multiple matching drives!{Style.RESET_ALL} Returning first matched drive. Path = {Fore.YELLOW}{drv}{Style.RESET_ALL}.", silence=silence_output)
	return drv
	

def lin_to_dB(x:float, use10:bool=False):
	''' Converts a value from dB to linear units'''
	
	if use10:
		return 10*np.log10(x)
	else:
		return 20*np.log10(x)

def dB_to_lin(x:float, use10:bool=False):
	''' Converts a value from dB to linear units'''
	
	if use10:
		return 10**(x/10)
	else:
		return 10**(x/20)


# def dict_to_hdf(root_data:dict, save_file:str, use_json_backup:bool=True) -> bool:
# 	''' Writes a dictionary to an HDF file per the rules used by 'write_level()'. 
	
# 	* If the value of a key in another dictionary, the key is made a group (directory).
# 	* If the value of the key is anything other than a dictionary, it assumes
# 	  it can be saved to HDF (such as a list of floats), and saves it as a dataset (variable).
	
# 	'''
	
# 	def write_level(fh:h5py.File, level_data:dict):
# 		''' Writes a dictionary to the hdf file.
		
# 		Recursive function used by  '''
		
# 		# Scan over each directory of root-data
# 		for k, v in level_data.items():
			
# 			# If value is a dictionary, this key represents a directory
# 			if type(v) == dict:
				
# 				# Create a new group
# 				fh.create_group(k)
				
# 				# Write the dictionary to the group
# 				write_level(fh[k], v)
					
# 			else: # Otherwise try to write this datatype (ex. list of floats)
				
# 				# Write value as a dataset
# 				fh.create_dataset(k, data=v)
	
# 	# Start timer
# 	t0 = time.time()
	
# 	# Open HDF
# 	hdf_successful = True
# 	exception_str = ""
	
# 	# Recursively write HDF file
# 	with h5py.File(save_file, 'w') as fh:
		
# 		# Try to write dictionary
# 		try:
# 			write_level(fh, root_data)
# 		except Exception as e:
# 			hdf_successful = False
# 			exception_str = f"{e}"
	
# 	# Check success condition
# 	if hdf_successful:
# 		print(f"Wrote file in {time.time()-t0} sec.")
		
# 		return True
# 	else:
# 		print(f"Failed to write HDF file! ({exception_str})")
		
# 		# Write JSON as a backup if requested
# 		if use_json_backup:
			
# 			# Add JSON extension
# 			save_file_json = save_file[:-3]+".json"
			
# 			# Open and save JSON file
# 			try:
# 				with open(save_file_json, "w") as outfile:
# 					outfile.write(json.dumps(root_data, indent=4))
# 			except Exception as e:
# 				print(f"Failed to write JSON backup: ({e}).")
# 				return False
		
# 		return True

# def hdf_to_dict(filename, to_lists:bool=True) -> dict:
# 	''' Reads a HDF file and converts the data to a dictionary '''
	
# 	def read_level(fh:h5py.File) -> dict:
		
# 		# Initialize output dict
# 		out_data = {}
		
# 		# Scan over each element on this level
# 		for k in fh.keys():
			
# 			# Read value
# 			if type(fh[k]) == h5py._hl.group.Group: # If group, recusively call
# 				out_data[k] = read_level(fh[k])
# 			else: # Else, read value from file
# 				out_data[k] = fh[k][()]
				
# 				# Converting to a pandas DataFrame will crash with
# 				# some numpy arrays, so convert to a list.
# 				if type(out_data[k]) == np.ndarray and to_lists:
# 						out_data[k] = list(out_data[k])
# 				elif type(out_data[k]) == list and not to_lists:
# 						out_data[k] = np.array(out_data[k])
						
# 		return out_data
	
# 	# Open file
# 	with h5py.File(filename, 'r') as fh:
		
# 		try:
# 			root_data = read_level(fh)
# 		except Exception as e:
# 			print(f"Failed to read HDF file! ({e})")
# 			return None
	
# 	# Return result
# 	return root_data

def dict_summary(x:dict, verbose:int=0, indent_level:int=0, indent_char:str="   "):
	'''
	'''
	
	color_dict = Fore.CYAN
	color_name = Fore.GREEN
	color_lines = Fore.LIGHTBLACK_EX
	color_list_type = Fore.MAGENTA
	color_type = Fore.YELLOW
	color_value = Fore.WHITE
	color_ellips = Fore.RED
	
	lvlmarker_1 = "|"
	lvlmarker_2 = "."
	
	def get_indent(indent_level:int):
		
		indent_char0 = f" {indent_char}"
		indent_char1 = f"{lvlmarker_1}{indent_char}"
		indent_char2 = f"{lvlmarker_2}{indent_char}"
		
		indent_str = ""
		for i in range(indent_level):
			if i == 0:
				indent_str += indent_char0
			elif i % 2 == 1:
				indent_str += indent_char1
			else:
				indent_str += indent_char2
		return f"{color_lines}{indent_str}{Style.RESET_ALL}"
	
	def value_to_string(val, verbose:int, indent_level, length_limit:int=50, wrap_length:int=80):
		
		# Get full value string if verbose != 0
		if verbose == 0:
			return ""
		
		val_str = f"{val}"
		
		# If verbose == 1, truncate
		if verbose == 1:
			if len(val_str) > length_limit:
				val_str = val_str[:length_limit//2] + f"{color_ellips}...{color_value}" + val_str[-(length_limit//2-3):]
		
		# If verbose == 2, indent and print full value
		if verbose == 2:
			
			# Get length of color specifier
			cvlen = len(color_value)
			
			# Get indent char
			indent = get_indent(indent_level+1)
			indent.replace('\t', "    ")
			
			# Initialize with newline, indent and color
			if type(val) == str:
				val_str = f"\n{indent}{color_value}\"{val_str}\""
			else:
				val_str = f"\n{indent}{color_value}{val_str}"
			val_str.replace('\t', "    ")
			
			# Find last newline
			nlidx = val_str.rfind('\n')
			
			# Continue to wrap line until under length limit
			while len(val_str) - nlidx - cvlen > wrap_length:
				
				# Add newline (and color specs)
				val_str = val_str[:(nlidx)+wrap_length+cvlen] + "\n" + indent + color_value + val_str[(nlidx)+wrap_length+cvlen:]
				
				# Find new index
				nlidx = val_str.rfind('\n')
		
		else:
			# Add color to string
			if type(val) == str:
				val_str = f"{color_value}\"{val_str}\"{Style.RESET_ALL}"
			else:
				val_str = f"{color_value}{val_str}{Style.RESET_ALL}"
		
		return val_str
	
	# Scan over each key
	for k in x.keys():
		
		# IF key points to dictionary, recursive call
		if type(x[k]) == dict:
			print(f"{get_indent(indent_level)}[{color_dict}{k}{Style.RESET_ALL}]")
			dict_summary(x[k], verbose=verbose, indent_level=indent_level+1)
			
		# Otherwise print data element stats
		else:
			val = x[k]
			
			if type(val) == list:
				try:
					val0 = val[0]
				except:
					val0 = None
				
				if type(val0) == list:
					val_str = value_to_string(val, verbose, indent_level)
					print(f"{get_indent(indent_level)}{color_name}{k}{Style.RESET_ALL} = {color_list_type}{type(val)}{Style.RESET_ALL}, {len(val)} x {color_list_type}{type(val0)} {val_str}{Style.RESET_ALL}")
				else:
					val_str = value_to_string(val, verbose, indent_level)
					print(f"{get_indent(indent_level)}{color_name}{k}{Style.RESET_ALL} = {color_list_type}{type(val)}{Style.RESET_ALL}, {len(val)} x {color_type}{type(val0)} {val_str}{Style.RESET_ALL}")
			else:
				val_str = value_to_string(val, verbose, indent_level)
				print(f"{get_indent(indent_level)}{color_name}{k}{Style.RESET_ALL} = {color_type}{type(val)}{Style.RESET_ALL} {val_str}{Style.RESET_ALL}")

# From ChatGPT - for exporting data from figures to MIDAS:

def _finite_xy(x, y):
	x = np.asarray(x, dtype=float)
	y = np.asarray(y, dtype=float)
	m = np.isfinite(x) & np.isfinite(y)
	return x[m], y[m]

def _segment_bound_intersections(x0, y0, x1, y1, xlow, xhigh):
	"""Return boundary intersection points (in segment order) if the segment crosses xlow/xhigh."""
	dx = x1 - x0
	if dx == 0 or not np.isfinite(dx):
		return []
	pts = []
	for bound in (xlow, xhigh):
		# Does the segment cross this vertical line?
		if (x0 < bound and x1 > bound) or (x0 > bound and x1 < bound):
			t = (bound - x0) / dx
			if 0.0 <= t <= 1.0:
				yb = y0 + t * (y1 - y0)
				pts.append((t, bound, yb))
	# ensure in-segment order
	pts.sort(key=lambda p: p[0])
	return [(xb, yb) for _, xb, yb in pts]

def _trim_line_to_xbounds(x, y, xlow, xhigh):
	"""
	Keep all original points with x in [xlow, xhigh] and add boundary points
	where segments cross xlow/xhigh.
	"""
	x, y = _finite_xy(x, y)
	if x.size < 2:
		# nothing to interpolate; just keep if inside
		m = (x >= xlow) & (x <= xhigh)
		return x[m], y[m]

	out_x: List[float] = []
	out_y: List[float] = []

	for i in range(len(x) - 1):
		x0, y0 = x[i],   y[i]
		x1, y1 = x[i+1], y[i+1]
		x0_in = (xlow <= x0 <= xhigh)
		x1_in = (xlow <= x1 <= xhigh)

		seg_pts = []
		if x0_in:
			seg_pts.append((x0, y0))

		# add boundary intersections (0, 1 or 2), in order along the segment
		seg_pts += _segment_bound_intersections(x0, y0, x1, y1, xlow, xhigh)

		if x1_in:
			seg_pts.append((x1, y1))

		# append to output, avoiding duplicate joins
		for (xs, ys) in seg_pts:
			if not out_x or xs != out_x[-1] or ys != out_y[-1]:
				out_x.append(xs)
				out_y.append(ys)

	# Final safety filter (numeric noise, exact inclusivity)
	m = (np.asarray(out_x) >= xlow) & (np.asarray(out_x) <= xhigh)
	return np.asarray(out_x)[m], np.asarray(out_y)[m]

def extract_visible_xy(fig: Figure) -> List[Dict[str, Any]]:
	"""
	Extract X/Y data for each visible trace in a Matplotlib figure, trimmed to
	the current x-limits of each Axes.

	Returns a list of dicts, one per trace:
	  {
		'axes_index': int,           # index of the Axes in fig.get_axes()
		'type': 'line'|'scatter',
		'label': str,                # artist label
		'x': np.ndarray,             # trimmed x data
		'y': np.ndarray,             # trimmed y data
		'xlim_used': (float, float)  # x-limits applied for trimming
	  }
	"""
	results: List[Dict[str, Any]] = []
	for ax_i, ax in enumerate(fig.get_axes()):
		# Respect each axes' current x-limits; sort so bounds are [low, high]
		xmin, xmax = ax.get_xlim()
		xlow, xhigh = (xmin, xmax) if xmin <= xmax else (xmax, xmin)

		# Lines
		for line in ax.lines:
			if not line.get_visible():
				continue
			x = line.get_xdata(orig=True)
			y = line.get_ydata(orig=True)
			tx, ty = _trim_line_to_xbounds(x, y, xlow, xhigh)
			results.append({
				'axes_index': ax_i,
				'type': 'line',
				'label': line.get_label(),
				'x': tx,
				'y': ty,
				'xlim_used': (xlow, xhigh),
			})

		# Scatter collections (PathCollection)
		for col in ax.collections:
			if not col.get_visible():
				continue
			if not isinstance(col, PathCollection):
				continue
			offs = col.get_offsets()
			if offs is None or len(offs) == 0:
				continue
			offs = np.asarray(offs, dtype=float)
			if offs.ndim != 2 or offs.shape[1] != 2:
				continue
			xs = offs[:, 0]
			ys = offs[:, 1]
			xs, ys = _finite_xy(xs, ys)
			m = (xs >= xlow) & (xs <= xhigh)
			results.append({
				'axes_index': ax_i,
				'type': 'scatter',
				'label': col.get_label(),
				'x': xs[m],
				'y': ys[m],
				'xlim_used': (xlow, xhigh),
			})

	return results
