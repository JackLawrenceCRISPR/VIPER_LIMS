##The following code is an example of an SQL Module, works with the Sakila databse from MySql workbench database
#TODO: Make a default VIPER Package .py set of defined functions which ALL VIPER_Modules can import, which remain consistent between all versions
def LIMSReferralName():
    """Returns the name of your module to be used on every button, the module's /domain name, etc
    Returns:
        str: A unique, short, recognisable name for your module
    """
    RefName = "Boa Constructor"                        #Name your module
    return RefName.strip().replace(" ", "_")

#Import Modules
from flask import request, render_template, Blueprint, redirect
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sys
import json
import ast

#Define Cookie access
def VIPER_DecodeLoginCookie(LoginCookieText):
    """Extract User information from a VIPER browser cookie

    Args:
        LoginCookieText (str): A VIPER_Cookie from a web browser session containing User Information compressed into a single string
        
    Returns:
        dict: A dictionary containing the Cookie information (Server, Token, PublicKey, Certificate, LocalIPAddress) 
    """
    if LoginCookieText is None:
        raise ValueError("No VIPER Cookie found, please login")
    
    VIPER_CookieUserInfo = []
    for x in range(0,3):    #LOOPS 1-4 loops 3 times, cycle 4 DOESNT occur?
        VIPER_CookieUserInfo.append(LoginCookieText[:LoginCookieText.find("|")])
        LoginCookieText = LoginCookieText[LoginCookieText.find("|")+1:]
    return{ "Server" : VIPER_CookieUserInfo[0],
           "Token" : VIPER_CookieUserInfo[1],
           "NEVER_SHARE_SharedFernetKey" : (VIPER_CookieUserInfo[2]).encode(),
           "LocalIPAddress": LoginCookieText[:LoginCookieText.find("|")] 
           }

##Module pages 
Module_Page = Blueprint(LIMSReferralName(), __name__, template_folder=os.getcwd())



## V MAKE YOUR MODULE DOWN HERE V
@Module_Page.route("/"+LIMSReferralName(), methods = ["POST", "GET"])
def ModuleHomepage():
    """Generates a homepage for the module

    Returns:
        str: Webpage in HTML format
    """
    #coookie = decodecookie
    #if no cookie then: render "Access Denied" template, with redirect to login page
    #else:
    return render_template("BoaConstructorHome_Homepage.html", LIMSRef=LIMSReferralName(), LocalIPAddress=VIPER_DecodeLoginCookie(request.cookies.get('VIPER_LocalUserInfo'))["LocalIPAddress"] )
       
@Module_Page.route("/"+LIMSReferralName()+"/InduceButton", methods=['POST'])
def InduceButtonPageExample():
    """Handles the JQuery POST requests from Search and buttons on the module's homepage

    Returns:
        dict: A JSONified response from the SQL database containing the Query constructed in the Search bar on the homepage 
    """

    RawBuildObject = request.form.get("siteobject")

    ObjectBuild = False 
    if len(RawBuildObject) > 10:
        ObjectBuild = RawBuildObject.replace(r"%22",'"').replace(r"%20"," ").replace(r"%3D","=") .replace(r"%3C","<").replace(r"%3E",">")
        #.replace(r"%3D",r'=').replace(r'\"',r'"') #.replace(r"%22",r'"').replace(r"%3C",r'<').replace(r"%2F",r'/').replace(r"%3E",r'>').replace(r"%3A+",r':').replace(r";+",r';')
    NewModuleName = ObjectBuild[:ObjectBuild.find("NAMEENDSHERE")]
    #print(NewModuleName)
    OriginalCWD = os.path.dirname(os.path.realpath(__file__))
    os.chdir(OriginalCWD)
    if 1==1: #"Boa_Constructor_Converter" not in sys.modules:
        if os.path.exists(os.path.join(os.getcwd(),"Sources")):
            os.chdir("Sources")
        if os.path.exists(os.path.join(os.getcwd(),"Boa_Constructor")):
            os.chdir("Boa_Constructor")
        if os.path.exists(os.path.join(os.getcwd(),"Boa_Sources")):
            os.chdir("Boa_Sources")
        sys.path.append(os.getcwd())
        import Boa_Constructor_Converter
    if not ObjectBuild:
        ObjectBuild = os.getcwd() #try to recover if send contains nothing
    NewModule = Boa_Constructor_Converter.ConstructVIPERModule(NewModuleName.replace(" ","_"),ObjectBuild)
    os.chdir(OriginalCWD)
    return ("Module complete, find at /VIPER/Sources/"+NewModuleName.replace(" ","_"))
    return redirect(VIPER_DecodeLoginCookie(request.cookies.get('VIPER_LocalUserInfo'))["LocalIPAddress"], code=302) #f'strings' can contain {variables}
