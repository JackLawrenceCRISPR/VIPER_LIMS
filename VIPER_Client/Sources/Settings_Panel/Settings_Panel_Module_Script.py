def ModuleName():
    return "Settings_Panel"

#Import Modules
from flask import jsonify
import json
import os
from VIPER_Utility import LIMSQuery, LogOutput
os.chdir( os.path.dirname(os.path.realpath(__file__)) ) #ensure we operate in this Module's folder


#Response Script:
def Process_User_Request(request,LIMSPreRoute,LIMSReferralName):
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
            RedirectTo = f"{LIMSPreRoute}{LIMSReferralName}/Boa_Constructor"
        elif ButtonPressed == "Button 1": 
            RedirectTo = f"{LIMSPreRoute}{LIMSReferralName}/Method_Checker"
        elif ButtonPressed == "Button 2": 
            RedirectTo = f"{LIMSPreRoute}{LIMSReferralName}/Basic_Admin_Panel"
        elif ButtonPressed == "Button 3": 
            RedirectTo = f"{LIMSPreRoute}{LIMSReferralName}/Module_Toggler"
        elif ButtonPressed == "Button 4": 
            RedirectTo = f"{LIMSPreRoute}{LIMSReferralName}/Local_Settings"
        elif ButtonPressed == "Button 5": 
            RedirectTo = "/logout" #logout is unique!
        SubmissionResponse = {
            "RedirectTo":RedirectTo
        }

    except:
        return jsonify(Info={"RedirectTo":"None"}) 
    finally:        
        return jsonify(Info=SubmissionResponse) 