#include <iostream>
#include <stdio>
#include <vector>
#include <string>
#include <stdlib.h>

typedef struct{
	std::string flag;
	std::string command;
	std::string help_msg;
}cmdflg;

using namespace std;

void print_help(vector<cmdflg> flags);

int main(int argc, char** argv){
	
	// Create library of commands
	vector<cmdflg> flags;
	
	// Create flags
	cmdflg nf;
	nf.flag = "optimizer_end"
	nf.command = "python C:\\Users\\grant\\Documents\\GitHub\\Ganymede\\Scripts\\AWR Scripts\\Design Tools\\alert_end_of_optimizer.py"
	nf.help_msg = "Plays an alert sound when the AWR optimizer finishes."
	flags.push_back(nf);
	
	
	// Check for no arguments case
	if (argc < 2){
		print_help();
	}
	
	// Check for help request
	if (strcmp(argv[1], "-h") == 0 || strcmp(argv[1], "-help") == 0){
			print_help();
	}
	
	bool found;
	
	// Scan over all input flags
	for (size_t i = 1 ; i < argc ; i++){
		
		found = false;
		
		// Scan over all listed flags
		for (size_t f = 0 ; f < flags.size() ; f++){
		 	
			// Flag was found
			if (strcmp(flags[f].flag, argv[i]) == 0){
				system(flags[f].command); // Run command
				found = true; // Mark as found
				break; // Quit inner loop
			}
		}
		
		// Check for error
		if (!found){
			cout << "ERROR: Failed to recognize flag '" << argv[i] << "'. Skipping." << endl;
		}
	}
	
	return 0;
}


void print_help(vector<cmdflg> flags){
	
	cout << "PyTools Help" << endl;
	
}
