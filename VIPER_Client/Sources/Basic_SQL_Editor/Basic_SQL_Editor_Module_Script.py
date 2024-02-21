def ModuleName():
    return "Basic_SQL_Editor"

#Import Modules
from flask import jsonify
import json
import os
from VIPER_Utility import LIMSQuery, LogOutput
os.chdir( os.path.dirname(os.path.realpath(__file__)) ) #ensure we operate in this Module's folder

#Response Script:
def Process_User_Request(request):
    """Basic SQL Editor Module: Fetches and Inserts to the Sakila MySQL Test database

    Button 0: Fetches the records of an actor from the Sakila test database
        Inputs  : 
            Textbox 2: first_name
        Outputs : 
            Label 4: All actor records with a matching first_name

    Button 1: Adds a new entry to the Sakila test database
        Inputs  : 
            Textbox 2: first_name
            Textbox 3: last_name
        Outputs : 
            Label 4: Confirmation of new actor entry 
    
    Returns: A Jsonified string
    """
    SubmissionResponse = {
        "Label 4":"An Error Has Occured",
    }

    try: #protect from request.form[name] not found and request failure
        ButtonPressed = request.form['SubmitButtonPressed']

        if ButtonPressed == "Button 0": 
            Textbox_2 = request.form.get("Textbox 2")

            Output = json.loads( LIMSQuery(request, "sakila", Textbox_2.strip(), "fetchall") )                  
            LogOutput(Output, ModuleName(), os.path.join(os.getcwd(), "Logs")) 
            SubmissionResponse = {
            "Label 4":Output,
            }


        if ButtonPressed == "Button 1": 
            Textbox_3 = request.form.get("Textbox 3") #surname
            Textbox_2 = request.form.get("Textbox 2") #name

            Output = json.loads( LIMSQuery(request, "sakila", [Textbox_2.strip(),Textbox_3.strip()], "writenew") )                  
            LogOutput(Output, ModuleName(), os.path.join(os.getcwd(), "Logs"))                                                                  

            SubmissionResponse = {
            "Label 4":json.dumps(Output),
            }

    except:
        return '', 400 #If nothing happens, return nothing
    finally:        
        return jsonify(Info=SubmissionResponse) 