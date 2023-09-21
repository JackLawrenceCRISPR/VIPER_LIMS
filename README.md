<h1 align="center">Virtual Interface for Production & Experimental Research</h1>
<p align="center">
  <picture>
    <source srcset="./Viper_Icon_Small.ico"> 
    <img src="./Viper_Icon_Small.ico">
  </picture>
</p>

<h3 align="center">Easy | Modular | Lightweight</h3>

<p align="center">A simple, highly scalable & adaptable LIMS system for rapidly evolving laboratory teams.</p>

# Features
- **Customisable clientside:** Build your own VIPER modules in Python and help from Boa Constructor
- **Boa Constructor:** Make new HTML-Javascript-Python front-end modules with simple drag and drop
- **Client Scripting:** Beginner friendly code with complete control for advanced programmers
- **Client Commands:** Scriptable client to server requests passed through Server Methods
- **Server Methods:** Programmable permission authenticated serverside functions
- **Security:** OAuth2 user verification and encrypted HTTP requests
- **SQL:** Intrinsic support for MySQL, PostgreSQL and SQLite 
- **OAuth2:** Intrinsic support for Github and LinkedIn OAuth2 Apps

### The Vision
- Lightweight plug-and-play framework
- Power for beginner programmers
- Freedom for advanced programmers
- Competency based permissions


# Installation
[Requires Python (>=3.7)](https://www.python.org/downloads/)

Operating System terminal:  
```
pip install VIPER_LIMS
```

Python terminal or script:  
```python
import VIPER_LIMS
VIPER_LIMS.Deploy_VIPER()
```

_Alternatively: download this repository and run VIPER_LIMS/VIPER_Installer.py_


# Deploy Server
[Server Install Tutorial](VIPER_Videos/VIPER_Server_Install_Compressed.mp4)

Store the *VIPER_Server will need:* information from the *SQL Database* and *OAuth 2.0 Service* sections below  
Run the following command and provide the requested information:
```VIPER_LIMS.Deploy_VIPER("Server")```

## Server IP Address: 
Before you start you should know the **local IP of your VIPER_Server**.  
Use ```ipconfig``` on Windows or ```ifconfig``` on Unix based systems and get your IPV4 local IP address (usually 192.168.X.X)  
If you do not intend to host your VIPER_Server online then your VIPER_Server IP Address will be this local IP  

If you want your VIPER_Server to be accessible through the internet you need to **Port Forward TCP 8000** on your router to the local IP of your VIPER_Server  
[Afterwards use your public IP Address](https://whatismyipaddress.com/)  

You will use this IP address for the OAuth2 service callback URL.
**If your IP Address changes you must update the callback URL.**

## SQL Database
The database which your LIMS requests will access.  
[MySQL is recommended](https://dev.mysql.com/downloads/workbench/) but PostgreSQL or SQLite should be compatible  

*The VIPER_Server will need:*
- Username
- Password
- IP Address of SQL Server 
- Port of SQL Server (default is 3306 for MySQL)

## OAuth 2.0 Service
The service which hosts your users accounts, pick ONE:  
- [LinkedIn OAuth2](https://www.linkedin.com/developers/secure/developer)  
- [Github OAuth2](https://github.com/settings/applications/new)  
- [Other available services which require manual configuration](https://requests-oauthlib.readthedocs.io/en/latest/examples/examples.html)  
- [Further reading if you want to set up your own](https://github.com/topics/oauth2-server?l=python)  

*The VIPER_Server will need:*
- Client ID
- Client Secret
- Callback URL


# Deploy Client
[Client Install Tutorial](VIPER_Videos/VIPER_Client_Install_Compressed.mp4)
1. ```VIPER_LIMS.Deploy_VIPER("Client")```
2. Paste the desired deployment folder directory
3. Paste the VIPER_Server SDump (or "none" if you do not have one yet)
4. To connect to a new Server go to Settings_Panel -> Local_Settings, then Paste an SDump -> Click *Autosetup SDump*
5. Type *off* or *on* and click *Set ServerURL* to disable or enable online mode  
**To Logout go to Settings_Panel/Logout AND Logout of your OAuth2 Service**
[Client Tour Tutorial](VIPER_Videos/VIPER_Client_Tour.mp4)


# Applications
## Boa Constructor
Build your own modules:
[Boa Constructor Tutorial](VIPER_Videos/VIPER_Boa_Constructor_Compressed.mp4)

Highly modular, simple, completely customisable scripts for rapidly evolving teams
1. Launch the Client  
2. Assemble an HTML page using Boa Constructor  
3. See **Coding a *Module_Script.py***
4. Activate your module in Settings_Panel/Module_Toggler
5. Restart VIPER_Client

## Coding a *Module_Script.py*:
```python
Expired_Ethanol_List = LIMSQuery(False, "Reagents", ["Ethanol","Expired"], "fetchall_criteria")) #Access the LIMS SQL Database
```
Which could execute the following on the server through a fetchall_criteria Method:
```sql
SELECT * FROM Ethanol WHERE Expired = True
```

In this example we are fetching all Expired Reagents:  
**LIMSQuery(**  
**False**:     Initiates LIMSQuery's Third Party App support,  
**Database**:  The database within which to execute the SQL process,  
**Command**:   The data necessary to perform the request,  
**Method**:  The VIPER_Server method through which the Command will be processed,  
**)** 

```python
#Example Boa Constructed module script:
def Process_User_Request(request):  #Runs when the user clicks a button on your Boa Constructed VIPER Module
    try:
        ButtonPressed = request.form['SubmitButtonPressed']  #Which action button has the user pressed?
        if ButtonPressed == "Button 0":                      #If the user pressed Action button 0 run the following
##YOUR CODE: ##
            Textbox_2 = request.form.get("Textbox 2")             #Input: The user's Textbox 2 input (e.g "Ethanol")
            Textbox_3 = request.form.get("Textbox 3")             #Input: The user's Textbox 3 input (e.g "Expired")

            ##Process the input however you want!##
            Expired_Ethanol_List = LIMSQuery(request,"Reagents", [Textbox_2,Textbox_3], "fetchall_expired") 
            SubmissionResponse = {"Label 4":Expired_Ethanol_List} #Output: Change the text in Label 4

        elif ButtonPressed == "Button 1":                 #if the user pressed a different button...
            #etc
##END OF YOUR CODE##
    except:
        return 'An error has occured.', 400 #If nothing happens, return nothing
    finally:        
        return jsonify(Info=SubmissionResponse) 
```

## Jupyter Notebook intergration:  
Enable Third Party App Intergration in Settings_Panel/Local_Settings  
```python
import sys, requests #required imports
VIPERFolder = requests.post("http://127.0.0.1:7800/RefreshLogin", data="locate") #get VIPER_Utility folder
print(f"VIPER Folder: {VIPERFolder.text}")
sys.path.insert(0, VIPERFolder.text) #Prepare VIPER folder for importation
from VIPER_Utility import LIMSQuery #Import VIPER_Utility from VIPER_Client

print( LIMSQuery(request,"Reagents", [Textbox_2,Textbox_3], "fetchall_expired") )
```
