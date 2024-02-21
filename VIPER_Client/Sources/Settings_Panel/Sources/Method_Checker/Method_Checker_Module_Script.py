def ModuleName():
    return "Method_Checker"

#Import Modules
from flask import jsonify
import json
import os
from VIPER_Utility import LIMSQuery, LogOutput
os.chdir( os.path.dirname(os.path.realpath(__file__)) ) #ensure we operate in this Module's folder

#Response Script:
def Process_User_Request(request):
    """Method Checker Module: Provides the user with a VIPER_Server Methods which can be used in LIMSQuery requests for interacting with VIPER_Server SQL data.
    Only Methods which align with the User's Permission Groups are retrieved.

    Button 0: Gets a list of VIPER_Server Methods
        Inputs  : 
            Textbox 1: The Name of a VIPER_Server Method. Leave empty to return a list of all available Methods.
        Outputs : 
            Label 2: A description of the VIPER_Server Methods, including Inputs and Outputs.

    Returns: A string containing the VIPER_Server Methods
    """
    try: 
        ButtonPressed = request.form['SubmitButtonPressed']

        if ButtonPressed == "Button 0": 
            Textbox_1 = request.form.get("Textbox 1")

            if Textbox_1:
                Output = json.loads( LIMSQuery(request, False, str(Textbox_1), "GetMethod") )                   
            else:
                Output = json.loads( LIMSQuery(request, False, False, "GetMethod") )                   

            LogOutput(Output, ModuleName(), os.path.join(os.getcwd(), "Logs"))                                                                  

            SubmissionResponse = {
            "Label 2":Output,
            }

    except:
        return '', 400 #If nothing happens, return nothing
    finally:        
        return jsonify(Info=SubmissionResponse) 