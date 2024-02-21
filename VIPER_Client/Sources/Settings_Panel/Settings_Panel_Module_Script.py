def ModuleName():
    return "Settings_Panel"

#Import Modules
from flask import jsonify
import json
import os
from VIPER_Utility import LIMSQuery, LogOutput
os.chdir( os.path.dirname(os.path.realpath(__file__)) ) #ensure we operate in this Module's folder


#Response Script:
def Process_User_Request(request):
    """Settings Panel Module: Allows easy access to the Settings Sub-modules.

    Button 0: Redirects to the Boa Constructor module \n
    Button 1: Redirects to the Method Checker module \n
    Button 2: Redirects to the Basic Admin Panel module \n
    Button 3: Redirects to the Module Toggler module \n
    Button 4: Redirects to the Local Settings module \n
    Button 5: A Logout button which both sends a logout request to the VIPER_Server and kills this VIPER_Client by killing the process ID 
    The VIPER_Server will destroy the encyption key used to communicate with the user during the Logout request, which is intended to prevent the misuse of login tokens which could be compromised at a later date.


    Returns: A URL to which the Client is Redirected
    """
    try: 
        ButtonPressed = request.form['SubmitButtonPressed']

        RedirectTo = "None"
        if ButtonPressed == "Button 0": 
            RedirectTo = "Boa_Constructor"
        if ButtonPressed == "Button 1": 
            RedirectTo = "Method_Checker"
        if ButtonPressed == "Button 2": 
            RedirectTo = "Basic_Admin_Panel"
        if ButtonPressed == "Button 3": 
            RedirectTo = "Module_Toggler"
        if ButtonPressed == "Button 4": 
            RedirectTo = "Local_Settings"
        if ButtonPressed == "Button 5": 
            RedirectTo = "logout"
        SubmissionResponse = {
            "RedirectTo":RedirectTo
        }

    except:
        return jsonify(Info={"RedirectTo":"None"}) 
    finally:        
        return jsonify(Info=SubmissionResponse) 