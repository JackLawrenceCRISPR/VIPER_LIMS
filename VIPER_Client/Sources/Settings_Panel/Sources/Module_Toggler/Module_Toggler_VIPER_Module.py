#Import Modules
from flask import request, jsonify, render_template, Blueprint
import json
import os
import glob
#Import universal VIPER_Utility module
import sys
sys.path.append(os.path.join(os.environ["VIPER_LIMS_SRC_DIR"],"VIPER"))
import VIPER_Utility
os.chdir( os.path.dirname(os.path.realpath(__file__)) ) #ensure we operate in this Module's folder

LIMSPreRoute = VIPER_Utility.GetExtensionPath(os.path.dirname(os.path.realpath(__file__)))
def LIMSReferralRoute():
    return LIMSPreRoute

def LIMSReferralName():
    return "Module_Toggler"
   
##Module pages 
Module_Page = Blueprint(LIMSPreRoute+LIMSReferralName(), __name__, template_folder=os.path.dirname(os.path.realpath(__file__)), static_folder=os.path.join(os.path.dirname(os.path.realpath(__file__)), "Static"), static_url_path="/"+LIMSPreRoute+LIMSReferralName()+"/Static")

def GetHighestSources(myFolder):
    os.chdir(myFolder)
    if os.path.basename(os.getcwd()) == "Sources":
        os.chdir("..")
        os.chdir("..")
        if os.path.basename(os.getcwd()) == "Sources":
            return GetHighestSources(os.getcwd()) #climb to highest sources!
        else:
            return myFolder
    else:
        os.chdir("..")
        if os.path.basename(os.getcwd()) == "Sources":
            return GetHighestSources(os.getcwd())
        else:
            print("Cannot find any sources...")
            return myFolder

def GetListOfViperModules(DetectedModuleList:list, ScanDir:str=False): 
    originaldir = os.getcwd() 
    if ScanDir:
        os.chdir(ScanDir)
    else:
        os.chdir(GetHighestSources(os.path.dirname(os.path.realpath(__file__))))
    
    if not os.path.exists(ScanDir):
        return
    ScanDir = os.getcwd()
    for MF in [MF for MF in list(filter(os.path.isdir, os.listdir(os.getcwd()))) if len( glob.glob( os.path.join(MF, "*_VIPER_Module.py") ) )>0]: # :^)
        #Import each module as an entry in a table
        FMF = os.path.join(os.getcwd(), MF)
        MFFile = (glob.glob(os.path.join(FMF,"*_VIPER_Module.py")))[0] #Get the first instance of VIPER_Module_*.py  
        if os.path.exists(MFFile):
            DetectedModuleList.append([MFFile,os.path.basename(MFFile),not os.path.exists(os.path.join(MF,"INACTIVE")),not os.path.exists(os.path.join(MF,"UNLISTED"))])  #get module states 
            if os.path.exists(os.path.join(FMF,"Sources")):
                GetListOfViperModules(DetectedModuleList, os.path.join(FMF,"Sources"))
        os.chdir(ScanDir)
    os.chdir(originaldir)
    return DetectedModuleList


# 


@Module_Page.route("/"+LIMSPreRoute+LIMSReferralName(), methods = ["POST", "GET"])
def ModuleHomepage():
    """Generates a homepage for the module

    Returns:
        str: Webpage in HTML format
    """
    #coookie = decodecookie
    #if no cookie then: render "Access Denied" template, with redirect to login page
    #else:

    #Imports a list of VIPER-LIMS Modules and Names
    #Imports the VIPER_Module_X.py in every Module folder in Sources which contains one
    global DeterminedListOfVIPERModules
    DeterminedListOfVIPERModules = GetListOfViperModules([])
    DetectedModuleListHTMLified = ""
    for m in DeterminedListOfVIPERModules:
        #m = [module, active?, listed?] # TRUE = Active/Listed, FALSE = Inactive/Unlisted
        mName = m[1][:-16].replace("_"," ") #remove _VIPER_Module.py from the end, replace _ with spaces

        ActiveChecked = ""
        if m[2]:
            ActiveChecked = "checked"
        ListedChecked = ""
        if m[3]:
            ListedChecked = "checked"
        DetectedModuleListHTMLified += f"""<li style="line-height: 0px;"><p style="display:inline-block;max-width: 150px; min-width: 150px;" class="VIPER-MTBtn">{mName}</p>  <input style="display:inline-block;" type="checkbox" class="ClickToggler ActiveToggler" value="Active" {ActiveChecked}> <p style="display:inline-block; white-space:pre;">           </p> <input style="display:inline-block;" type="checkbox" class="ClickToggler ListedToggler" value="Listed" {ListedChecked}> </li> 
        """
        
    return render_template("Module_Toggler_Homepage.html", LIMSRef=LIMSReferralName(), LIMSPreRoute=LIMSPreRoute, VIPERModuleLister=DetectedModuleListHTMLified, LocalIPAddress=VIPER_Utility.VIPER_DecodeLoginCookie(request.cookies.get('VIPER_LocalUserInfo'))["LocalIPAddress"] )
       
    
@Module_Page.route("/"+LIMSPreRoute+LIMSReferralName()+"/InduceButton", methods=['POST'])
def InduceButtonPageExample():
    """Handles the JQuery POST requests sent by buttons in the module
    Toggles the state of module activity or listing. 

    Returns:
        dict: A JSONified response from the users module 
    """

    #Label 1 = [hidden] Module Path
    #Label 2 = [hidden] State
    #Label 3 = Response to user

    SubmissionResponse = {
    "Label 3":"Processing Failed",
    }


    ToggleInfo = request.form["toggleinfo"]
    MyModuleState = int(request.form["togglestate"]) > 0
    ToggleIdentity = request.form["toggleidentity"][13:] # removes "ClickToggler "
    
    #<a href="#" class="VIPER-MTBtn">Basic Admin Panel</a>  <input type="checkbox" class="ActiveToggler ClickToggler" value="Active"> <input type="checkbox" class="ListedToggler ClickToggler" value="Listed" checked=""> 
    MyText = "No Change"

    NameStart =ToggleInfo.find("""VIPER-MTBtn""")
    TogglerModuleNameRaw =  ToggleInfo[NameStart:][ToggleInfo[NameStart:].find(">")+1:]
    TogglerModuleNameRaw = TogglerModuleNameRaw[:TogglerModuleNameRaw.find("</p>  ")]

    #print(TogglerModuleNameRaw)
    ModuleDirectory = False
    global DeterminedListOfVIPERModules
    
    for M in DeterminedListOfVIPERModules:
        if M[1].find(TogglerModuleNameRaw.strip().replace(" ","_")+r"_VIPER_Module.py")>-1:
            ModuleDirectory= os.path.dirname(M[0])
            break

    oldwd = os.getcwd()
    #These just write or delete files called INACTIVE or UNLISTED depending on which checkbox was toggled
    if ToggleIdentity == "ActiveToggler" and not MyModuleState:
        if not os.path.exists(os.path.join(ModuleDirectory,"INACTIVE")):
            os.chdir(ModuleDirectory)
            with open("INACTIVE","w") as INACTIVEF:
                INACTIVEF.write("INACTIVE")
        MyText = f"{TogglerModuleNameRaw} is now inactive"

    elif ToggleIdentity == "ActiveToggler" and MyModuleState:
        if os.path.exists(os.path.join(ModuleDirectory,"INACTIVE")):
            os.remove(os.path.join(ModuleDirectory,"INACTIVE"))
        MyText = f"{TogglerModuleNameRaw} is now active"

    elif ToggleIdentity == "ListedToggler" and not MyModuleState:
        if not os.path.exists(os.path.join(ModuleDirectory,"UNLISTED")):
            os.chdir(ModuleDirectory)
            with open("UNLISTED","w") as UNLISTEDF:
                UNLISTEDF.write("UNLISTED")
        MyText = f"{TogglerModuleNameRaw} is now unlisted"

    elif ToggleIdentity == "ListedToggler" and MyModuleState:
        if os.path.exists(os.path.join(ModuleDirectory,"UNLISTED")):
            os.remove(os.path.join(ModuleDirectory,"UNLISTED"))
        MyText = f"{TogglerModuleNameRaw} is now listed"
    os.chdir(oldwd)

    SubmissionResponse = {
    "Label 3":MyText,
    }    
    return jsonify(Info=SubmissionResponse) 



if __name__=="__main__":
    import glob
    Filename = os.path.basename(__file__)
    CorrectFilename = LIMSReferralName()+"_VIPER_Module.py"
    if not Filename == CorrectFilename:
        os.rename(Filename, CorrectFilename)
        print("Main file renamed with Reference name")

MyRefName = LIMSReferralName()
