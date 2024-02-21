#VIPER Server#

#Import modules#
import os
os.chdir(os.path.join(os.getcwd(),"Server_Sources"))
import configparser
from cryptography.fernet import Fernet
import json
import rsa
import glob
SQLVerificationModule = True
try:
   import SQLVerification   
except ImportError:
   SQLVerificationModule = False

##Import FLASK SERVER##
from flask import Flask, request, redirect
from authlib.integrations.flask_oauth2 import ResourceProtector
from requests_oauthlib import OAuth2Session
from cheroot.wsgi import Server as WSGIServer
from cheroot.wsgi import PathInfoDispatcher as WSGIPathInfoDispatcher
from cheroot.ssl.builtin import BuiltinSSLAdapter

#Server Configuration
app = Flask(__name__)
config = configparser.ConfigParser()
config.read('Settings.ini')
Callback_URL = config["ResourceServer"]["Callback_URL"]
client_id = config["OAuth"]["OAuth_client_id"]
client_secret = config["OAuth"]["OAuth_client_secret"]
authorization_base_url = config["OAuth"]["OAuth_authorization_base_url"]
token_url =config["OAuth"]["OAuth_token_url"]
TokenLink = config["OAuth"]["OAuth_TokenLink"]                               #FUTURE UPDATE: make Oauth2 Customisable by settings.ini
OAuthScope = None
if not str.lower(config["OAuth"]["OAuth_Scope"]) == "none":    ##If .ini has multiple scope (e.g google)
        OAuthScope = [config["OAuth"]["OAuth_Scope"]]
OAuth_Session = OAuth2Session(client_id, redirect_uri=Callback_URL, scope=OAuthScope)    #Creates a session
require_auth = ResourceProtector()
EncryptToken = Fernet(Fernet.generate_key())   #Random key on boot-up, destroyed on shutdown

def VIPER_SDump_For_Client(RawCallbackURL):
    ServerEncryptString = ""

    originalcwd = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "Server_Sources","ServerKeys"))
    with open("Server_Encrypt.pem","r") as ServerEncryptfile:
        for encryptline in ServerEncryptfile.readlines():
            ServerEncryptString += encryptline[:-1]+"@@@@@"
        ServerEncryptString = ServerEncryptString[:-5]

    ##READ THIS WARNING##
    SDUMP = f"SDUMPSTART!!!!!{RawCallbackURL[:-9]}!!!!!{ServerEncryptString}!!!!!SDUMPSTOP"
    #WARNING ## WARNING ## WARNING#
    #NEVER try to exchange an SDUMP through a basic internet or network connection
    #If the SDUMP becomes TAMPERED with during transmission, the recipient may be subjected to a Man in the Middle attack
    #^User logins can be hijacked if this occurs
    #Always transfer SDUMP through a safe manner, ensure the RSA encryption key on the client end matches the server.
    #You can use an email service you trust, a USB device, or any form of secure communication.



    print("TO CONNECT NEW VIPER CLIENTS:")
    print("Copy the following output")
    print("including SDUMPSTART all the way to and including SDUMPSTOP")
    print(SDUMP)
    print("Run your VIPER_Client, go to Settings Panel -> Local Settings")
    print("Paste the SDUMP into the textbox, and then finally press the Autosetup Dump button")
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    with open("SDumps.txt","w") as SDumpFile:
        SDumpFile.write(SDUMP)
    os.chdir(originalcwd)



for OldClientKeys in glob.glob(os.path.join(os.getcwd(), "ClientKeys", "*")): 
    os.remove(OldClientKeys)

SecretStatesList = {}
NEVER_SHARE_ClientFernetKeys = {}

#Generates new keys if none are found
if not(os.path.exists(os.path.join(os.getcwd(), "ServerKeys", "NEVER_SHARE_THIS_FILE_Server_Decrypt.pem"))):     
    print("VIPER Decryption Key not found... Generating new keys")
    NEW_public_key, NEW_private_key = rsa.newkeys(1024)
#Create New Pair
    with open(os.path.join(os.getcwd(), "ServerKeys", "Server_Encrypt.pem"), "wb") as f: 
        f.write(NEW_public_key.save_pkcs1("PEM"))
    with open(os.path.join(os.getcwd(), "ServerKeys", "NEVER_SHARE_THIS_FILE_Server_Decrypt.pem"),"wb") as f:    
        f.write(NEW_private_key.save_pkcs1("PEM"))
    print("New VIPER_Encrypt.pem must be safely transferred to clients")

#Access 
with open(os.path.join(os.getcwd(), "ServerKeys", "NEVER_SHARE_THIS_FILE_Server_Decrypt.pem"), "rb") as f:   
    ServerPrivateKey = rsa.PrivateKey.load_pkcs1(f.read())

def VIPER_Encrypt(Message, UserToken:str):
    """Encrypts a message for the Client to recieve in response, using their personal Fernet secret

    Args:
        Message (str/bytes): Message to be Fernet Encrypted
        UserToken (str): The decrypted user Token which corrosponds to their personal Fernet secret

    Returns:
        str: Message encrypted with the personalised Fernet key shared secret for the client
    """
    if not type(Message) == type(b"b"):
        Message = Message.encode()
    return ((Fernet(NEVER_SHARE_ClientFernetKeys[UserToken])).encrypt( Message ))

def VIPER_Decrypt(EncryptedMessage, UserToken):
    """Decrypts a message from the Client when recieved from a request, using their personal Fernet secret

    Args:
        Message (str/bytes): Message to be Fernet Decrypted
        UserToken (str): The decrypted user Token which corrosponds to their personal Fernet secret

    Returns:
        str: Message decrypted with the personalised Fernet key shared secret from the client
    """
    return ((Fernet(NEVER_SHARE_ClientFernetKeys[UserToken])).decrypt(EncryptedMessage)).decode()

def VIPER_Server_RSA_Decrypt(Message:str):
    """Performs an Asymmetrical decryption using safe RSA keys
        Only to be used prior to creating a Shared Secret Fernet Key in the Greet request
    Args:
        Message (str): A short one-way message sent from the client to the server

    Returns:
        str: Decrypted short message
    """
    if len(Message) > 128:
        return VIPER_Server_RSA_Decrypt(Message[:128]) + VIPER_Server_RSA_Decrypt(Message[128:])
    return (rsa.decrypt(Message,  ServerPrivateKey)).decode()  #decode()?


#Flask Webpages
@app.route("/Greet", methods = ["POST"])
def Greet():    
    """An initial handshake performed by the Server and Client
    A login link is prepared alongside a temporary secret identity associated with the "state" of their LoginURL/authorization_url

    Returns:
        str: Login link for the OAuth2 Server, which will be passed through /callback
    """
    #Access temp files to create some semi-permenant files under unknown names
    RequestData = json.loads(VIPER_Server_RSA_Decrypt(request.data))
    ClientStateSecret = RequestData["StateSecret"]
    Never_Share_ClientFernetKey = (RequestData["SharedFernetKey"]).encode()
    
    #Server sends back confirmation message containing the log-in link (e.g "secure transport ready)
    authorization_url, state = OAuth_Session.authorization_url(authorization_base_url)
    if ClientStateSecret in SecretStatesList or ClientStateSecret in NEVER_SHARE_ClientFernetKeys:
        return "Error: State Secret ID Already Registered"
    NEVER_SHARE_ClientFernetKeys[ClientStateSecret] = Never_Share_ClientFernetKey
    SecretStatesList[ClientStateSecret] = state ##for later
    return (Fernet(Never_Share_ClientFernetKey)).encrypt(authorization_url.encode())

@app.route("/callback")
def callback():
    """After completing OAuth2 login, this will redirect the user to their local VIPER_Client which will engage /CompleteToken to finish the UserInfo cookie in the web browser
   
   Returns:
        str: Redirects the client to their VIPER_Client address whilst appending the successful login Token callback URL so the VIPER_Client can capture the callbackURL
    """
    print("Redirecting :" + str(request.url))
    return redirect("http://127.0.0.1:7800/callback?q="+str(request.url), code=302)

@app.route("/ConfirmIdentity", methods = ["POST"])
def ConfirmIdentity():
    """Final login step where a Client Token is obtained from the OAuth2 server and old temporary information (from Greet) is destroyed
    The Fernet Key Shared Secret is linked with the Client Token, only messages encrypted with the correct Fernet Key for the relative Client Token will be processed

    Returns:
        str: Users encrypted Client Token which can be used to send OAuth2 authorised requests to the /LIMS service
    """

    DecryptedCallback = VIPER_Server_RSA_Decrypt(request.data[:128]) + VIPER_Server_RSA_Decrypt(request.data[128:])
    req = json.loads(DecryptedCallback) 
    ClientCompletedLoginLink = req["TokenURL"] #Will contain their encrypted PublicKey -- put a ["NothingAfterHere"] to trim
    ClientStateSecret = req["StateSecret"]
    URLState = ClientCompletedLoginLink[ClientCompletedLoginLink.find("state=")+6:] ##FIX THIS
    if SecretStatesList[ClientStateSecret] == URLState and len(URLState)>3 : #or whatever, do a state.find
        try:
            #SECURITY FLAW: someone can spoof the start of Token_url, intercept with garbage
            #^to fix, force the start of the token_url the same as our OAuth2 sever
            #^still flaw? they could have a redirect on the OAuth2 which they can use to sneak a fake token
            if str.find(token_url,"linkedin") > 2:
                z = OAuth_Session.fetch_token(token_url, client_secret=client_secret, include_client_id=True, authorization_response=ClientCompletedLoginLink)
            else:
                z = OAuth_Session.fetch_token(token_url, client_secret=client_secret, authorization_response=ClientCompletedLoginLink)
            #include_client_id=True if using Linkedin^
        except:
            return VIPER_Encrypt("Invalid Token", ClientStateSecret)
        else:
            ClientToken = z["access_token"]  #Already encoded!
            NEVER_SHARE_ClientFernetKeys[ClientToken] = NEVER_SHARE_ClientFernetKeys[ClientStateSecret]
            NEVER_SHARE_ClientFernetKeys[ClientStateSecret] = None
            SecretStatesList[ClientStateSecret] = None
            
            return VIPER_Encrypt( EncryptToken.encrypt(ClientToken.encode()) , ClientToken)
    return "State Secret Not Registered"



@app.route("/RawTextOauthLogin", methods = ["POST"])
def RawTextOauthLogin():
    """Returns an OAuth2 login link 
    
    Returns:
        str: An OAuth2 login link, which will redirect to /callback when completed
    """
    
    print("Manual Login requested")
    authorization_url, state = OAuth_Session.authorization_url(authorization_base_url)
    print(authorization_url)
    return 

@app.route("/")
def ClientAsksForPublicKey():
    return RawTextOauthLogin()
    
@app.route("/LIMS", methods = ["POST"])
def LIMS():
    """Handles requests between VIPER_Clients and VIPER_Server, all client VIPER_modules will parse information through here
        If the VIPER_Token is valid then the request is processed by the SQLVerification module
    Returns:
        json¦str: Response from SQL Verification module, or an error message
    """
    
    #send file:
        #1. Encryption { ZIP File ( File, Token) }  Each file must have a token to be validated
    
    #Split the request into components
    RequestJSON = request.json
    EncryptedUserToken = RequestJSON["Token"]
    UserToken = EncryptToken.decrypt(EncryptedUserToken.encode()).decode() #If you see ^Invalid Token then this your problem is fetch_token

    req = json.loads( VIPER_Decrypt((RequestJSON["Info"]).encode() , UserToken) )
    #^Even if someone has the token, only way to write to the token table is to get it from an OAuth2 completion URL
    

    #Verify the user
    headers = {"Authorization": "Bearer "+str(UserToken)}
    VerifyAccessToken = OAuth_Session.get(TokenLink, headers=headers)
      
    #Prepare the SQL Request array
    SQLRequest = {}
    SQLRequest["AccessToken"] = VerifyAccessToken
    SQLRequest["Method"] = req.get("Method")
    SQLRequest["Command"] = req.get("SQLCommand")
    SQLRequest["Database"] = req.get("Database")
    

    if VerifyAccessToken.reason == "OK" and VerifyAccessToken.ok == True and NEVER_SHARE_ClientFernetKeys.get(UserToken) is not None:
#USER AUTHENTICATED COMMUNICATION STARTS HERE##
#The user IS who they claim to be, assuming decryption keys are not compromised
#IMPORTANT: We have not yet validated if the user has permission or is even associated with our institution, this is performed in SQLVerification
        if request.method == "POST":
            
            #Special Requests#
            #Logout
            if req.get("SQLCommand")=="Logout" and req.get("Database")=="Logout" and req.get("Method")=="Logout":  
                FakeResponse = VIPER_Encrypt("Client Fernet Key destroyed, you are logged out.", UserToken)
                try:
                    NEVER_SHARE_ClientFernetKeys.pop(UserToken) #Destroy the user login details
                    print(str(VerifyAccessToken.json()["id"]) + " has safely logged out.")
                finally:
                    return FakeResponse #We fake a response so man in the middle exploiters don't know logout requests were sent - better security
            #Get own UserID
            if req.get("SQLCommand")=="UserID" and req.get("Database")=="UserID" and req.get("Method")=="UserID":  
                UserJson = VerifyAccessToken.json()
                Response = {
                    "id" : str(UserJson["id"]),
                    "login" : UserJson["login"],
                    }
                print(str(UserJson["id"]) + " has verified their UserID.")
                return VIPER_Encrypt( json.dumps(Response) , UserToken)


            #Process request#
            if SQLVerificationModule: #User can provide custom security & permissions module
                SQLResponse = SQLVerification.Verify(SQLRequest)
                return VIPER_Encrypt(json.dumps(SQLResponse), UserToken)
            else:
                return VIPER_Encrypt(json.dumps({"Output":"No SQL module called #SQLVerification.py# with #def Verify()# found within Server.py's folder..."}), UserToken)
    else:
        return VIPER_Encrypt(json.dumps({"Output":"Token is Invalid - Restart LIMS and Login Again"}), UserToken)
##END OF AUTHENTICATED USER COMMUNICATION##     



my_app = WSGIPathInfoDispatcher({'/': app})
server = WSGIServer(('0.0.0.0', 8000), my_app)

#Make a fake Certificate and Key
ssl_cert = os.path.join(os.getcwd(), "ServerKeys", "VIPER_Certificate.crt")
ssl_key = os.path.join(os.getcwd(), "ServerKeys", "VIPER_Certificate_Key.key")
server.ssl_adapter =  BuiltinSSLAdapter(ssl_cert, ssl_key, None)

if __name__ == '__main__':
   try:
      VIPER_SDump_For_Client(Callback_URL)
      print("\n\n\n")
      print("SERVER RUNNING...")
      server.start()
   except KeyboardInterrupt:
      server.stop()


