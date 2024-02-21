#Import Modules
from datetime import datetime 
import requests
import json
from cryptography.fernet import Fernet
import os
import runpy
import glob
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Define encryption / decryption functions
def VIPER_Encrypt(Message, NEVER_SHARE_SharedFernetKey):
    """Symmetrical Fernet encryption using the Shared Secret between the VIPER_Client and VIPER_Server
    Assuming the Fernet Key is not compromised, the Client and Server can privately exchange information without interception.

    Args:
        Message (str/bytes): The message to be encrypted

    Returns:
        bytes: A Fernet encrypted message, which only the VIPER_Client and VIPER_Server should be able to decrypt
    """
    if not type(Message) == type(b"b"):
        Message = Message.encode()
    return ((Fernet(NEVER_SHARE_SharedFernetKey)).encrypt( Message ))

def VIPER_Decrypt(EncryptedMessage, NEVER_SHARE_SharedFernetKey):
    """Symmetrical Fernet encryption using the Shared Secret between the VIPER_Client and VIPER_Server
    Assuming the Fernet Key is not compromised, the Client and Server can privately exchange information without interception.

    Args:
        EncryptedMessage (bytes): The encrypted message to be decrypted

    Returns:
        str: A plain text decrypted message, presumably information privately given by the VIPER_Server
    """
    if EncryptedMessage==str(EncryptedMessage):
        EncryptedMessage = EncryptedMessage.encode()
    return ((Fernet(NEVER_SHARE_SharedFernetKey)).decrypt( EncryptedMessage )).decode()

#Define saving Log files
def LogOutput(Output:str,LIMSReferralName="Unknown Module",Log_Directory:str="Default"):
    """Logs a piece of information in a .log file

    Args:
        Output (str): Information which will be the contents of the generated .log file
        Log_Directory (str, optional): Specified folder for log file storage. Defaults to os.getcwd()+r"\Logs".

    Returns:
        str: The OS.dir path to the generated log file named: DD-MM-YY__hh-mm-ss-ms_M-(ModuleName)
    """

    if Log_Directory == "Default":
        OriginalCwd = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)) ))
        os.chdir("..")
        os.chdir("..")
        Log_Directory =os.path.join(os.getcwd(),"Logs")
        os.chdir(OriginalCwd)

    if not os.path.exists(Log_Directory):
        os.makedirs(Log_Directory)
    NowTime = datetime.now()
    Today = datetime.today().strftime("%x").replace("/","-") 
    ReadMicroseconds = NowTime.strftime("%f")
    ReadTime = NowTime.strftime("%X")
    ReadTime = ReadTime.replace(":","-")
    LogFileName = f"{Today}_Logs" #10th of a microsecond
    #Create Log File in directroy, and write statement
    LogFilePath = os.path.join(Log_Directory,f"{LogFileName}.log")
    if os.path.exists(LogFilePath):
        with open(LogFilePath, 'a') as LogFile:
            LogFile.write(f"\nD{Today}T{ReadTime}{ReadMicroseconds[0:2]}M{LIMSReferralName}_!Dump:"+json.dumps(Output))  #to autofetch logs go line by line and find first instance of "LM"
    else:
         with open(LogFilePath, 'w') as LogFile:
            LogFile.write(f"D{Today}T{ReadTime}{ReadMicroseconds[0:2]}M{LIMSReferralName}_!Dump:"+json.dumps(Output))
    print("Logged to " + LogFilePath)
    return LogFilePath



def GetExtensionPath(StartingDir):
    #StartingDir should be the __File__ directory of your submodule

    #Go to Starting Dir
    OriginalCWD = os.getcwd()
    os.chdir(StartingDir)
    ModulesFound = True
    CurrentExtensionPath = ""

    TreeSourcesFolder = ""
    while ModulesFound: #climb up until we have no more Parent VIPER_Modules
        os.chdir("..")  #up to Sources
        TreeSourcesFolder = os.getcwd()
        os.chdir("..")  #up to Parent module
        FMF = os.getcwd()   #Parent Module dir
        MFFile = None
        MFFileList = glob.glob(os.path.join(FMF,"*_VIPER_Module.py")) #Get the first instance of VIPER_Module_*.py  
        if len(MFFileList)>0:
            MFFile = MFFileList[0]
            if os.path.exists(MFFile):
                modglobals = runpy.run_path(MFFile, init_globals=None, run_name="GetRefName")
                CurrentExtensionPath = modglobals["MyRefName"]+r"/"+CurrentExtensionPath    #add parent's refname to the currentextension
            else:
                ModulesFound = False    #if we can't find a Module.py then break loop (we are at highset level)
        else:
            ModulesFound = False    #if we can't find a Module.py then break loop (we are at highest level)

    os.chdir(OriginalCWD)
    return os.path.basename(TreeSourcesFolder) +r"/"+CurrentExtensionPath #return the SOURCE/VIPER/Module/OtherModule/



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
    for x in range(0,5):    #LOOPS 1-4 loops 3 times, cycle 4 DOESNT occur?
        VIPER_CookieUserInfo.append(LoginCookieText[:LoginCookieText.find("|")])
        LoginCookieText = LoginCookieText[LoginCookieText.find("|")+1:]
    return{ "Server" : VIPER_CookieUserInfo[0],
           "Token" : VIPER_CookieUserInfo[1],
           "NEVER_SHARE_SharedFernetKey" : (VIPER_CookieUserInfo[2]).encode(),
           "LocalIPAddress": VIPER_CookieUserInfo[3],
           "id":VIPER_CookieUserInfo[4],
           "login":LoginCookieText[:LoginCookieText.find("|")]
           }



def LIMSQuery(request, Database:str, Query, Method:str):
    """Send an SQL command to the VIPER_Server

    Args:
        request (dict): A Flask request from the Local User containing their VIPER_Cookie with user information
        Query (str): SQL command to be performed, format subject to changed based on how your VIPER_Server performs SQL query construction 
        Database (str): Name of the database which is to be accessed

    Returns:
        dict: Response from the VIPER_Server containing an error message the completed Query
    """
    MyCookie = None
    if request:
        MyCookie = request.cookies.get('VIPER_LocalUserInfo')
    if MyCookie is None:
        #Attempt Third Party App intergration
        print("VIPER LIMS Query via third party app")
        try:
            CookieRequest=requests.post("http://127.0.0.1:7800/RefreshLogin")
            MyCookie = CookieRequest.text
        finally:
            if MyCookie is None:
                return "VIPER Cookie not found, cannot send LIMS request."
            elif MyCookie.find("|") < 0:
                print(MyCookie)
                return MyCookie
    CookieInformation = VIPER_DecodeLoginCookie(MyCookie)
    #POST##
    sqlJSONreq = {
        'SQLCommand': Query,       #Send just a single space: " " to get UserInfo ([login] = name, [id] = userid)
        'Database': Database,
        'Method': Method
        }
    sqlJSON = json.dumps(sqlJSONreq)
    #Server Communication
    
    EncryptedPostData={"Token":(CookieInformation["Token"]), 
                       "Info": (VIPER_Encrypt(sqlJSON, CookieInformation["NEVER_SHARE_SharedFernetKey"]).decode()) 
                       }
    
    Response = requests.post(CookieInformation["Server"], json = (EncryptedPostData), verify=False)
    
    return VIPER_Decrypt(Response.text, CookieInformation["NEVER_SHARE_SharedFernetKey"])       #HAVE TO SEND TOKEN TOO

OriginalCWD  = os.getcwd()
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")
os.chdir("..")
VIPER_RootDirectory = False
if os.path.exists(os.path.join(os.getcwd(),"Sources")):
    VIPER_RootDirectory = os.getcwd()
os.chdir(OriginalCWD)

def VIPER_GetRootDirectory():
    return VIPER_RootDirectory