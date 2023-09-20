def Deploy_VIPER(Deployment_Type:str="Select", Deployment_Directory:str="Select", SDumps:str="None"):
    """Deploys a VIPER LIMS Client or Server and installs necessary dependencies.

    Args:
        Deployment_Type (str): By default the user is prompted with a choice. Server or Client can be specified in the arguments to skip the prompt.
        Deployment_Directory (str): The directory to which VIPER LIMS will be deployed. By default VIPER will prompt the user for an installation directory; type 'cwd' for current working directory.
    """
    
    if Deployment_Type == "Select":
        print("Installation type:")
        Deployment_Type = input()
        if Deployment_Type.lower() == "s":
            Deployment_Type = "server"
        if Deployment_Type.lower() == "" or Deployment_Type.lower() == " " or Deployment_Type.lower() == "c":
            Deployment_Type = "client"
    if Deployment_Directory=="Select":
        print("Directory")
        Deployment_Directory = input()
        if Deployment_Directory == "" or Deployment_Directory == " ":
            Deployment_Directory = None


    import os
    if Deployment_Directory == "" or Deployment_Directory == " " or Deployment_Directory.replace("'","").replace('"',"").lower() == "cwd" or Deployment_Directory.lower()=="current working directory":
        Deployment_Directory = os.getcwd()
    if not os.path.exists(Deployment_Directory):
        print("Installation directory not found...")
        return

    import zipfile
    import configparser
    import subprocess
    import sys

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
                                                "mysql-connector-python":"mysql.connector",
                                                "Authlib":"authlib.integrations.flask_oauth2",
                                                "Flask":"flask",
                                                "cheroot":"cheroot.wsgi",
                                                "rsa":"rsa",
                                                "requests_oauthlib":"requests_oauthlib"
                                                #"Flask-Authlib",
                                                #"python-sql"
                                                }








    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    if Deployment_Type.lower() == "server" or Deployment_Type.lower() == "s":
        #Server Deployment Mode
        print("Deploying Server")


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


        
        
        
        
        
        
        
        #Deploying Server...
        print("Deploying VIPER_Server...")


        VIPERZip = os.path.join(os.getcwd(),"VIPER_Server.zip")
        if not os.path.exists(VIPERZip):
            VIPERZip = os.path.join(os.getcwd(),"VIPER_Server.zip.py")
            if os.path.exists(VIPERZip):
                os.rename(VIPERZip, VIPERZip[:-3])
                VIPERZip = VIPERZip[:-3]
            if not os.path.exists(VIPERZip):
                print("VIPER_Server.zip is missing...")
                return
        zip_archive = zipfile.ZipFile(VIPERZip,'r')
        os.chdir(Deployment_Directory)
        zip_archive.extractall(Deployment_Directory)

        #Set details for config file: configparser
        SettingsFileINI = f"{Deployment_Directory}\\VIPER_Server\\Server_Sources\\Settings.ini"
        config = configparser.ConfigParser()
        config.read(SettingsFileINI)
        for CFGCategoryName, CFGCategoryData in CFGInfo.items():
            for CFGValueName, CFGValue in CFGCategoryData.items():
                config.set(CFGCategoryName.strip(), CFGValueName.strip(), CFGValue.strip())
        with open(SettingsFileINI, 'w') as configfile:
            config.write(configfile)     
        print("VIPER_Server is deployed.")

        print("VIPER_Server is available on the local network")
        print("You must port forward port '8000' if you want VIPER_Server to be accessable online.")
        print("Run VIPER_Server.py and follow the instructions in the terminal to connect VIPER_Clients.")
        while not UnskippableChoice("Service Installed. Are you ready to quit?"):
            print("Service has been installed")

    else:
        #Client Deployment Mode
        print("Deploying Client")
        #Install Server Dependencies [Imports]
        VIPERZip = os.path.join(os.getcwd(),"VIPER_Client.zip")
        if not os.path.exists(VIPERZip):
            VIPERZip = os.path.join(os.getcwd(),"VIPER_Client.zip.py")
            if os.path.exists(VIPERZip):
                os.rename(VIPERZip, VIPERZip[:-3])
            VIPERZip = VIPERZip[:-3]
            if not os.path.exists(VIPERZip):
                print("VIPER_Client.zip is missing...")
                return
        zip_archive = zipfile.ZipFile(VIPERZip,'r')
        os.chdir(Deployment_Directory)
        zip_archive.extractall(Deployment_Directory)
    
        #Take a THIRD Argument from the installer^
        #That will be a ServerDumps string
        #Run same processing as in our 
        if SDumps=="None":
            print("Copy and paste an 'SDumps' from your VIPER_Server - if you don't know what this is, just type 'none'")
            SDumps = CannotNoneInput()


        SettingsFileINI = os.path.join(Deployment_Directory, "VIPER_Client", "Sources", "VIPER", "Settings.ini")     
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
            os.chdir(os.path.join(Deployment_Directory, "VIPER_Client", "Sources", "VIPER"))
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
   Deploy_VIPER()
