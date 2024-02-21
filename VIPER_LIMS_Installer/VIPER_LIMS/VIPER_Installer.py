def Install(Install_Type:str="Select", Install_Directory:str="Select", SDumps:str="None", VIPER_Source:str=r"https://github.com/JackLawrenceCRISPR/VIPER_LIMS/archive/refs/heads/main.zip"):
    """Installs a VIPER LIMS Client or Server and installs necessary dependencies.

    Args:
        Install_Type (str): By default the user is prompted with a choice. Server or Client can be specified in the arguments to skip the prompt.
        Install_Directory (str): The directory to which VIPER LIMS will be Installed. By default VIPER will prompt the user for an installation directory; type 'cwd' for current working directory.
    """
    import sys
    import os

    if hasattr(sys, 'getandroidapilevel'):
        if Install_Directory == "Select":
            Install_Directory = os.getcwd() #just dump it in termux files, it's easier to execute and we have good permissions.
        if Install_Type=="Select":
            Install_Type = "client"

    if Install_Type == "Select":
        print("Installation type:")
        Install_Type = input()
        if Install_Type.lower() == "s":
            Install_Type = "server"
        if Install_Type.lower() == "" or Install_Type.lower() == " " or Install_Type.lower() == "c":
            Install_Type = "client"
    Install_Type = Install_Type.lower()

    if Install_Directory=="Select":
        print("Directory")
        Install_Directory = input()

    if Install_Directory == "" or Install_Directory == " " or Install_Directory.replace("'","").replace('"',"").lower() == "cwd" or Install_Directory.lower()=="current working directory":
        Install_Directory = os.getcwd()
    if not os.path.exists(Install_Directory):
        print("Installation directory not found...")
        return


    import zipfile
    import configparser
    import subprocess
    import shutil
    import requests
    
    def CannotNoneInput():
        UserResponse = input()
        if len(UserResponse) < 1:
            return CannotNoneInput()
        return UserResponse

    Unskippable_yes = {'yes','y', '[y]', '(y)'}
    Unskippable_no = {'no','n', '[n]', '(n)'}
    def UnskippableChoice(Unskippable_Statement: str):
        """Gives the user an unskippable choice

        Args:
            UnskippableStatement (str): The unskippable request

        Returns:
            bool: User's response
        """
        print(Unskippable_Statement)
        print("Confirm with [y] or reject with [n]")
        choice = input().lower()
        if choice in Unskippable_yes:
            return True
        elif choice in Unskippable_no:
            return False
        elif choice == "help":
            print("If you need help please go to: https://github.com/JackLawrenceCRISPR/VIPER-LIMS#installation")
        return UnskippableChoice(Unskippable_Statement)

    
    LocalZipFilePath = os.path.join(Install_Directory,"VIPER_Install_Source.zip")
    if os.path.exists(VIPER_Source): #local install instance
        print("Local VIPER_Source found!")
        LocalZipFilePath = VIPER_Source
    else:
        CancelDownload = False
        if os.path.exists(LocalZipFilePath):
            CancelDownload = UnskippableChoice("Local VIPER Source zip file found in Install directory. Should VIPER use this?")
        if not CancelDownload:     
            try:
                r = requests.get(VIPER_Source, stream=True)
                print("VIPER_Source URL found. Downloading from: " + VIPER_Source)
                with open(LocalZipFilePath, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
                print("Download complete!")
            except requests.ConnectionError as exception:
                raise Exception("Error: No VIPER Source found: please ensure you are connected to the internet and your source directory or download url is valid")
    
    if not os.path.exists(LocalZipFilePath):
        raise Exception("Error: previously idenfitied VIPER Source zip file cannot be found?")

    def EnsureInstallModule(ModuleName, ModuleImportName):
        try:
            __import__(ModuleImportName)  #check by import
            print(f"{ModuleName} Found")
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", ModuleName], check=True) 
            print(f"{ModuleName} Installed")
        return

    VIPER_Python_Module_Dependencies_Server = { "cryptography":"cryptography",
                                                "requests":"requests",
                                                "requests-oauthlib":"requests_oauthlib",
                                                "psycopg2":"psycopg2",
                                                "mysql-connector-python":"mysql.connector",
                                                "Authlib":"authlib.integrations.flask_oauth2",
                                                "Flask":"flask",
                                                "cheroot":"cheroot.wsgi",
                                                "rsa":"rsa",
                                                "requests_oauthlib":"requests_oauthlib"
                                                #"Flask-Authlib",
                                                #"python-sql"
                                                }




    #USE THIS TO MAKE HOOKS https://github.com/fefong/markdown_readme#style-text




    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    if Install_Type.lower() == "server" or Install_Type.lower() == "s":
        #Server Install Mode
        print("Installing Server")


        #Install any missing Python dependencies to the current environment
        print(f"The following Python Modules are required for VIPER Server:")
        for n in VIPER_Python_Module_Dependencies_Server.keys():
            print(n)
        if not UnskippableChoice("Can VIPER Install any missing modules?"):
            print("Modules are required for installation. VIPER will not reinstall a module which you already have.")
            print("Installation has stopped.")
            return 
        for n,m in VIPER_Python_Module_Dependencies_Server.items():
            EnsureInstallModule(n,m)   

    
    
    
    
    #Set up third party dependencies
        #Get SQL Database: #MySQL
        ConfigServerLater = True
        if UnskippableChoice("Do you want to configure the server now?"):
            ConfigServerLater = False
            if not UnskippableChoice("Do you have an SQL database?"):
                print(" ")
                print("If you need help please go to: https://github.com/JackLawrenceCRISPR/VIPER-LIMS#installation")
                print(" ")
                print("You require an SQL Database:")
                print("The following is recommended (and free):")
                print("https://dev.mysql.com/downloads/workbench/")
                while not UnskippableChoice("Have you installed an SQL Database?"):
                    if not UnskippableChoice("An SQL database is required, will you continue with the installation?"):
                        print("An SQL database is required")
                        return
            
            
            print("Please provide the following SQL Database information:")
            CFGInfo = {"ResourceServer":{},"Database":{},"OAuth":{}}
        
            print("Type the name of the database service you are using out of the following choices:") 
            print("| sqlite | postgresql | mysql |")
            SQLType = CannotNoneInput()
            if SQLType.lower() == "postgresql":
                print("SQLType set to PostgreSQL")
                SQLType = "PostgreSQL"
            elif SQLType.lower() == "sqlite":
                print("SQLType set to SQLite")
                SQLType = "SQLite"
            elif SQLType.lower() == "mysql":
                print("SQLType set to MySQL")
                SQLType = "MySQL"
            else:
                print("Type not recognised... defaulting to MySQL")
                SQLType = "MySQL"
            CFGInfo["Database"]["SQLType"] = SQLType
                
            print("Host IP of the SQL database (e.g 123.45.67.89)")
            print("If you installed the SQL database to this machine just type: localhost - do not include port number")
            CFGInfo["Database"]["SQLHost"] = CannotNoneInput()
            print("Please provide the port number:")
            CFGInfo["Database"]["SQLPort"] = CannotNoneInput()
            print("Account details for access to the SQL Database (it does not have to be 'root')")
            print("SQL Database Username which VIPER will use to read/write data")
            CFGInfo["Database"]["SQLUsername"] = CannotNoneInput()
            print("The corresponding password for this account:")
            CFGInfo["Database"]["SQLPassword"] = CannotNoneInput()

            
            
            
            
            
            
            #Get OAuth2 Service ##OAuth2-Configure
            if not UnskippableChoice("Do you have an OAuth2 Service?"):
                print("You require an OAuth2 Service - ALL your users must have an account on this service.")
                print("Create a LinkedIn app: https://www.linkedin.com/developers/")
                print("OR if you prefer Github use: https://github.com/settings/applications/new")
                while not UnskippableChoice("Have you created an app?"):
                    print("Create an app: https://www.linkedin.com/developers/")


            #Configure OAuth2 Service            
            print("Please provide the 'OAuth client id' of the OAuth2 app")
            CFGInfo["OAuth"]["OAuth_client_id"] = CannotNoneInput()
            print("And the corresponding 'OAuth client secret' for this app:")
            CFGInfo["OAuth"]["OAuth_client_secret"] = CannotNoneInput()
            print("Make sure the OAuth2 callback URL is configured on the OAuth2 service to this VIPER_Server correctly")
            print("It should look something like 'https://123.45.67.89:8000/callback' ")
            print("Provide the Callback URL used by the OAuth2 application:")#
            OAuthCallbackURL = ""
            while OAuthCallbackURL.find("/callback") <3:
                OAuthCallbackURL = CannotNoneInput()
                if OAuthCallbackURL.find("/callback") <3:
                    print("Callback URL must end with /callback")
            CFGInfo["ResourceServer"]["Callback_URL"] = OAuthCallbackURL

            ServiceType = "Other"
            if UnskippableChoice("Is your OAuth2 Service a LinkedIn developer app?"):
                ServiceType = "LinkedIn"
                CFGInfo["OAuth"]["OAuth_authorization_base_url"] = "https://www.linkedin.com/oauth/v2/authorization"
                CFGInfo["OAuth"]["OAuth_token_url"] = "https://www.linkedin.com/oauth/v2/accessToken"
                CFGInfo["OAuth"]["OAuth_TokenLink"] = "https://api.linkedin.com/v2/me"
                CFGInfo["OAuth"]["OAuth_Scope"] = "r_liteprofile"
            elif UnskippableChoice("Is your OAuth2 Service a Github developer app?"):
                ServiceType = "Github"
                CFGInfo["OAuth"]["OAuth_authorization_base_url"] = "https://github.com/login/oauth/authorize"
                CFGInfo["OAuth"]["OAuth_token_url"] = "https://github.com/login/oauth/access_token"
                CFGInfo["OAuth"]["OAuth_TokenLink"] = "https://api.github.com/user"
                CFGInfo["OAuth"]["OAuth_Scope"] = "None"

            #elif UnskippableChoice("Is your OAuth2 Service a Google developer app?"):
                #ServiceType = "Google"
            else:
                print("Your OAuth2 service requires manual configuration.")
                print("Please configure VIPER_Server\Server_Sources\settings.ini")


        
        
        
        
        
        
        
        #Installing Server...
        print("Installing VIPER_Server...")
        zip_archive = zipfile.ZipFile(LocalZipFilePath,'r')
        os.chdir(Install_Directory)
        #zip_archive.extractall(Install_Directory)
        TargetIsSubFolder = False
        FolderBeforeExtraction = [ f.path for f in os.scandir(Install_Directory) if f.is_dir() ]
        for file in zip_archive.namelist():
            if file.startswith('VIPER_Client/'):
                zip_archive.extract(file, Install_Directory)
            if file.startswith('VIPER_LIMS-main/VIPER_Server/'):
                TargetIsSubFolder = True
                zip_archive.extract(file, Install_Directory)
        if TargetIsSubFolder:
            ExtractedFolder = "Not found"
            for x in [ f.path for f in os.scandir(Install_Directory) if f.is_dir() ]:
                if not x in FolderBeforeExtraction:
                    ExtractedFolder = x
            TempClientDir = os.path.join(ExtractedFolder,"VIPER_Server")
            print(TempClientDir)
            shutil.copytree(TempClientDir,os.path.join(Install_Directory,"VIPER_Server") )
            shutil.rmtree(ExtractedFolder)

        
        if not ConfigServerLater:
            #Set details for config file: configparser
            SettingsFileINI = f"{Install_Directory}\\VIPER_Server\\Server_Sources\\Settings.ini"
            config = configparser.ConfigParser()
            config.read(SettingsFileINI)
            for CFGCategoryName, CFGCategoryData in CFGInfo.items():
                for CFGValueName, CFGValue in CFGCategoryData.items():
                    config.set(CFGCategoryName.strip(), CFGValueName.strip(), CFGValue.strip())
            with open(SettingsFileINI, 'w') as configfile:
                config.write(configfile)     
        print("VIPER_Server is Installed.")

        print("VIPER_Server is available on the local network")
        print("You must port forward port '8000' if you want VIPER_Server to be accessable online.")
        print("Run VIPER_Server.py and follow the instructions in the terminal to connect VIPER_Clients.")
        while not UnskippableChoice("Service Installed. Are you ready to quit?"):
            print("Service has been installed")

    else:
        #Client Install Mode
        print("Installing Client")
        zip_archive = zipfile.ZipFile(LocalZipFilePath,'r')
        os.chdir(Install_Directory)
        #zip_archive.extractall(Install_Directory)
        TargetIsSubFolder = False
        FolderBeforeExtraction = [ f.path for f in os.scandir(Install_Directory) if f.is_dir() ]
        for file in zip_archive.namelist():
            if file.startswith('VIPER_Client/'):
                zip_archive.extract(file, Install_Directory)
            if file.startswith('VIPER_LIMS-main/VIPER_Client/'):
                TargetIsSubFolder = True
                zip_archive.extract(file, Install_Directory)
        if TargetIsSubFolder:
            ExtractedFolder = "Not found"
            for x in [ f.path for f in os.scandir(Install_Directory) if f.is_dir() ]:
                if not x in FolderBeforeExtraction:
                    ExtractedFolder = x
            TempClientDir = os.path.join(ExtractedFolder,"VIPER_Client")
            print(TempClientDir)
            shutil.copytree(TempClientDir,os.path.join(Install_Directory,"VIPER_Client") )
            shutil.rmtree(ExtractedFolder)
    
        if SDumps=="None":
            print("Copy and paste an 'SDumps' from your VIPER_Server - if you don't know what this is, just type 'none'")
            SDumps = CannotNoneInput()


        SettingsFileINI = os.path.join(Install_Directory, "VIPER_Client", "Sources", "VIPER", "Settings.ini")     
        Textbox_3 = SDumps
        if Textbox_3.find("START!!!!!") < 0 or Textbox_3.find("!!!!!S") < 8 or not os.path.exists(SettingsFileINI):
            print("Please run the VIPER Client and configure the Server details in the Settings Panel -> Local Settings")
        else:
            config = configparser.ConfigParser()
            config.read(SettingsFileINI)
            SDump = Textbox_3[Textbox_3.find("START!!!!!")+10:Textbox_3.find("!!!!!S")]
            ExtractedURL =  SDump[:SDump.find("!!!!!-----")]
            if not ExtractedURL[-1:] == "/":
                ExtractedURL+="/"
            EncryptionKey = SDump[SDump.find("!!!!!-----")+5:].replace("@@@@@","\n")
    #Set Server Config data from SDUMP
            oriignaldir = os.getcwd()
            os.chdir(os.path.join(Install_Directory, "VIPER_Client", "Sources", "VIPER"))
            with open("Server_Encrypt.pem","w") as ServerEncryptfile:
                    ServerEncryptfile.write(EncryptionKey)
            config.set('Addresses', 'DefaultServerURL', ExtractedURL)
            config.set('Addresses', 'ServerURL', ExtractedURL) 
            with open("Settings.ini", 'w') as configfile:
                config.write(configfile)                        
            os.chdir(oriignaldir)
        print("Installation complete.")
    
    return os.getcwd()

if __name__ == '__main__':
   Install()
