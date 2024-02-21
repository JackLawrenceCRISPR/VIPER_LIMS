CompatibilityMode = True
port=8004   #share same port as VIPER? Maybe?
host = '0.0.0.0'

def getModuleZipName():
    return "VIPER_SyncFile.zip"


def Try_MakeQRCode(QRCodeLink:str="none"):  # MODIFIED FOR SIMPLICITY
    TempSVGpath = os.path.join(os.getcwd(),'VIPERLocalQRCode.svg')

    TempHostnametextpath = os.path.join(os.getcwd(),'VIPERLocalSyncHostname.txt')
    hostnametextfile = open(TempHostnametextpath, "w")
    hostnametextfile.write(QRCodeLink)
    hostnametextfile.close()

    try:
        #import segno -> create a QR code -> save it to a temp file -> read -> delete file -> return SVG text
        import segno
        qrcode = segno.make(QRCodeLink)
        qrcode.save(TempSVGpath, border=0, scale=8)  # No border
        return False
    
    except ImportError:
        if os.path.exists(TempSVGpath):
            os.remove(TempSVGpath)
        return False


import os
os.chdir( os.path.dirname(os.path.realpath(__file__)) )
import json

def SibFile(filename):
    return os.path.join( os.path.dirname(os.path.realpath(__file__)),filename)

def writeJson(filename,data):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))

def readJson(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.loads(f.read())
    





writeJson("DownloadApprovedUsers.json",[])
writeJson("DownloadRequestUsers.json",[])

# HIGH LEVEL FLASK INSTANCE # HIGH CONSISTENCY WITHIN VIPER #
def VIPERSyncSharingFLASK(FileToSend):
    from flask import Flask, send_file, request
    VIPERSyncSharingApp = Flask(__name__)

    @VIPERSyncSharingApp.route('/sync')
    def syncroute():
        if not os.path.exists(os.path.join(os.getcwd(),"DownloadApprovedUsers.json")):  #shut down upon deleting DownloadAPprovedUsers.json, as a backup measure
            import sys
            sys.exit()

        DownloadApprovedUsers = readJson("DownloadApprovedUsers.json")
        DownloadRequestUsers = readJson("DownloadRequestUsers.json")

        RequestUser = str(request.remote_addr)
        if RequestUser in DownloadApprovedUsers:
            print("Sending VIPER Sync to: " + RequestUser)
            return send_file(os.path.join(os.getcwd(),getModuleZipName()), as_attachment=True)        
        else:
            if not RequestUser in DownloadRequestUsers:
                DownloadRequestUsers.insert(len(DownloadRequestUsers),RequestUser)
                print(DownloadRequestUsers)
                writeJson("DownloadRequestUsers.json",DownloadRequestUsers)
                return """<H1>Permission requested...</H1> <button onClick="window.location.href=window.location.href">Click to download when approved...</button>"""
            else:
                return """<H1>Permission requested...</H1> <button onClick="window.location.href=window.location.href">Click to download when approved...</button>"""
            
    print("sync Hosting available...")
    VIPERSyncSharingApp.run(host="0.0.0.0", port=int(port))


# LOW LEVEL NET SOCKET # HIGH COMPATIBILITY ACROSS PYTHON ENVIRONMENTS#
def VIPERSyncSharingSOCKET():
    def SocketSendZip(clientsocket,FileToSend):
        header="HTTP/1.1 200 OK"
        header1="Content-Type: application/zip"
        header2="Content-Length: {}".format(os.stat(FileToSend).st_size)
        blank="\r\n"

        sendt=header+"\r\n"+header1+"\r\n"+header2+"\r\n"+blank
        clientsocket.sendall(sendt.encode())

        file=open(FileToSend,'rb')
        z=file.read(512)
        while (z):
            try:
                clientsocket.sendall(z)
                z=file.read(512)
            except:
                print("Complete")
                exit()


    def SocketSendHTML(cleintsocket,FileToSend):
        f = open(FileToSend, 'r') 

        cleintsocket.sendall(str.encode("HTTP/1.0 200 OK\n",'iso-8859-1'))
        cleintsocket.sendall(str.encode('Content-Type: text/html\n', 'iso-8859-1'))
        cleintsocket.send(str.encode('\r\n'))
        # send data per line
        for l in f.readlines():
            #print('Sent ', repr(l))
            cleintsocket.sendall(str.encode(""+l+"", 'iso-8859-1'))
            l = f.read(1024)
        f.close()


    os.chdir( os.path.dirname(os.path.realpath(__file__)) )
    import socket
    serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)


    serversocket.bind((host,port))
    serversocket.listen(5)

    Try_MakeQRCode(f"http://{str(socket.gethostbyname(socket.gethostname()))}:{str(port)}/sync") #this makes http://xx.xx.xx.xx:7800 for example


    def runServer():
        (clientsocket, address) = serversocket.accept()
        RequestUser = address[0]
        clcommand=clientsocket.recv(1024).decode('utf8')

        #for hosted files check:
        if (RequestUser != None) and (f"/sync" in clcommand):
            if RequestUser in readJson("DownloadApprovedUsers.json"):
                SocketSendZip(clientsocket,SibFile(getModuleZipName()))
            else:
                DownloadRequestUsers = readJson("DownloadRequestUsers.json")
                if not RequestUser in DownloadRequestUsers:
                    DownloadRequestUsers.insert(len(DownloadRequestUsers),RequestUser)
                    writeJson("DownloadRequestUsers.json",DownloadRequestUsers)
                    print(f"{RequestUser} request sync permission.")
                else:
                    print(f"{RequestUser} already requested sync permission.")
                SocketSendHTML(clientsocket,SibFile("VIPER_Sync_Host_Page.html"))
        clientsocket.close()

    while True:
        runServer()



if CompatibilityMode:
    VIPERSyncSharingSOCKET()
else:
    VIPERSyncSharingFLASK()