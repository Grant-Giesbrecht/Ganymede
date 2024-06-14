import h5py
import time
import json
import numpy as np

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


def dict_to_hdf(root_data:dict, save_file:str, use_json_backup:bool=True) -> bool:
	''' Writes a dictionary to an HDF file per the rules used by 'write_level()'. 
	
	* If the value of a key in another dictionary, the key is made a group (directory).
	* If the value of the key is anything other than a dictionary, it assumes
	  it can be saved to HDF (such as a list of floats), and saves it as a dataset (variable).
	
	'''
	
	def write_level(fh:h5py.File, level_data:dict):
		''' Writes a dictionary to the hdf file.
		
		Recursive function used by  '''
		
		# Scan over each directory of root-data
		for k, v in level_data.items():
			
			# If value is a dictionary, this key represents a directory
			if type(v) == dict:
				
				# Create a new group
				fh.create_group(k)
				
				# Write the dictionary to the group
				write_level(fh[k], v)
					
			else: # Otherwise try to write this datatype (ex. list of floats)
				
				# Write value as a dataset
				fh.create_dataset(k, data=v)
	
	# Start timer
	t0 = time.time()
	
	# Open HDF
	hdf_successful = True
	exception_str = ""
	
	# Recursively write HDF file
	with h5py.File(save_file, 'w') as fh:
		
		# Try to write dictionary
		try:
			write_level(fh, root_data)
		except Exception as e:
			hdf_successful = False
			exception_str = f"{e}"
	
	# Check success condition
	if hdf_successful:
		print(f"Wrote file in {time.time()-t0} sec.")
		
		return True
	else:
		print(f"Failed to write HDF file! ({exception_str})")
		
		# Write JSON as a backup if requested
		if use_json_backup:
			
			# Add JSON extension
			save_file_json = save_file[:-3]+".json"
			
			# Open and save JSON file
			try:
				with open(save_file_json, "w") as outfile:
					outfile.write(json.dumps(root_data, indent=4))
			except Exception as e:
				print(f"Failed to write JSON backup: ({e}).")
				return False
		
		return True

def hdf_to_dict(filename) -> dict:
	''' Reads a HDF file and converts the data to a dictionary '''
	
	def read_level(fh:h5py.File) -> dict:
		
		# Initialize output dict
		out_data = {}
		
		# Scan over each element on this level
		for k in fh.keys():
			
			# Read value
			if type(fh[k]) == h5py._hl.group.Group: # If group, recusively call
				out_data[k] = read_level(fh[k])
			else: # Else, read value from file
				out_data[k] = fh[k][()]
				
				# Converting to a pandas DataFrame will crash with
				# some numpy arrays, so convert to a list.
				if type(out_data[k]) == np.ndarray:
						out_data[k] = list(out_data[k])
		
		return out_data
	
	# Open file
	with h5py.File(filename, 'r') as fh:
		
		try:
			root_data = read_level(fh)
		except Exception as e:
			print(f"Failed to read HDF file! ({e})")
			return None
	
	# Return result
	return root_data
	