CreateNewSyncZIP= True         #SET THIS TO TRUE TO SYNC NEW VERSIONS

def ModuleName():
    return "VIPER_Sync"

def HostSyncSibFile(filename):
    return os.path.join( os.path.dirname(os.path.realpath(__file__)),'Host_Sync_Tool', filename)

#Import Modules
import time
from flask import jsonify
import json
import os
import subprocess
import shutil
#Import universal VIPER_Utility module
from VIPER_Utility import LIMSQuery, LogOutput, VIPER_GetRootDirectory
os.chdir( os.path.dirname(os.path.realpath(__file__)) )

VIPERSyncSharingRunning = [False]
VIPER_Sync_Host_Process = [False]      #Rename this to the Host Wrapper or something

def writeJson(filename,data):
    with open(HostSyncSibFile(filename), 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))

def readJson(filename):
    with open(HostSyncSibFile(filename), 'r', encoding='utf-8') as f:
        return json.loads(f.read())




def PrepareZIPFile(TreeToZip):
    import os
    import zipfile
        
    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), 
                                        os.path.join(path, '..')))

    OriginalCWD = os.getcwd()
    os.chdir(VIPER_GetRootDirectory())
    os.chdir("..")
    UberDirectory = os.getcwd()
    os.chdir(OriginalCWD)


    if CreateNewSyncZIP == True:
        os.mkdir(os.path.join(UberDirectory,"_VIPERZipTEMP"))
        with zipfile.ZipFile(os.path.join(UberDirectory,"_VIPERZipTEMP","VIPER_SyncFile.zip"), 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipdir(TreeToZip, zipf)
        if os.path.exists(HostSyncSibFile("VIPER_SyncFile.zip")):
            os.remove(HostSyncSibFile("VIPER_SyncFile.zip"))
        shutil.move(os.path.join(UberDirectory,"_VIPERZipTEMP","VIPER_SyncFile.zip"),HostSyncSibFile("VIPER_SyncFile.zip"))
        os.rmdir(os.path.join(UberDirectory,"_VIPERZipTEMP"))


if os.path.exists(HostSyncSibFile("DownloadApprovedUsers.json")):
    os.remove(HostSyncSibFile("DownloadApprovedUsers.json"))
if os.path.exists(HostSyncSibFile("DownloadRequestUsers.json")):
    os.remove(HostSyncSibFile("DownloadRequestUsers.json"))

def Process_User_Request(request):
    SubmissionResponse = None

    DownloadApprovedUsers = []
    if os.path.exists(HostSyncSibFile("DownloadApprovedUsers.json")):
        DownloadApprovedUsers = readJson("DownloadApprovedUsers.json")
    

    #for each button name, try queryrequest 
    try: #protect from request.form[name] not found and request failure
        ButtonPressed = request.form['SubmitButtonPressed']

        if ButtonPressed == "Button 0": 
            if len(request.form.get("Textbox 4")) > 2:

                if request.form.get("Textbox 4").lower == "stop":
                    if VIPER_Sync_Host_Process[0]:
                        VIPER_Sync_Host_Process[0].kill()
                    VIPER_Sync_Host_Process[0] = False


                #textbox syntax is "192.168.0.1 & 192.168.0.2 & etc"
                UsersToApproveRAW = '["'+request.form.get("Textbox 4").replace(r'&',r'","')+'"]'
                UsersToApprove = json.loads(UsersToApproveRAW) #json dumps conversion

                if len(UsersToApprove) > 0:
                    for x in UsersToApprove:
                        if not x in DownloadApprovedUsers:
                            DownloadApprovedUsers.append(x.strip())     
                writeJson("DownloadApprovedUsers.json",DownloadApprovedUsers)
                
            ApprovedDownloadersText = "No approved sync IPs"
            if len(json.dumps(DownloadApprovedUsers)) > 6: 
                ApprovedDownloadersText = "Approved downloaders:" + json.dumps(DownloadApprovedUsers)
                print("Approved Sync request from:" + json.dumps(DownloadApprovedUsers))                                      
                LogOutput("Approved Sync request from:" + json.dumps(DownloadApprovedUsers))

            SubmissionResponse = {
            "Label 2":ApprovedDownloadersText,
            }

        if ButtonPressed == "Button 1": 
            if not VIPER_Sync_Host_Process[0]:
                PrepareZIPFile(VIPER_GetRootDirectory())
                VIPER_Sync_Host_Process[0] = subprocess.Popen(f'python "{HostSyncSibFile("VIPER_Sync_Host.py")}"') #terrible solution...
                time.sleep(0.6) #wait for it to boot up...?

            ResponseText = "No users requesting sync access. "
            if os.path.exists(HostSyncSibFile("DownloadRequestUsers.json")):
                firsttime = True
                for r in readJson("DownloadRequestUsers.json"):
                    if firsttime:
                        ResponseText = "Download Requests: "
                        firsttime = False
                    ResponseText = f"{ResponseText}  {r} &"

            VIPERSyncLocalHostname = "Cannot identify my own IP Address..."
            VIPERSyncLocalHostnameQRCode = "No QR Code."

            if os.path.exists(HostSyncSibFile('VIPERLocalSyncHostname.txt')):
                with open( HostSyncSibFile('VIPERLocalSyncHostname.txt') ) as my_file:
                    VIPERSyncLocalHostname = my_file.read()

            if os.path.exists(HostSyncSibFile('VIPERLocalQRCode.svg')):
                with open( HostSyncSibFile('VIPERLocalQRCode.svg') ) as my_file:
                    VIPERSyncLocalHostnameQRCode = my_file.read()
        
            SubmissionResponse = {"Label 3":ResponseText[:-1],"Label 4":VIPERSyncLocalHostname,"Label 5":VIPERSyncLocalHostnameQRCode}

    except:
        return '', 400 #If nothing happens, return nothing
    finally:        
        return jsonify(Info=SubmissionResponse) 
