def ModuleName():
    return "Local_Settings"

#Import Modules
from flask import jsonify
import json
import os
import sys
sys.path.append(os.path.join(os.environ["VIPER_LIMS_SRC_DIR"],"VIPER"))
from VIPER_Utility import LIMSQuery, LogOutput
os.chdir( os.path.dirname(os.path.realpath(__file__)) ) #ensure we operate in this Module's folder
import configparser
config = configparser.ConfigParser()




#Response Script:
def Process_User_Request(request):
    """Local Settings Module: Configures the local VIPER Client's settings.ini file

    Button 0: Gets and Sets the ServerURL
        Inputs  : 
            Textbox 2: Different behavior based upon input type:
                    "http://..." -> Sets ServerURL to input \n
                    "off" -> Disables ServerURL, switching VIPER to Offline mode on restart \n
                    "on" -> Sets ServerURL from DefaultServerURL, switching VIPER to Online mode on restart \n
                    ""->An empty submission box will get the current value of ServerURL
        Outputs : 
            Label 4: Returns the current ServerURL value

    Button 1: Toggles the OpenToLocalNetwork value - determines whether the VIPER_Client can be accessed accross the local network by other devices. Only ever set this to True if you absolutely trust your local network with your security. Should always be False for security reasons, only enable this feature if you need to. e.g accessing VIPER_Client from a browser on a mobile phone.
    Button 2: Toggles the HotkeySidebar value - the VIPER Client will use "Z + C" hotkeys to toggle the sidebar, a more device compatible but intrusive variation with a toggle button at the top left is enabled if this value is set to False. Set this to False for touchscreen compatibility.
    
    Returns: A Jsonified string
    """
    try: 
        ButtonPressed = request.form['SubmitButtonPressed']
        SubmissionResponse = {
            "Label 4":"Cannot find Settings.ini"
            }
        


        print(ButtonPressed)

        OriginalSentDir = os.getcwd()
        os.chdir( os.path.dirname(os.path.realpath(__file__)) ) 
        os.chdir("..")
        for x in range(1,6): #search two folder-module deep
            if not os.path.exists(os.path.join(os.getcwd(), "Sources", "VIPER", "Settings.ini")):
                os.chdir("..")
        config.read(os.path.join(os.getcwd(), "Sources", "VIPER", "Settings.ini"))

        if ButtonPressed == "Button 0": 
            Textbox_3 = request.form.get("Textbox 3")
            Label4ServerURLResponse = config["Addresses"]["ServerURL"]
            if Label4ServerURLResponse == "False":
                Label4ServerURLResponse = "Nothing. You are Offline."

            if Textbox_3[:4] == "http":
                if not Textbox_3[-1:] == "/":
                    Textbox_3+="/"
                print(f"Setting ServerURL to: {Textbox_3}")
                config.set('Addresses', 'ServerURL', Textbox_3)  
                Label4ServerURLResponse = config["Addresses"]["ServerURL"]
            elif Textbox_3.lower() == "false" or Textbox_3.lower() == "none" or Textbox_3.lower() == "disable" or Textbox_3.lower() == "offline" or Textbox_3.lower() == "off":
                print("Offline Mode Enabled")
                Label4ServerURLResponse = "Offline Mode Enabled"
                config.set('Addresses', 'ServerURL', "False")
            elif Textbox_3.lower() == "true" or Textbox_3.lower() == "lims" or Textbox_3.lower() == "enable" or Textbox_3.lower() == "online" or Textbox_3.lower() == "on":
                try:
                    print(f"Setting ServerURL to: {config['Addresses']['DefaultServerURL']}")
                    Label4ServerURLResponse = f"Setting ServerURL to: {config['Addresses']['DefaultServerURL']}"
                    config.set('Addresses', 'ServerURL', config['Addresses']['DefaultServerURL'])
                except:
                    print("Error: No Default ServerURL Found")
                    Label4ServerURLResponse = "Nothing! - Error: No Default ServerURL Found..."        
            SubmissionResponse = {
            "Label 4":f"ServerURL is now {Label4ServerURLResponse}"
            }

        if ButtonPressed == "Button 1": 
            LocalVariableToSwitch = "False"
            if config["Addresses"]["OpenToLocalNetwork"] == "False":
                LocalVariableToSwitch = "True"
            config.set('Addresses', 'OpenToLocalNetwork', LocalVariableToSwitch)
            AdditionalWarning = ""
            if LocalVariableToSwitch == "True":
                AdditionalWarning = " - Security WARNING: Only enable this feature if you need to. Please turn this off if you don't need it. This feature allows other devices on your local network to connect to your LIMS Client, e.g your phone browser. This feature does not work yet - it is still in development!"
            SubmissionResponse = {
            "Label 4":f"OpenToLocalNetwork is now {str(config['Addresses']['OpenToLocalNetwork'])}{AdditionalWarning}."
            }

        if ButtonPressed == "Button 2": 
            LocalVariableToSwitch = "False"
            if config["Addresses"]["HotkeySidebar"] == "False":
                LocalVariableToSwitch = "True"
            config.set('Addresses', 'HotkeySidebar', LocalVariableToSwitch)
            SubmissionResponse = {
            "Label 4":f"HotkeySidebar is now {str(config['Addresses']['HotkeySidebar'])}. Press 'Z + C' to open the sidebar. "
            }
        

        if ButtonPressed == "Button 3":
        #Process SDUMP
            Textbox_3 = request.form.get("Textbox 3")
            if Textbox_3.find("START!!!!!") < 0 or Textbox_3.find("!!!!!S") < 8:
                SubmissionResponse = {"Label 4":str("Invalid SDump, make sure you include START!!!!! and !!!!!STOP")}

            else:
                SDump = Textbox_3[Textbox_3.find("START!!!!!")+10:Textbox_3.find("!!!!!S")]
                ExtractedURL =  SDump[:SDump.find("!!!!!-----")]
                if not ExtractedURL[-1:] == "/":
                    ExtractedURL+="/"
                EncryptionKey = SDump[SDump.find("!!!!!-----")+5:].replace("@@@@@","\n")
        #Set Server Config data from SDUMP
                OriginalWD = os.getcwd()
                os.chdir(os.path.join(os.getcwd(), "Sources", "VIPER"))
                with open("Server_Encrypt.pem","w") as ServerEncryptfile:
                        ServerEncryptfile.write(EncryptionKey)
                config.set('Addresses', 'DefaultServerURL', ExtractedURL)
                config.set('Addresses', 'ServerURL', ExtractedURL)
                print("New server details applied, restart VIPER.")
                SubmissionResponse = {"Label 4":str("Server details applied; please Log out and restart VIPER")}
                os.chdir(OriginalWD)


        if ButtonPressed == "Button 4": 
            LocalVariableToSwitch = "False"
            if config["Addresses"]["thirdpartyappintergration"] == "False":
                LocalVariableToSwitch = "True"
            config.set('Addresses', 'thirdpartyappintergration', LocalVariableToSwitch)
            AdditionalWarning = ""
            if LocalVariableToSwitch == "True":
                AdditionalWarning = " - Security WARNING: Only enable this feature if you need to. Please turn this off if you don't need it. This feature allows other locally hosted apps can use your login details for LIMS (e.g Jupyter Notebook)"
            SubmissionResponse = {
            "Label 4":f"Third Party App Intergration is now {str(config['Addresses']['thirdpartyappintergration'])}{AdditionalWarning}."
            }
            
        with open(os.path.join(os.getcwd(), "Sources", "VIPER", "Settings.ini"), 'w') as configfile:
            config.write(configfile)     
        os.chdir(OriginalSentDir)


    except:
        return '', 400 #If nothing happens, return nothing
    finally:        
        SubmissionResponse["Label 4"] += " You must LOG OUT to commit any changes."

        return jsonify(Info=SubmissionResponse) 