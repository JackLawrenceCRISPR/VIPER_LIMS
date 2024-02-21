#Import Modules
from flask import request, jsonify, render_template, Blueprint
import json
import os
#Import universal VIPER_Utility module
import VIPER_Utility
os.chdir( os.path.dirname(os.path.realpath(__file__)) ) #ensure we operate in this Module's folder
import Settings_Panel_Module_Script #import user script

def LIMSReferralName():
    return Settings_Panel_Module_Script.ModuleName().strip().replace(" ", "_")

##Module pages 
Module_Page = Blueprint(LIMSReferralName(), __name__, template_folder=os.getcwd())

@Module_Page.route("/"+LIMSReferralName(), methods = ["POST", "GET"])
def ModuleHomepage():
    """Generates a homepage for the module

    Returns:
        str: Webpage in HTML format
    """
    #coookie = decodecookie
    #if no cookie then: render "Access Denied" template, with redirect to login page
    #else:
    return render_template("Settings_Panel_Homepage.html", LIMSRef=LIMSReferralName(), LocalIPAddress=VIPER_Utility.VIPER_DecodeLoginCookie(request.cookies.get('VIPER_LocalUserInfo'))["LocalIPAddress"] )
       
       
@Module_Page.route("/"+LIMSReferralName()+"/InduceButton", methods=['POST'])
def InduceButtonPageExample():
    """Handles the JQuery POST requests sent by buttons in the module

    Returns:
        dict: A JSONified response from the users module 
    """
    return Settings_Panel_Module_Script.Process_User_Request(request)

if __name__=="__main__":
    import glob
    Filename = os.path.basename(__file__)
    CorrectFilename = LIMSReferralName()+"_VIPER_Module.py"
    if not Filename == CorrectFilename:
        os.rename(Filename, CorrectFilename)
        print("Main file renamed with Reference name")