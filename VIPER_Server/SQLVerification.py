#Example custom SQL Verification
#This script allows a completely customisable interrogation of the Request and Oauth2 verified User data

import configparser
import os
import json
import datetime
datetimeclass = type(datetime.datetime.now())
config = configparser.ConfigParser()
config.read('Settings.ini')
config.set('Database', 'Type', config["Database"]["SQLType"].lower())  #Standardise and speed up requests
PermissionListFile = os.path.join(os.getcwd(),"ExampleUserPermissions.json")
#List of people who are associated with your organisation [You could pull this table from somewhere else, even an SQL database of users]

def RefreshPermissionList():
    return json.loads( (open(PermissionListFile, "r")).read() )

PermissionList = RefreshPermissionList()


#Configure PermssionTypes
SPG = {
    "Important": {"Senior Scientist"},
}  
#SPG["Combined"] = {"Scientist"}.update(SPG["Important"]).update(SPG["Not Important"])

#Optimisation note: 
# 1. Lists are faster to iterate through than sets
# 2. Sets are faster to "in" than lists
#This is why SPG uses sets (to check who is "in") vs user permission list which is iterated through

SQLMethods = {}

###################################################################################################################################################################################################################################################################################
###################################################################################################################################################################################################################################################################################
###################################################################################################################################################################################################################################################################################
###################################################################################################################################################################################################################################################################################
###################################################################################################################################################################################################################################################################################

#SQL Request Methods

def GetMethod(LIMSdb, SQLRequest):
    """Defines a list of LIMS Server Methods with the associated permission groups and a description of their function. Only Methods for which the user has permission to execute are listed.
    
    Parameters: None
    
    Returns: [Method, Permission Groups, Description of Method]"""
    MyTempAvailableMethodKeys = set()
    TempListSQLMethods = SQLMethods
    RequestedMethod = str(SQLRequest["Command"])
    if SQLRequest["Command"]:
        if SQLMethods.get(RequestedMethod) is None:
            return "No Method found for " + str(RequestedMethod)
        TempListSQLMethods = {RequestedMethod: SQLMethods.get(RequestedMethod)}

    for MethodKey, SQLMethod in TempListSQLMethods.items():
        for UserPermission in SQLRequest["Permission"]:
            if isinstance(SQLMethod[1], str): #String type permission? -> Method Group
                RequestPermitted = (UserPermission in SPG[SQLMethod[1]])
                #^Permission group type -> Is my authorisation type found in the Permission Group?
            else: #List type permission -> Check list directly
                RequestPermitted = (UserPermission in SQLMethod[1])
                if SQLMethod[1][0] == "all":  #if all users are permitted
                    RequestPermitted = True
                #^permission list tyep -> is my authorisation found in the custom permission list?
            if RequestPermitted:
                MyTempAvailableMethodKeys.add(MethodKey)

    #^to ensure there are no repeats in the table

    TempMethodTable = []
    for k, v in SQLMethods.items():
        if k in MyTempAvailableMethodKeys:
            #remove "v[1]," if you do not want permission groups communicated 
            TempMethodTable.append( [k,v[1],str(v[0].__doc__) ] ) 
    

    return list(TempMethodTable)

def GetAllMethods(LIMSdb, SQLRequest):
    """Defines a list of every LIMS Server Method with the associated permission groups and a description of their function.
    
    Parameters: None
    
    Returns: [Method, Permission Groups, Description of Method]"""
    TempMethodTable = []
    for k, v in SQLMethods.items():
        TempMethodTable.append( [k,v[1],str(v[0].__doc__) ] )
    return TempMethodTable

def fetchall(LIMSdb, SQLRequest):
    """A simple fetch command for the Sakila test SQL database.
    
    Parameters: First name of Actor from Sakila test database.
    
    Returns: A list of Actors with the input first name."""
    if not LIMSdb:
        return "Invalid Database requested"
    
    myresult = "Only letters and numbers permitted." #basic injection protection     
    if SQLRequest["Command"].isalnum():
        mycursor = LIMSdb.cursor()

        mycursor.execute(f"SELECT * FROM actor WHERE first_name ='{SQLRequest['Command'].strip()}'")    #delete this line when using python-sql
        myresult = mycursor.fetchall()      #delete this line when using python-sql

        #Is there a better way to clean datetimes?!?   
        for entryiter, entry in enumerate(myresult):
            if type(entry)==type( () ):
                myresult[entryiter] = list(entry)
                for Xiter, X in enumerate(entry):
                    if type(X)==datetimeclass:              
                        myresult[entryiter][Xiter] = X.strftime("%m/%d/%Y, %H:%M:%S")        
    return myresult

def writenew(LIMSdb, SQLRequest):
    """A simple insert command for the Sakila test SQL database.
    
    Parameters: [First_Name, Last_Name]
    
    Returns: The inserted row number, First name and Last name"""
    myresult = "Only letters and numbers permitted."
    mycursor = LIMSdb.cursor()
    NewEntryInfo = SQLRequest["Command"]
    if NewEntryInfo[0].isalnum() and NewEntryInfo[1].isalnum():
        sql = "INSERT INTO actor (first_name, last_name) VALUES (%s, %s)"
        val = (NewEntryInfo[0], NewEntryInfo[1])
        mycursor.execute(sql, val)
        LIMSdb.commit()
        myresult = mycursor.rowcount
    return myresult

def updateuser(LIMSdb, SQLRequest):
    """Sets the Permission Groups for a user Login ID
    
    Parameters: [Login ID, Permissions]
    
    Returns: Login ID is now: Permissions"""
    #todo: make a system for "temporary" users / elevated permissions on a timer, maybe if "Senior Scientist !!date" <_ expires on this date
    NewUserInfo = SQLRequest["Command"] #Command structure -> [ "UserID", ["Senior Scientist"] ]
    PermissionList[ NewUserInfo[0] ] = NewUserInfo[1]
    (open(PermissionListFile, "w")).write( json.dumps(PermissionList) )
    #PermissionList = RefreshPermissionList()
    return NewUserInfo[0] + " is now: "+ NewUserInfo[1]

def checkuser(LIMSdb, SQLRequest):
    """Gets the Permission Groups for a user Login ID
    
    Parameters: Login ID
    
    Returns: Permission Groups"""

    CheckedPermission = PermissionList.get(SQLRequest["Command"])
    
    if CheckedPermission == "":
        CheckedPermission = "User has no permissions"
    elif CheckedPermission is None:
        CheckedPermission = "User is not recognised"
    
    return CheckedPermission
    




SQLMethods = {
    "fetchall": [fetchall,"Important"], #[Function, permission] -- permission can be a [table] for specific, or string 
    "writenew": [writenew,["Senior Scientist"]],
    "updateuser" : [updateuser, ["Administrator"]],
    "checkuser" : [checkuser,["Administrator","Senior Scientist"]],
    "GetAllMethods" : [GetAllMethods,["Administrator"]],
    "GetMethod" : [GetMethod,["all"]],
}



#End of SQL Methods configuration


###################################################################################################################################################################################################################################################################################
###################################################################################################################################################################################################################################################################################
###################################################################################################################################################################################################################################################################################
###################################################################################################################################################################################################################################################################################
###################################################################################################################################################################################################################################################################################




#Third step is safe SQL request construction, and any final checks    
def AccessSQL(LIMSdb, SQLRequest):
    """Database Access Stage 3: Commit action to SQL databse, and any final checks before returning the data to the Client

    Args:
        UserAccessData (dict): A dictionary of User Information which can be verified against a permission list
        UserSQLRequest (str): SQL Query from the client
        UserSQLDatabase (str): Name of the database to be accessed

    Returns:
        str: SQL Response back to Client
    """

    #SQLRequest format
    #SQLRequest["AccessToken"] = VerifyAccessToken
    #SQLRequest["Method"] = req.get("Method")
    #SQLRequest["Command"] = req.get("SQLCommand")
    #SQLRequest["Database"] = req.get("Database")
    #SQLRequest["Permission"] = List of Permission Types for the user e.g ["Senior Scientist"]

 ###        THIS NEEDS TO BE CONFIGURED TO YOUR BACKEND PREFERENCES FOR SQL PROTECTION          ###
 
    #Use pypika for safe construction
    #https://realpython.com/prevent-python-sql-injection/ further reading
    
    myresult = "SQL Method not found."
    if SQLRequest["Method"] in SQLMethods.keys(): #does the Method exist?
        myresult = "You are not authorised for the requested SQL Method" 
        SQLMethod = SQLMethods[SQLRequest["Method"]] #Get server Method info from the Method name in the request
        RequestPermitted = False
        #If ONE of our permission types matches ONE permission group then we can perform the Method
        for UserPermission in SQLRequest["Permission"]:
            if isinstance(SQLMethod[1], str): #String type permission? -> Method Group
                RequestPermitted = (UserPermission in SPG[SQLMethod[1]])
                #^Permission group type -> Is my authorisation type found in the Permission Group?
            else: #List type permission -> Check list directly
                RequestPermitted = (UserPermission in SQLMethod[1])
                if SQLMethod[1][0] == "all":  #if all users are permitted
                    RequestPermitted = True
                #^permission list tyep -> is my authorisation found in the custom permission list?
            if RequestPermitted:
                break
        #If we are permitted, perform Method
        if RequestPermitted:       
            myresult = SQLMethod[0](LIMSdb, SQLRequest)
    return myresult     


#Configure SQL Connector module for later
if config["Database"]["SQLType"] == "postgresql":
    import psycopg2
elif config["Database"]["SQLType"] == "sqlite":
    import sqlite3
#MySQL Default
else:   #config["Database"]["SQLType"] == "mysql":
    import mysql.connector as mysql
#If you want to use multiple databases you can restructure the ConnectSQL code
#There are two ways to do it - 
# 1. make SQLRequest["Database"] = ["SQLType", "Name of Databse"] -- takes a lot of clientside reworking!
# 2. connect to one database (mysql), see if there's a database under the SQLRequest["Database"] name, if not try with PostreSQL
# 2continued --this may put unecessary server stress for each request. Make sure your most used database is checked first! 
def ConnectSQL(SQLRequest):
    """Database Access Stage 2: Secures a connection to the SQL database, primed to commit the request

    Args:
        UserAccessData (dict): A dictionary of User Information which can be verified against a permission list
        UserSQLRequest (str): SQL Query from the client
        UserSQLDatabase (str): Name of the database to be accessed

    Returns:
        str: Stage 3 (Perform action, verify response) -> SQL Response back to Client (str)
    """

    LIMSdb = False
    if SQLRequest["Database"]:
        #PostgreSQL support
        if config["Database"]["SQLType"] == "postgresql":
            LIMSdb = psycopg2.connect(
            database=SQLRequest["Database"],
            host=config["Database"]["SQLHost"],
            port=config["Database"]["SQLPort"],
            user=config["Database"]["SQLUsername"],
            password=config["Database"]["SQLPassword"],
            )

        #SQLite support 
        elif config["Database"]["SQLType"] == "sqlite":
            sqlite3.connect(config["Database"]["SQLHost"]) 
            #Set "Database" to the file path of the "database.db" file
            
            ##This approach only lets users write to one .db
            ##if you have multiple .db files which you intend to use, you can do this:
            #SQLiteDBFile = os.path.join(config["Database"]["SQLHost"],SQLRequest["Database"])
            #if not os.path.exists(SQLiteDBFile):
            #   return "SQLite DB file found."  #if the user asks for a database which doesn't exist  
            #sqlite3.connect("SQLiteDBFile")
            
            ##Expanding on the above, you might want permissions for specific databases
            ##For example, only senior scientists can access the database and scientists cannot
            #SQLiteDBFile = os.path.join(config["Database"]["SQLHost"],SQLRequest["Database"])
            #if not os.path.exists(SQLiteDBFile):
            #   return "SQLite DB file found."  #if the user asks for a database which doesn't exist  
            #if SQLiteDBFile == r"C:/DirectoryTo/SeniorOnlyDatabase.db":
            #   #Special database!
            #   if not "Senior Scientist" in SQLRequest["Permission"]:
            #       return "You do not have permission to access this database."
            ##Establish connection 
            #sqlite3.connect("SQLiteDBFile")
            
            #The above code is ONLY relevant if you are using SQLite and want additional file access security...
            #if you use PostgreSQL or MySQL use the native built-in permission system from SQLMethods

        #MySQL Default
        else:   #config["Database"]["SQLType"] == "mysql":
            LIMSdb = mysql.connect(
            database=SQLRequest["Database"],
            host=config["Database"]["SQLHost"],
            port=config["Database"]["SQLPort"],
            user=config["Database"]["SQLUsername"],    
            password=config["Database"]["SQLPassword"],
            )
    
    
    
    #if you were using postgresql for example, you would do this: https://www.freecodecamp.org/news/postgresql-in-python/
    
    #Sense SQL execution request type
    return AccessSQL(LIMSdb, SQLRequest) #Once we are inside our SQL database, we can move to the execution stage



#First Step is initial permission checks (e.g is the user allowed to perform the type of request?)
def Verify(SQLRequest):
    """Database Access Stage 1: Checks the UserAccessData to ensure the Client is permitted to access the database

    Args:
        UserAccessData (dict): A dictionary of User Information which can be verified against a permission list
        UserSQLRequest (str): SQL Query from the client
        UserSQLDatabase (str): Name of the database to be accessed

    Returns:
        str: Stage 2 (Connect to Database) -> Stage 3 (Perform action, verify response) -> SQL Response back to Client (str)
    """

    #SQLRequest format
    #SQLRequest["AccessToken"] = VerifyAccessToken
    #SQLRequest["Method"] = req.get("Method")
    #SQLRequest["Command"] = req.get("SQLCommand")
    #SQLRequest["Database"] = req.get("Database")
    #++ SQLRequest["Permission"] = List of Permission Types for the user e.g "Senior Scientist"

    UserJson = SQLRequest["AccessToken"].json()
    UserID = str(UserJson["id"])
    


    if UserID in PermissionList:
        SQLRequest["Permission"] = PermissionList[UserID]
        #At any stage you can return a string containing an error message to prevent the SQL request being parsed
        #Example of a permission check
        #if "Senior Scientist" in PermissionList[UserID]: 
         #   print("User is a Senior Scientist")
        
        #Example of an SQL request analysis
        #if isinstance(SQLRequest["Command"], str):
         #   if SQLRequest["Command"].find("Something Bad") > 1: 
          #      return "You are not allowed to search for:Something Bad" 
        
        #you can combine the two above examples for permission-based requests:
        #e.g if command is Writing to the SQL database, then user must ALSO be a Senior Scientist or LIMS administrator
        
        return ConnectSQL(SQLRequest)    #If everything is ok then we can move to Step 2
    else:
        print(f"{UserID} is not a recognised UserID")
        return f"{UserID} is not a recognised UserID"
