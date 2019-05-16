from flask import Flask, render_template, request, abort, jsonify, Response, url_for,flash,redirect
import os
import requests
import json
import yaml
import app.journals
 

# Initialize your application.

app = Flask(__name__)
app.secret_key = 'rlflmfdlk;mfdklnkl@@JIUkldnkndnd'

# some variables
records=[]
sid="301017lkx4h9dlw"

####################################################
# Load the CSV file containing the book and issn
####################################################

def loadCSV():
        recup=journals.journals
        for line in recup:
            records.append(line)

####################################################
# Get the issn from the line of the file
####################################################

def getISSN(myLine):
    value=myLine.split("|")
    return value[1]

####################################################
# And start building your routes.
####################################################

@app.route('/')
@app.route('/index')
def index():
    try:
        loadCSV()
        return(render_template('base.html',records=records))
    except:
        pass


@app.route('/processAPI',methods=['GET'])
def processAPI():

    # define your parameters
    issn=getISSN(request.args.get("issn"))
    email=request.args.get("email")
    myAction,mySid,myIssn,myEmail=("getStatus",sid,issn,email)

    # building the parameters dictionary
    parameters={
                "action":myAction,
                "sid" : mySid,
                "issn": myIssn,
                "email": myEmail
            }

    # call the API
    response = requests.get('http://www.journaltocs.ac.uk/parsers/remoteAlert.php?',params=parameters)

    # convert the response 
    myData = yaml.load(response.text)

    # Evaluation of the cases
    text=myData["responseText"]

    if text.startswith("User does not exist in JournalTOCs database"):
        flash('This user does not exist in the database!!! , please click on the link HERE at the bottom ', 'message')


    if text.startswith("User exists in JournalTOCs but journal XXXX-XXXXX was not found in JournalTOCs"):
        flash('This journal does not exist in the database!!! ', 'message')

    if text.startswith("User exists in JournalTOCs but is not following journal"):
        myAction="follow"

        # building the parameters dictionary
        parameters={
                "action":myAction,
                "sid" : mySid,
                "issn": myIssn,
                "email": myEmail
        }
        # call the API
        response = requests.get('http://www.journaltocs.ac.uk/parsers/remoteAlert.php?',params=parameters)

        flash('Congratulations, you are now subscribed to this journal!!! ', 'message')

    if text.startswith("User exists in JournalTOCs and is already following journal"):
        flash(' You are already following this journal!!! ', 'message')        
    
    return redirect(url_for('index'))
    

@app.route('/unfollow',methods=['GET'])
def unfollow():

    # define your parameters
    issn=getISSN(request.args.get("issn"))
    email=request.args.get("email")
    myAction,mySid,myIssn,myEmail=("unfollow",sid,issn,email)

    # building the parameters dictionary
    parameters={
                "action":myAction,
                "sid" : mySid,
                "issn": myIssn,
                "email": myEmail
            }

    # call the API
    response = requests.get('http://www.journaltocs.ac.uk/parsers/remoteAlert.php?',params=parameters)

    # convert the response 
    myData =response.text

    # Evaluation of the cases
    result=myData.find("unfollowed")

    if (result != -1) :
        flash('You have successfully unsubcribed from this journal!!! ', 'message')        
    else : 
        flash('You are not following this journal!!! ', 'message')        

    return redirect(url_for('index'))

if __name__ == '__main__':

   app.run(debug=True)