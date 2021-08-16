from pyddf import *

def barstr(text:str, width:int=80, bc:str='*', pad:bool=True):

		s = text;

		# Pad input if requested
		if pad:
			s = " " + s + " ";

		pad_back = False;
		while len(s) < width:
			if pad_back:
				s = s + bc
			else:
				s = bc + s
			pad_back = not pad_back

		return s

def barprint(text:str, width:int=80, bc:str='*', pad:bool=True):

	print(barstr(text, width, bc, pad))

def dictList_to_ddf(dl):

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

	# Initialize interim dictionary
	interim = {key: [] for key in keys}

	# Scan over each input dictionary
	for d in dl:
		# Scan over each key
		for k in keys:
			interim[k].append(d[k])

	for k in keys:
		ddf.add(interim[k], makeValidName(k), "")

	return ddf
