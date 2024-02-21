def Launch_VIPER_Client():
    ###The launch applucation for VIPER-LIMS###
    GoTo_After_Exited_URL = "https://www.google.co.uk/" #the URL the user is sent to after the close the client
    ###Import Python Builtin Modules###
    import subprocess
    import sys
    import json
    import os
    os.chdir( os.path.dirname(os.path.realpath(__file__)) )

    os.environ["VIPER_LIMS_SRC_DIR"] = os.path.join(os.getcwd(),"Sources")

    import glob 
    import webbrowser
    from datetime import datetime
    import socket
    LocalIPAddress = socket.gethostbyname(socket.gethostname())
    import secrets
    import shutil
    import configparser
    global VIPER_Client_Process_Identification      #Can be used to self-terminate the VIPER upon logging out
    VIPER_Client_Process_Identification = os.getpid() 
    global Global_VIPER_Login_Cookie_LocalUserInfo
    Global_VIPER_Login_Cookie_LocalUserInfo = None

    if hasattr(sys, 'getandroidapilevel'):
        webbrowser.register("termux-open '%s'", None)   #Special configuration for Termux (Android device) compatibility

    ###Import (or Install->Import) External Python Module Dependencies###
    def Install_Module_Choice(ModuleName: str):
        """Gives the user an unskippable choice of wether a required module will be installed

        Args:
            ModuleName (str): Name of the required >pip install "Module"

        Returns:
            bool: User's consent on installing the required module
        """
        yes = {'yes','y', '[y]', '(y)'}
        no = {'no','n', '[n]', '(n)'}
        choice = input().lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print(f"Confirm {ModuleName} installation with [y] or reject with [n]")
            return Install_Module_Choice(ModuleName)

    def Install_Module(ModuleName : str):
        """Prompts the user with a request to automatically install an essential module which is not installed

        Args:
            ModuleName (str): Name of the required >pip install "Module"

        Raises:
            ImportError: User rejected the installation request
        """
        print(f"{ModuleName} module not found, would you like to install? [Y/N]")
        if Install_Module_Choice(ModuleName):
            subprocess.run([sys.executable, "-m", "pip", "install", ModuleName], check=True) 
        else:
            raise ImportError(f"Please install {ModuleName} with >pip install {ModuleName}")

    try:
        import requests
    except ImportError:
            Install_Module(ModuleName = "requests")
            import requests
        
    try:
        import rsa
    except ImportError:
            Install_Module(ModuleName = "rsa")
            import rsa

    try:
        from cryptography.fernet import Fernet
    except ImportError:
            if hasattr(sys, 'getandroidapilevel'):
                raise ImportError(f"Please use 'pkg install python-cryptography' and then run VIPER_Client.py again.")

                    #the below line doesn't work?!
                    #subprocess.run([sys.executable, "-m", "apt", "install", "python-cryptography"], check=True) #Special solution for Termux on Android (Rust compiler is usually required, this special version works on Android)
            else:
                Install_Module(ModuleName = "cryptography")
                import cryptography
         
            from cryptography.fernet import Fernet

    try:
        import urllib3
    except ImportError:
            Install_Module(ModuleName = "urllib3")
            import urllib3 
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #VIPER uses its own encryption

    try:
        from flask import Flask, request, redirect, jsonify, render_template, Blueprint, make_response, send_from_directory
    except ImportError:
            Install_Module(ModuleName = "flask")
            from flask import Flask, request, redirect, jsonify, render_template, Blueprint, make_response, send_from_directory

    #Read Settings.ini
    config = configparser.ConfigParser()
    config.read(os.path.join(os.getcwd(), "Sources", "VIPER", "Settings.ini"))
    ServerURL = config["Addresses"]["ServerURL"] 
    if ServerURL == "False":
        ServerURL = False
        print("No ServerURL, running in Offline mode")


    ###Define variables and functions###

    #Define secret keys / passwords for secure communcation. 
    #You should never access these, and you should NEVER share these.

    TempFileDirectory = os.path.join(os.getcwd(), "Sources", "VIPER", "TEMP")
    Server_Encryption_Key = "No Encryption Key"
    if os.path.exists(os.path.join(os.getcwd(), "Sources", "VIPER", "Server_Encrypt.pem")):
        with open(os.path.join(os.getcwd(), "Sources", "VIPER", "Server_Encrypt.pem"), "rb") as f:
            Server_Encryption_Key = rsa.PublicKey.load_pkcs1(f.read())  #Define the trusted Public Key for which only the VIPER_Server has the private key
    NEVER_SHARE_SharedFernetKey = Fernet.generate_key() #Except ONCE in Greet handshake, encrypted
    MyStateSecret = secrets.token_hex(8)                #Temporary secret for the Greet handhsake

    #Define encryption / decryption functions
    def VIPER_RSA_Encrypt(Message:str):
        """Asymmetrical RSA Encryption which only the VIPER_Server can decrypt, assuming the VIPER_Server's Private key is not compromised

        Args:
            Message (str): The message to be encrypted

        Returns:
            bytes: An RSA encrypted message, which only the VIPER_Server should be able to decrypt
        """
        if not type( ("").encode() ) == type(Message):
            Message = Message.encode()
        if len(Message) > 117:
            return VIPER_RSA_Encrypt(Message[:117]) + VIPER_RSA_Encrypt(Message[117:])
        return rsa.encrypt( (Message), Server_Encryption_Key)

    def VIPER_Encrypt(Message):
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

    def VIPER_Decrypt(EncryptedMessage):
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
        
    def Filename_Today():
        """Get todays date without slashes for filename compatibility.

        Returns:
            str: Todays date formatted as "DD-MM-YY"
        """
        return datetime.today().strftime("%x").replace("/","-") #Create the date



    #https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
    def DeleteFolder(folder): 
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))



    ##VIPER Handshake to create a secure connection##

    #Attempt to Greet the VIPER_Server with a temporary name (StateSecret) and our shared fernet key (SharedFernetKey)
    LoginURL = None #OAuth2 Server Login URL, retrieved from the Resource VIPER_Server
    if ServerURL:
        GreetData = VIPER_RSA_Encrypt(json.dumps( {                     #Encrypt our secrets with the VIPER_Server's Asymmetrical encryption key, only the VIPER_Server can decrypt this message
        "StateSecret"       :   MyStateSecret, 
        "SharedFernetKey" :   NEVER_SHARE_SharedFernetKey.decode()      #This is the ONLY time our shared secret should ever be shared, safely with the server  
        } ) )
    OfflineModeStatement = "Offline Mode: set SDump in Settings_Panel -> Local_Settings"
    try:
        if ServerURL:
            print(f"Attempting to connect to LIMS_Server at {ServerURL}")
            r = requests.post(f"{ServerURL}Greet", data=GreetData, verify=False)      #First communcation with the VIPER_Server
            LoginURL = VIPER_Decrypt(r.content) 
            print("LIMS_Server connection successful")
    except:
        #Could fail for many reasons, the server isn't up, IP address is wrong, our Greet data was invalid and server cannot respond, the servers response was invalid, etc
        print("Server Connection FAILED!")
        OfflineModeStatement = "Connection to ServerURL Failed, you are Offline."
        #raise ConnectionError("LIMS_Server connection has failed")
        ServerURL = False
    #We start doing more complicated LIMS setup now that we are confident that launch will work

    VIPER_Directory = os.getcwd() #Record the VIPER program's directory as VIPER_Directory
    #Prepare a generic non-specific Log directory for any module to access if required
    if not os.path.exists(os.path.join(VIPER_Directory, "Logs")):
        os.mkdir(os.path.join(VIPER_Directory, "Logs"))
    VIPER_Log_Directory = os.getcwd()
    #Relocate the current work directory to the Sources folder for easy VIPER_Module access
    os.chdir(os.path.join(VIPER_Directory, "Sources"))
    #sys.path.append(os.path.join(VIPER_Directory, "Sources"))
    sys.path.insert(1, os.path.join(VIPER_Directory, "Sources", "VIPER"))   ##this VIPER core has HIGHEST priority

    #Source trick
    #insert in position 1 the current sources folder to process
    #import the current sources folder as SourceX [where x is a number]
    #then we continue from there

    #prevent Module Toggler from being inactivated - to stop any silly little mistakes :)
    if os.path.exists(os.path.join(os.getcwd(),"Settings_Panel","INACTIVE")):
        os.remove(os.path.join(os.getcwd(),"Settings_Panel","INACTIVE"))
    if os.path.exists(os.path.join(os.getcwd(),"Settings_Panel","Sources","Module_Toggler","INACTIVE")):
        os.remove(os.path.join(os.getcwd(),"Settings_Panel","Sources","Module_Toggler","INACTIVE"))

    SourceTrees = []
    if os.path.exists(os.path.join(VIPER_Directory, "Sources", "VIPER","SourceTrees.json")):
        with open( os.path.join(VIPER_Directory, "Sources", "VIPER","SourceTrees.json"),"r") as SourceTreesFile:
            SourceTrees = json.loads(SourceTreesFile.read())["trees"] #load the SourceTree List
    SourceTrees.insert(0,os.path.join(VIPER_Directory, "Sources"))

    #Imports a list of VIPER-LIMS Modules and Names
    LML = [] #An Imported LIMS Module List (LML), entries are the modules themselves
    #Imports the VIPER_Module_X.py in every Module folder in Sources which contains one 
    def ScanForVIPERModules(LML:list, ScanDir:str=""): 
        if ScanDir != "":
            os.chdir(ScanDir)
        ScanDir = os.getcwd()
        
        #TempVIPERSource = __import__("Sources")

        for MF in [MF for MF in list(filter(os.path.isdir, os.listdir(os.getcwd()))) if len( glob.glob( os.path.join(MF, "*_VIPER_Module.py") ) )>0]: # :^)
            #Import each module as an entry in a table
            FMF = os.path.join(os.getcwd(), MF)
            MFFile = (glob.glob(os.path.join(FMF,"*_VIPER_Module.py")))[0] #Get the first instance of VIPER_Module_*.py  
            if os.path.exists(MFFile):
                if not os.path.exists(os.path.join(FMF,"INACTIVE")):
                    if os.path.exists(os.path.join(FMF,"Static","TEMP")):
                        DeleteFolder(os.path.join(FMF,"Static","TEMP")) #wipe the temp folder on bootup
                    os.chdir(FMF)
                    sys.path.insert(1,FMF)
            
                    try:
                        NewImport = __import__(MFFile[len(FMF)+1:-3])
                    except ImportError:
                        OriginalName = MFFile
                        NewTempName = MFFile+str(secrets.token_hex(24))+".py"
                        os.rename(MFFile,NewTempName) #module shares name with another? we'll just rename it (temporary)
                        try:
                            NewImport = __import__(MFFile[len(FMF)+1:-3])
                        except ImportError:
                            NewImport = False   #problem with the module
                        os.rename(NewTempName,OriginalName)
                    if NewImport is False:  #safer way of handline __import__ objects 
                        print(f"Failed to import VIPER Module {MF}")
                    else:
                        LML.append( [NewImport, not os.path.exists(os.path.join(FMF,"UNLISTED")) ] ) 
                        print(f">>Imported VIPER Module - {MF}")
                    if os.path.exists(os.path.join(FMF,"Sources")):
                        print(f">Getting deep sources from {MF}:")
                        ScanForVIPERModules(LML, os.path.join(FMF,"Sources"))
                        print(f">Finished deep sourcing {MF}")
                    sys.path.remove(FMF)
            os.chdir(ScanDir)
        
    SourceTreeBasenames = []
    VIPER_Sources_Directory = os.getcwd()
    for SourceTree in SourceTrees:
        if os.path.exists(SourceTree):
            SourceTreeBasename = os.path.basename(SourceTree)
            if SourceTreeBasename in SourceTreeBasenames:
                print(f"WARNING! POTENTIAL SOURCETREE CONFLICT DETECTED WITH {SourceTree} - MODULE WILL NOT BE IMPORTED.")
                print(f"Sourcetrees should have unique basenames, please rename the folder to ensure only ONE Sourcetree folder has the name: {SourceTreeBasename}")
            else:
                SourceTreeBasenames.append(SourceTreeBasename)
                print(">Importing from Source Tree: " + SourceTree)
                os.chdir(SourceTree)
                ScanForVIPERModules(LML,SourceTree)
        else:
            print("SourceTree Directory not found: "+SourceTree)
            
    os.chdir(VIPER_Sources_Directory)

    ###LIMS FLASK Setup###
    if not config["Addresses"]["OpenToLocalNetwork"].lower() == "true":
        LocalIPAddress = "127.0.0.1"

    #Define Cookie access
    def VIPER_DecodeLoginCookie(LoginCookieText):
        """Extract User information from a VIPER browser cookie
            Decoded Cookie Contents:
                ["Server"]  =   https://{IP Address of VIPER-Server}/LIMS 
                ["Token"]   =   Encrypted VIPER Token used by VIPER-Server to Authenticate a user. 
                ["PublicKey"]   =   Asymmetrical encryption key, for which only the VIPER-Server should have the decryption key
                ["LocalIPAddress"]  =   http://{Local Address}:{Port} where this VIPER-Client script hosts this service
                ["id"]  =   The UserID stated by the OAuth2 Service which the Token represents            
                ["login"]  =    Your Username stated by the OAuth2 Service which the Token represents         
                Additionally, id and login are only useful for local services, the Token determines your Server permissions.
        Args:
            LoginCookieText (str): A VIPER_Cookie from a web browser session containing User Information compressed into a single string
            
        Returns:
            dict: A dictionary containing the Cookie information (Server, Token, PublicKey, LocalIPAddress, id, login) 
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

    ### CREATE LIMS in FLASK ##
    app = Flask(__name__, template_folder=os.getcwd(), static_url_path="/Sources", static_folder='Sources')
    for XPages in LML:
        app.register_blueprint(XPages[0].Module_Page) #Register each LML Module


    #Register sources folder
    @app.route("/", methods = ["POST", "GET"])
    def VIPER_index():
        """Returns the Homepage of VIPER-LIMS.

        Returns:
            str: The HTML of the Homepage 
        """

        #Default information assuming the user is not logged in
        CookieInformation = {
            "Server": ServerURL,
            "LocalIPAddress":LocalIPAddress,
            "id":"You are not logged in",
            "login":"You are not logged in"
        }
        #If the user is logged in, then replace the information with correct data
        if request.cookies.get('VIPER_LocalUserInfo'):  
            CookieInformation = VIPER_DecodeLoginCookie(request.cookies.get('VIPER_LocalUserInfo'))

        return render_template("VIPER/Homepage.html", LocalIPAddress=LocalIPAddress, 
                            HomepageServer =  CookieInformation["Server"],
                            HomepageLocalIPAddress = CookieInformation["LocalIPAddress"],
                            Homepageid = CookieInformation["id"],
                            Homepagelogin = CookieInformation["login"])

        


    @app.route('/RefreshLogin', methods = ["POST", "GET"])
    def RefreshLogin():
        """
    POST Request:
        Returns: 
            The users own VIPER_LocalUserInfo cookie.
            Used for intergration with others apps through VIPER_Utilities.LIMSQuery function
            For example, Jupyter Notebook can use LIMSQuery

    GET Request:
        Redirects to the homepage of VIPER. 
        Allows for cookies to be set and processed before loading the homepage.

        Returns:
            str: A redirect to the homepage of this VIPER client.
        """

    #TODO: THIRD PARTY REST-API IDEA
    #1. User goes onto page
    #2. user consents ("I understand the risks, take responsibility etc")
    #3. while true do loop (while box is ticked) - sets timer on python->settings.ini to 4
    #4. main script always ticks down by subtracting 1 (if number is greater than 10 then it auto-sets it to zero)
    #5. whilst the user has a tab open to permit transmissions from third party apps, the portal lets local systems LIMS-proxy
    #6. as soon as the browser is closed, LIMS takes 20 seconds (in 5 second chunks) to reduce settings.ini 4 -> 3 -> 2 -> 1 -> off


    #Right now we just have third party app intergration through Python imports ONLY, other systems not yet supported
        if request.method == 'POST':
            if str(request.remote_addr)=="127.0.0.1":
                if config["Addresses"]["thirdpartyappintergration"].lower() == "true":
                    global Global_VIPER_Login_Cookie_LocalUserInfo
                    if (request.data).decode() == "locate":
                        print("Third Party App granted VIPER_Utilities module location")
                        return str(os.path.join(VIPER_Directory, "Sources", "VIPER"))
                    elif Global_VIPER_Login_Cookie_LocalUserInfo is None:
                        print("Third Party App Login Cookie request failed - you are not logged in.")
                        return "no cookie"
                    else:
                        print("Granted Login Cookie to Third Party App, if you did not authorise this please log out immediately!")
                        return Global_VIPER_Login_Cookie_LocalUserInfo
                else:
                    print("Rejected Third Party App Login Cookie request. External App Intergration is not enabled.")
                    return "VIPER LIMS Client - External App Intergration is not enabled."
            else:
                print("Rejected Third Party App Login Cookie request. Connection was from an external device at "+str(request.remote_addr))
                return "VIPER LIMS Client - Login Cookie requests must be from a localhost app (127.0.0.1)."
        else:
            return """<html>
    <script>
        setTimeout(function(){window.location.replace('http://"""+LocalIPAddress+""":7800')}, 1);
    </script>"""

    @app.route('/callback')
    def Callback():
        """Handles the Callback after a successful OAuth2 login.
        Updates the local User's information in the LocalUser class
        Inserts the local User's information in a cookie which is stored in the web browser session
        Redefines the standard VIPER_Server ServerURL to the LIMS directory for easy communcation with the LIMS module after login

        Returns:
            str: A redirect which returns the user to the Homepage AND sets the VIPER_LocalUserInfo cookie
        """
        EncryptedToken = False
        currenturl = request.url[4:].replace("%2F", "/").replace("%3F", "?")
        if currenturl.find("callback?code=") + currenturl.find("&code=") > 2: #Check URL contains callback code
            ValidLoginToken  = currenturl[currenturl.find("http"):]
            #Use Resource Server to get Client Token then Launch LIMS
            CallbackInfo = json.dumps({'TokenURL': ValidLoginToken, "StateSecret":MyStateSecret})
            
            EncryptedTokenURLInfo = VIPER_RSA_Encrypt(CallbackInfo[:117]) + VIPER_RSA_Encrypt(CallbackInfo[117:])
            
        
            EncryptedToken = requests.post(ServerURL+"ConfirmIdentity", data = EncryptedTokenURLInfo, verify=False)        
        resp = make_response(redirect(f"http://{LocalIPAddress}:7800/RefreshLogin", code=302))
        MyClientToken = "No Token"
        if EncryptedToken:
            MyClientToken = VIPER_Decrypt(EncryptedToken.content)

    #Get User Info
        UserInfoRequestDumpedJSON = json.dumps({
        'SQLCommand': "UserID",     
        'Database': "UserID",
        'Method': "UserID"
        })
        EncryptedPostData={"Token":(MyClientToken), 
                        "Info": (VIPER_Encrypt(UserInfoRequestDumpedJSON).decode()) 
                        }    
        
        print(LocalIPAddress)

        if not MyClientToken == "No Token":
            Response = requests.post(ServerURL+"LIMS", json = (EncryptedPostData), verify=False)
            ServerProvidedUserInformation = VIPER_Decrypt(Response.text)
            ServerProvidedUserInformation = json.loads(ServerProvidedUserInformation)
            global Global_VIPER_Login_Cookie_LocalUserInfo
            Global_VIPER_Login_Cookie_LocalUserInfo = f"{ServerURL}LIMS|{MyClientToken}|{NEVER_SHARE_SharedFernetKey.decode()}|{LocalIPAddress}|{ServerProvidedUserInformation['id']}|{ServerProvidedUserInformation['login']}|"
            resp.set_cookie('VIPER_LocalUserInfo', Global_VIPER_Login_Cookie_LocalUserInfo, httponly=True, samesite='Strict') #Secure=True->httpsonly  #add expires=date
        else:
            resp.set_cookie('VIPER_LocalUserInfo', f"You are Offline|{MyClientToken}|No Fernet Key Required|{LocalIPAddress}|{OfflineModeStatement}|{OfflineModeStatement}|", httponly=True, samesite='Strict') #Secure=True->httpsonly  #add expires=date
        return resp


    @app.route('/Exit_LIMS')
    def Exit_LIMS():
        """Stops this python script by killing the Process ID task.

        Returns:
            Stops everything, only used when exiting LIMS.
        """

        os.chdir(VIPER_Sources_Directory)
        for MF in [MF for MF in list(filter(os.path.isdir, os.listdir(os.getcwd()))) if len( glob.glob( os.path.join(MF, "*_VIPER_Module.py") ) )>0]: # :^)
            #Import each module as an entry in a table
            FMF = os.path.join(os.getcwd(), MF)
            if not os.path.exists(os.path.join(FMF,"INACTIVE")):
                if os.path.exists(os.path.join(FMF,"Static","TEMP")):
                    DeleteFolder(os.path.join(FMF,"Static","TEMP")) #wipe the temp folder on logout



        #If you want to use the worst solution possible:
        #global VIPER_Client_Process_Identification
        try:
            from threading import Thread
            import time
            def thread_function(threaditerable):
                time.sleep(1)
                #os.kill(VIPER_Client_Process_Identification, 15) #9 = harsh shutdown
                import sys
                sys.exit()
            deadthd = Thread(target=thread_function, args=(1,))
            deadthd.start()
            return r"""#<script>window.close();function close_window(){window.close()}</script> #auto destroy
        <script>setTimeout(function(){window.location.replace('"""+ GoTo_After_Exited_URL +r"""')}, 100);</script> #redirects to google homepage one exit if we can't self-close the tab!
        #<a href='javascript:close_window();'>VIPER_LIMS Exit, click here to close</a> #helpful button destroy
        """
        except:
            import sys
            sys.exit()
            #os.kill(VIPER_Client_Process_Identification, 15) #9 = harsh shutdown

            
    @app.route('/logout')
    def Logout():
        """Destroys the user's VIPER_LocalUserInfo cookie 

        Returns:
            Redirect to Exit_LIMS, which will stop VIPER by killing the Process ID of this task.
        """
                        
        if request.cookies.get('VIPER_LocalUserInfo'):
            CookieInformation = VIPER_DecodeLoginCookie(request.cookies.get('VIPER_LocalUserInfo'))
            if not CookieInformation["Token"] == "You are Offline":
                UserInfoRequestDumpedJSON = json.dumps({
                'SQLCommand': "Logout",     
                'Database': "Logout",
                'Method': "Logout"
                })
                EncryptedPostData={"Token":(CookieInformation["Token"]), 
                                "Info": (VIPER_Encrypt(UserInfoRequestDumpedJSON)) 
                                }    
                try:
                    print(f"Attempting to Logout from {ServerURL}")
                    Response = requests.post(ServerURL+"LIMS", json = (EncryptedPostData), verify=False)
                    print("Logout probably Successful")
                except:
                    print("Logout Failed")
        resp = make_response("""<html>
    <script>
        setTimeout(function(){window.location.replace('http://"""+LocalIPAddress+""":7800/Exit_LIMS')}, 100);
    </script>""")
        resp.set_cookie('VIPER_LocalUserInfo',"None", expires=0)
        return resp




    #how to serve a resource? - temporary
    #each folder needs its own static folder to serve resouces!
    ListOfServedResources = []
    @app.route('/LocalResources', methods = ["POST", "GET"])
    def SetLocalResources():
        if request.method == 'POST':
            if str(request.remote_addr)=="127.0.0.1":
                global Global_VIPER_Login_Cookie_LocalUserInfo
                if Global_VIPER_Login_Cookie_LocalUserInfo == request.cookies.get('VIPER_LocalUserInfo'):
                    ResourceInfo = json.loads((request.data).decode()) #ask with - json.dumps({"Filename":"Filename.txt","Location":"Module/Name/Whatever"})
                    #Resource path at Sources/-> ="whatever/someplace/"
                    #app.view_functions[route["page"]] = my_func

                    return send_from_directory(ResourceInfo["Filename"], os.path.join(VIPER_Sources_Directory, ResourceInfo["Location"]) )
                else:
                    return "Invalid login cookie"
            else:
                return "Local resources can only be sent to localhost"
        else:
            #make a list of local resources maybe?
            return "Local Resources"
        













    ###VIPER Sidebar Configuration###
    #Intergrated with every VIPER_module#
    app.config['SERVER_NAME'] = f'{LocalIPAddress}:7800'
    #Configure Sidebar HTML
    ModuleSearchChoices = f"""<li><a href=" http://{LocalIPAddress}:7800 " class="VIPER-SbBtn">Homepage</a></li>""" #Prepare a homepage button to be inserted into the HTML, start of a long list of Module buttons for the sidebar

    #Debug code for adding 100 dummy entries to the sidebar, mainly to test the scrollbar
    #for x in range(100):
    #   FakeModuleName = "Example "+str(x)
    #  FakeModuleLink = "https://www.google.com/"
    # ModuleSearchChoices = ModuleSearchChoices+r"""<li><a href=" """+ FakeModuleLink +""" " class="VIPER-SbBtn">"""+ FakeModuleName  +"""</a></li>""" #HTML button which states the name of a module, and redirects to the location

    for ModuleName in LML:
        if ModuleName[1]:
            ModuleLink = f"http://{LocalIPAddress}:7800/"+ModuleName[0].LIMSReferralRoute()+ModuleName[0].LIMSReferralName() #A module's location on the local Flask instance
            # 7800/"+ModuleName[0].LIMSReferralRoute()+ModuleName[0].LIMSReferralName()
            ModuleSearchChoices = ModuleSearchChoices+r"""<li><a href=" """+ ModuleLink +""" " class="VIPER-SbBtn">"""+ ModuleName[0].LIMSReferralName().replace("_"," ")  +"""</a></li>""" #HTML button which states the name of a module, and redirects to the location
    try:    #fixes Linux systems (app.url_for causes runtime error)
        VIPERIconLink = app.url_for('static', filename='VIPER/Viper_Icon_Large.png')
    except:
        VIPERIconLink = "None"
    finally:
        ModuleSearchChoices = """<html><head><link rel="icon" type="image/png" href="""+VIPERIconLink+"/></head></head>" +ModuleSearchChoices + "</ul></div></body>"    #Completes the ModuleSearchChoices list HTML which can be appended to the Sidebar file for a dynamic Module list
    #TODO: Add easy Logout button which goes to http://{LocalIPAddress}:7800/logout

    SidebarFilename = "SidebarClickable.html"
    if config["Addresses"]["HotkeySidebar"].lower() == "true":
        SidebarFilename = "SidebarHotkey.html" #Press Z + C together to open the VIPER sidebar

    SidebarFile = open(os.path.join(os.getcwd(),"VIPER",SidebarFilename),mode='r') #Load the HTML of the sidebar                                           ###TODO: Make a SCROLLABLE sidebar, excluding the search/homepage button for easy navigation
    SidebarFileContents = SidebarFile.read() + ModuleSearchChoices #Insert the dynamic Module list generated in VIPER into the sidebar                  ##TODO: Rework file structure to allow sub-module via folders, with expandable mini-lists
    SidebarFile.close() #No longer, HTML str data stored in SidebarFileContents

    @app.route('/Sidebar')
    def SidebarGet():
        """Returns the dynamic Sidebar HTML, generated from available LIMS modules

        Returns:
            str: HTML containing a JQuery controlled searchable list of LIMS Modules
        """
        #Create Sidebar
        return SidebarFileContents

    @app.route('/VIPER_Resources/VIPER_Default_CSS')
    def send_VIPER_Default_CSS():
        return send_from_directory(os.path.join(VIPER_Sources_Directory,"VIPER"),"DefaultVIPERCSS.css")




    ##START LIMS##
    if ServerURL:
        webbrowser.open_new_tab(LoginURL)
    else:
        webbrowser.open_new_tab(f"http://{LocalIPAddress}:7800/callback")

    app.run(host=str(LocalIPAddress), port=7800) #make this 0.0.0.0? 


    #Settings file

    #1. Boa Constructor
    #2. Method Check 
    #3. Basic_Admin_Panel
    #4. Module_Toggler
    #5. Local Settings
    #6. Restart LIMS 

    #Write a module for setting config file


    #7. Jupyter notebook intergration + VIPER Utilities release on pip install?


if __name__ == "__main__":
    Launch_VIPER_Client()
