def ModuleName():
    return "Basic_Admin_Panel"

#Import Modules
from flask import jsonify
import json
import os
from VIPER_Utility import LIMSQuery, LogOutput
os.chdir( os.path.dirname(os.path.realpath(__file__)) ) #ensure we operate in this Module's folder

#Response Script:
def Process_User_Request(request):
    """Basic Admin Panel Module: Provides basic Administration functions

    Button 0: Gets the permission groups associated with the input UserID
        Inputs  : 
            Textbox 2: UserID
        Outputs : 
            Label 4: Corresponding permission groups

    Button 1: Sets the permission groups of the input UserID
        Inputs  : 
            Textbox 2: UserID
            Textbox 3: Permission Groups in the format:  Scientist, Senior Scientist, Administrator, etc
        Outputs : 
            Label 4: Confirmation of new User permissions
    
    Returns: A Jsonified string
    """

    SubmissionResponse = f"A Python error has occured in {ModuleName()}_Module_Script.py"
    try: #protect from request.form[name] not found and request failure
        ButtonPressed = request.form['SubmitButtonPressed']
        
        if ButtonPressed == "Button 0": 
            
            Textbox_2 = request.form.get("Textbox 2") 

             #WRITE CODE HERE
            Output = json.loads( LIMSQuery(request, False, Textbox_2.strip(), "checkuser") )                   #example backend SQL request
            LogOutput(Output, ModuleName(), os.path.join(os.getcwd(), "Logs"))                                                #example log result 

            SubmissionResponse = {
            "Label 4":Output,
            }

        if ButtonPressed == "Button 1": 
            Textbox_2 = request.form.get("Textbox 2")
            Label_4 = request.form.get("Label 4")
            Textbox_3 = request.form.get("Textbox 3") #FORMAT:  "Senior Scientist", "Scientist", "Etc"

            ListifiedTextbox_3 = '"'+Textbox_3.strip().replace(", ", ',').replace(",", '","')+'"' #lazy conversion
            jsonifiedTextbox_3 =  json.loads( r'{"tx3info":['+ListifiedTextbox_3+"]}" )
            NewUserID = Textbox_2.strip()
            NewUserPermissions = jsonifiedTextbox_3["tx3info"]

            print("New User Permissions:", [NewUserID, NewUserPermissions])
            Output = json.loads( LIMSQuery(request, False,  [NewUserID, NewUserPermissions], "updateuser") )                   #example backend SQL request
            LogOutput(Output, ModuleName(), os.path.join(os.getcwd(), "Logs"))                                                                 #example log result 

            SubmissionResponse = {
            "Label 4":Output,
            }

    except:
        return '', 400 #If nothing happens, return nothing
    finally:        
        return jsonify(Info=SubmissionResponse) 