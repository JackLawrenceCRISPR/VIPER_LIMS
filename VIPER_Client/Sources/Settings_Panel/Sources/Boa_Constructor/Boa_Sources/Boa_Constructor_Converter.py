#have to have a bit say "press ctrl+s and save it to the VIPER/Boa_Constructor/folder under -webpage.html- (detect any "html" file to convert)

#search for new module?
#DO POSITIONS
import math
import glob, os

def ReadFileContents(Filename):
    file = open(Filename, "r")
    FullRawContents = file.read() 
    file.close()
    return FullRawContents

def ConstructVIPERModule(RefName,FolderDir=False,FileToTransform=False):
    if FolderDir:
        if FolderDir.find(r'id="PageConfigurator"') < 0:
            os.chdir(FolderDir)
    if os.path.basename(os.getcwd())=="Sources":
        os.chdir("Boa_Constructor")
        os.chdir("Boa_Sources")
    if FolderDir.find(r'id="PageConfigurator"') < 0 and not FileToTransform:
        FileToTransform = os.path.join(os.getcwd(), "/NewVIPERModule.html")
    FullRawHTML = FolderDir

    if FolderDir.find('id="PageConfigurator"') < 0:
        FullRawHTML = ReadFileContents(FileToTransform)
    PageConfigRaw = FullRawHTML[FullRawHTML.find("PageConfigurator"):]
    PageConfigRaw = PageConfigRaw[:PageConfigRaw.find(r"</p>")]

    cardWidth = PageConfigRaw[PageConfigRaw.lower().find("cardwidth=")+11:]
    cardHeight = PageConfigRaw[PageConfigRaw.lower().find("cardheight=")+12:]
    pageWidth = PageConfigRaw[PageConfigRaw.lower().find("pagewidth=")+11:]
    pageHeight = PageConfigRaw[PageConfigRaw.lower().find("pageheight=")+12:]

    cardWidth = int(cardWidth[:cardWidth.find(r'"')])
    cardHeight =  int(cardHeight[:cardHeight.find(r'"')])
    pageWidth =  int(pageWidth[:pageWidth.find(r'"')])
    pageHeight =  int(pageHeight[:pageHeight.find(r'"')])

    MasterPageSize = 2000
    HWRatio = cardHeight/cardWidth
    cardWidth = math.floor(MasterPageSize/pageWidth) #vw both height and width
    cardHeight = math.floor( (MasterPageSize/pageWidth)*HWRatio)


    #we need font size too?

    #data-cardwidth="100" data-cardheight="100" data-pagewidth="5" data-pageheight="5"

    RawHTML = FullRawHTML[FullRawHTML.find("vGe6uHl8Kg2ACtT"):] #<-- content detection phrase
    t = RawHTML[RawHTML.find("<div")+3:] #t=trimmed html
    StandardPythonFileContents = ReadFileContents("Generic_VIPER_Module.txt")
    StandardPythonFileContents = StandardPythonFileContents.replace("VIPER_Module_Script",RefName+"_Module_Script").replace("VIPER_Module_Homepage",RefName+"_Homepage")
    HTMLtop = ReadFileContents("VIPER_Constructor_Top_HTML.txt")+ r'<div id="content" style="width: 2000px;">'
    HTMLtop = HTMLtop.replace("<head>","<head>") #Add in the style sheet here later
    HTMLbottom = r'</div>'+ReadFileContents("VIPER_Constructor_Bottom_HTML.txt")
    AdditionalUniquePythonCode = ""
    pythonBottomHalf = """
    except:
        return '', 400 #If nothing happens, return nothing
    finally:        
        return jsonify(Info=SubmissionResponse) """

    HelpfulAdvice = f"""             #WRITE CODE HERE
            #QueryRequest = #BoxInfoStuff
            #Output = json.loads( LIMSQuery(request, "sakila", QueryRequest, "fetchall") )                   #example backend SQL request
            #LogOutput(Output, ModuleName(), os.getcwd()+r"\Logs")                                                                 #example log result \n"""

    HelpfulAdviceMinimal = f"""            #WRITE CODE HERE \n\n\n\n"""
    
    

  
    #Process your constructor
    FinalObjectLibrary = {}
    FinalObjectLibrary["Textbox"] = r""
    FinalObjectLibrary["Label"] = r""
    FinalObjectLibrary["Button"] = r""
    FinalObjectLibrary["Div"] = r""
    FinalObjectLibrary["Image"] = r""
    FinalObjectLibrary["ChartJS"] = r""
    FinalObjectLibrary["Mermaid"] = r""
    

    ObjectLibrary = {}
    ObjectLibrary["Textbox"] = """ <input name="!ID!" id="!ID!" class="Textbox" type="text" style="!TFORM!" value=""/> \n""" #name=2buttonname
    ObjectLibrary["Label"] = """<p name="!ID!" id="!ID!" class="Label" style="!TFORM!" value=""></p> \n"""                               #id=3responseid
    ObjectLibrary["Button"] = """<input name="!ID!" id="!ID!" class="Button" type="submit" style="!TFORM!" value=""/> \n"""          #id=button 1
    ObjectLibrary["Div"] = """<div name="!ID!" id="!ID!" class="div" style="!TFORM!"></div> \n"""
    ObjectLibrary["Image"] = r"""<img src="" alt="!ID!" name="!ID!" id="!ID!" class="Image" style="!TFORM!" value="">""" + f"\n"   #width="600" height="600"?
    ObjectLibrary["ChartJS"] = """<canvas id="myChart" style="!TFORM!"></canvas>"""
    ObjectLibrary["Mermaid"] = """<pre name="!ID!" id="!ID!" class="mermaid" style="!TFORM!">
    graph LR
    A --- B
    B-->C[fa:fa-ban forbidden]
    B-->D(fa:fa-spinner);
</pre>\n"""

    def HandleHTMLObject(ObjectInfo):
        CardLeft=ObjectInfo["Position"][0]*cardWidth
        CardTop=ObjectInfo["Position"][1]*cardHeight
        ObjectTransformation = f'height:{cardHeight}px; width:{cardWidth}px; position: absolute; top:{CardTop}px; left:{CardLeft}px;' # style="width:1000px; height:100px"
        NewObject = ObjectLibrary[ObjectInfo["Type"]]       #Get the default object code
        NewObject = NewObject.replace("!TFORM!", ObjectTransformation)       #Position the objects
        NewObject = NewObject.replace("!ID!", ObjectInfo["Name"])       #Label the code with the unique button name

        #special object config
        if ObjectInfo["Type"] == "ChartJS":
            NewObject += r"<script>{{ "+ ObjectInfo["Name"].replace(" ","_") +r" |safe }}</script>"

        FinalObjectLibrary[ObjectInfo["Type"]] += NewObject #Add the new object to it's category for later 

    IdentityList = {}   #Get an object by their ID (if we need to?)
    AllGroupList = {}   #UQOB -> UQOB12321, UQOB2412421
    ButtonTypeList = []
    ImageTypeList = []

    def HandlePythonSubmission(ObjectInfo):
        ####SPACES ARE VERY IMPORTANT IN PYTHON CODE###
        ModuleUniquePythonCode = f"""\n\n\n        if ButtonPressed == "{ObjectInfo["Name"]}": \n"""
        
        ModuleUniqueVariableDeclarations = r""
        ResponseObjects = r"" 
        if  AllGroupList.get(ObjectInfo["UQOB"]):
            for AssociatedObject in AllGroupList[ObjectInfo["UQOB"]]:
                AssociatedObjectName = IdentityList[AssociatedObject]["Name"]
                PythonSafeName = AssociatedObjectName.replace(" ","_")
                ModuleUniqueVariableDeclarations += f"""            {PythonSafeName} = request.form.get("{AssociatedObjectName}")\n"""          #
                ResponseObjects += f"""            "{AssociatedObjectName}":"New innerHTML",\n"""

            ResponseObjects = "{\n"+ResponseObjects+"            }\n" 
            SubmissionResponse = f"""            SubmissionResponse = {ResponseObjects}"""
            return ModuleUniquePythonCode+ ModuleUniqueVariableDeclarations+"\n\n"+ HelpfulAdvice+"\n\n"+ SubmissionResponse
        return ""
    #{"3ResponseID":Output}#<-- write this string for each of the "response" elements we have 


    HTMLObjectsUsed = set() #for keeping track of all unique HTML elements
    while t.find("<div") > -1 :
        oi = {} #object info                        ###UQOB, Type, Name, Groups, Position[x,y]
        t = t[t.find("<div")+3:]
        CurrentObject = t[:t.find("</div")]

        #Populate Object Info:
        #p = Point of interest = find(start phrase)
        #oi["Property"]= {Trim everything from start-phrase to find(endphrase)}
        p = CurrentObject.find("UQOB")
        oi["UQOB"] = t[p:][:t[p:].find(" ")] # get UQOB 
        
        p = t.find(r"data-viperobjectgroups")+24
        if t[p:p+1] == r'"':
            oi["Groups"] = ""
        else:
            oi["Groups"] =  t[p:][:t[p:].find('\"')]      ##MAKE IT SO if the entry is "" empty, we make it "false"                                                 ########################################################   

        p = t.find("data-viperposition")+20
        ObjectPagePosition =  t[p:][:t[p:].find('\"')]
        
        p = t.find("data-buttontype")+17
        oi["ButtonType"] =  t[p:][:t[p:].find('\"')] #not needed?
        
        
        p = t.find(r'id="')+4
        oi["Type"] =  t[p:][:t[p:].find('\"')]    
            
        p = t.find(r'">')+2
        oi["Name"] =  t[p:][:t[p:].find('</div')]
        #Object Info (oi populated)
        oi["Position"] = [ math.floor(int(ObjectPagePosition)%pageWidth), math.floor(math.floor(int(ObjectPagePosition)/pageWidth))] #X,Y coords
        IdentityList[oi["UQOB"]] = oi
        if oi["ButtonType"] == "1":
            ButtonTypeList.append(oi)

        HTMLObjectsUsed.add(oi["Type"]) #keep track of all unique elements used
        HandleHTMLObject(oi)
        if oi["Type"] == "Image":
            ImageTypeList.append(oi)

        #Link Groups Together
        GroupsText = oi["Groups"]
        if len(GroupsText) > 1:

            #Transform "UQOB12098321 UQOB7129032" -> ["UQOB12098321","UQOB7129032"]
            MyGroupsList = []
            StillMoreGroups = True
            while StillMoreGroups:
                while GroupsText.find(" ") == 0:
                    GroupsText = GroupsText[1:]
                TrimPoint = GroupsText.find(" ")    
                if TrimPoint > 3:
                    MyGroupsList.append(GroupsText[2:TrimPoint]) #skip " MX" before "UQOB"
                    GroupsText=GroupsText[TrimPoint:]
                else:
                    StillMoreGroups = False
                    MyGroupsList.append(GroupsText[2:])
                    GroupsText=""

            #Find my friends, add myself to their association indexes
            if AllGroupList.get(oi["UQOB"]) == None:
                AllGroupList[oi["UQOB"]] = set() 

            for group in MyGroupsList:
                if AllGroupList.get(group) == None:
                    AllGroupList[group] = set()
                AllGroupList[group].add(oi["UQOB"])
                AllGroupList[oi["UQOB"]].add(group)
            
        
    ModuleUniquePythonCode = f"""def ModuleName():
    return "{RefName}"

#Import Modules
from flask import jsonify
import json
import os

#Import universal VIPER_Utility module
OriginalDir = os.getcwd()
os.chdir("..")
os.chdir("VIPER")
from VIPER_Utility import LIMSQuery, LogOutput
os.chdir(OriginalDir)

#Response Script:
def Process_User_Request(request):

    SubmissionResponse = None

    #for each button name, try queryrequest 
    try: #protect from request.form[name] not found and request failure
        ButtonPressed = request.form['SubmitButtonPressed']
"""

    for ButtonObject in ButtonTypeList:
        ModuleUniquePythonCode+=HandlePythonSubmission(ButtonObject)
        HelpfulAdvice = HelpfulAdviceMinimal #On subsequent rounds, put less advice

    #Make list of GroupList[UQOB] = (All UQOBs I associate with)
    #Upon reading Groups break it down into a list []
    #for each friend in list:
    #GroupList[friend] = [OtherGroups] 












    PrecedingElementList = {}
    #put these in the order you want them to be written
    PrecedingElementList["ChartJS"] = """<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.js"></script>"""
    PrecedingElementList["Mermaid"] = """<script type="module"> import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs'; 

(function(global){
function RefreshMermaid() {mermaid.run()}

global.MermaidJavascriptModuleFunctions = {
	RefreshMermaid: RefreshMermaid
    }
})(window)
</script>  \n"""

    PrecedingElements = "<!--- Unique Preceding Elements: ---> \n"
    #Add any extra global JS dependencies into the PrecedingElements
    for Element, ElementPrecedingHTML in PrecedingElementList.items():
        if Element in HTMLObjectsUsed:
            PrecedingElements+=ElementPrecedingHTML

    #Write code
    #HTML
    AntiFLIMSRefText = r"{{LIMSRef}}"
    ModuleUniqueHTMLCode = f""" \n {PrecedingElements} \n \n <!---Unique Module Code---> \n
<form name="VIPERForm", id="VIPERForm", value="{AntiFLIMSRefText}/InduceButton">														
                        <input value="None" name="SubmitButtonPressed" id="SubmitButtonPressed" style="display:none;"></p>
            
                        <!---EVERY DIV--->
                        {FinalObjectLibrary["Div"]}
                        <!---EVERY TEXT BOX--->
                        {FinalObjectLibrary["Textbox"]}
                        <!---EVERY TEXT LABEL--->
                        {FinalObjectLibrary["Label"]}
                        <!---EVERY MERMAID--->
                        {FinalObjectLibrary["Mermaid"]}
                    </form>

                    <!---EVERY IMAGE--->
                    {FinalObjectLibrary["Image"]}
                    
                    <!---EVERY CHARTJS--->
                    {FinalObjectLibrary["ChartJS"]}

                    <!---EVERY BUTTON--->
                    {FinalObjectLibrary["Button"]}



    """



    if "Image" in HTMLObjectsUsed:
        AdditionalUniquePythonCode += """\n
def Static_Elements():
        return { #Put your images in the Static folder to access them
            #List of static elements\n"""
        for ImageElement in ImageTypeList:
            AdditionalUniquePythonCode+=f'            "{ImageElement["Name"]}" : "image.jpg",\n'
        AdditionalUniquePythonCode +="""        }"""



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

    #Create Files
    OriginalDir = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    os.chdir("..")
    os.chdir(GetHighestSources(os.getcwd()))
    FinalFolder = os.path.join(os.getcwd(), RefName)
    if not os.path.exists(FinalFolder):
        os.mkdir(FinalFolder)
    os.chdir(FinalFolder)

    os.mkdir(os.path.join(FinalFolder,"Static"))
    os.mkdir(os.path.join(FinalFolder,"Static","TEMP"))
    PythonFile = open(RefName+"_Module_Script.py", "w") 
    HTMLFile = open(RefName+"_Homepage.html", "w")
    OldConstructFile = open(RefName+"_OriginalDesign.html","w")
    INACTIVEF = open("INACTIVE","w")
    INACTIVEF.write("INACTIVE")
    INACTIVEF.close()
    GenericPythonFile = open(RefName+"_VIPER_Module.py", "w")
    GenericPythonFile.write(StandardPythonFileContents)
    GenericPythonFile.close()

    OldConstructFile.write(FullRawHTML)
    PythonFile.write(ModuleUniquePythonCode+pythonBottomHalf+AdditionalUniquePythonCode)
    HTMLFile.write(HTMLtop+ModuleUniqueHTMLCode+HTMLbottom)
    PythonFile.close()
    HTMLFile.close()
    OldConstructFile.close()
    if FileToTransform:
        os.remove(FileToTransform)
    print("New Module Created: "+RefName)
    return os.getcwd()

if __name__ == '__main__':
    print("Name your module:")
    RefName = input()
    for file in glob.glob("*.html"):
        if file.find("VIPER-Constructor.html")==-1:
            ConstructVIPERModule(RefName,file)
