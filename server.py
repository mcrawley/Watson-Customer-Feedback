"""
@date: 11 November 2016
@author: Megan Crawley 
Parts of this code have been modified from code provided by IBM 
(available at  https://github.com/watson-developer-cloud/text-to-speech-python)
"""

import os
from os.path import join, dirname
import requests
import json
from flask import Flask, render_template, request, Response, stream_with_context, redirect, url_for
from flask.ext.wtf import Form
import logging
from wtforms.fields import StringField, BooleanField
from wtforms.validators import DataRequired
from flask import request
from flask import jsonify
import couchdb

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True


class FeedbackForm(Form):
    feedback = StringField('feedback', validators=[DataRequired()])

# Database service
class DBService(object):
    def __init__(self,object):
        
        # Fetch credentials from VCAP_SERVICES when application launched from Bluemix
        vcapServices = os.getenv("VCAP_SERVICES")

        if vcapServices is not None:
            print("Parsing VCAP_SERVICES")
            services = json.loads(vcapServices)
            svcName = "cloudantNoSQLDB"
            if svcName in services:
                print("CloudantDB service found!")
                svc = services[svcName][0]["credentials"]
                self.url = svc["url"]
                self.username = svc["username"]
                self.password = svc["password"]
            else:
                print("ERROR: The CloudantDB service was not found")

        # Incorrect URL provided by VCAP services, correct URL for services available in API documentation
        self.url = "https://afc72af6-f469-4f0b-b262-efc47038eb48-bluemix:ab52f1e41adfd00dfbe03dda5ee3fb28e20609bda5eb1f98b08cb68d55bc9b7b@afc72af6-f469-4f0b-b262-efc47038eb48-bluemix.cloudant.com"
        couch = couchdb.Server(self.url, self.username)
        couch.resource.credentials = (self.username, self.password)

        db = couch['customer_feedback']
        i = db.info()['doc_count'] + 1

        app.logger.debug(db.info()['doc_count'])

        if(len(object) > 0):
            doc_id, doc_rev = db.save({
                'customerName': i,
                'anger': object['anger'],
                'disgust': object['disgust'],
                'fear': object['fear'],
                'joy': object['joy'],
                'sadness': object['sadness'] 
                })
            doc = db[doc_id]

        anger = 0.0;
        disgust = 0.0;
        fear = 0.0;
        joy = 0.0;
        sadness = 0.0;

        for d in db:
            anger = anger + db[d]['anger']
            disgust = disgust + db[d]['disgust']
            fear = fear + db[d]['fear']
            joy = joy + db[d]['joy']
            sadness = sadness + db[d]['sadness']

        anger = anger/i
        disgust = disgust/i
        fear = fear/i
        joy = joy/i
        sadness = sadness/i

        self.statistics = {'count':i, 'anger':anger, 'disgust':disgust, 'fear':fear, 'sadness':sadness, 'joy':joy}

    def getData(self):
        return self.statistics
    
# Tone analyser service
class ToneAnalyserService(object):
    def __init__(self,object):

        # Fetch credentials from VCAP_SERVICES when application launched from Bluemix
        vcapServices = os.getenv("VCAP_SERVICES")
        
        if vcapServices is not None:
            print("Parsing VCAP_SERVICES")
            services = json.loads(vcapServices)
            svcName = "tone_analyzer"
            if svcName in services:
                print("Tone Analyser service found!")
                svc = services[svcName][0]["credentials"]
                self.url = svc["url"]
                self.username = svc["username"]
                self.password = svc["password"]
            else:
                print("ERROR: The Tone Analyser service was not found")
        
        # Incorrect URL provided by VCAP services, correct URL for services available in API documentation
        self.url = "https://gateway.watsonplatform.net/tone-analyzer/api/v3/tone"
        response = requests.post(self.url, params=({'version':'2016-05-19'}), data=json.dumps({'text':object}), headers=({'Content-Type':'application/json'}), auth=(self.username, self.password))
        self.r = response.content

    def getAnalysedTone(self):
        return self.r    

# Language translator service
class LanguageTranslatorService(object):

    def __init__(self, object):
       
        # Fetch credentials from VCAP_SERVICES when application launched from Bluemix
        vcapServices = os.getenv("VCAP_SERVICES")
        
        if vcapServices is not None:
            print("Parsing VCAP_SERVICES")
            services = json.loads(vcapServices)
            svcName = "language_translator"
            if svcName in services:
                print("Language Translator service found!")
                svc = services[svcName][0]["credentials"]
                self.url = svc["url"]
                self.username = svc["username"]
                self.password = svc["password"]
            else:
                print("ERROR: The Language Translator service was not found")

        # Incorrect URL provided by VCAP services, correct URL for services available in API documentation
        self.url = "https://gateway.watsonplatform.net/language-translator/api/v2/translate"
        response = requests.get(self.url, params=({'text':object, 'source':'fr', 'target':'en'}), auth=(self.username, self.password))
        self.r = response.content

    def getTranslatedText(self):
        return self.r

# Speech to text service
class SpeechToTextService(object):
    def __init__(self, object, language):
        
        # Fetch credentials from VCAP_SERVICES when application launched from Bluemix
        vcapServices = os.environ.get('VCAP_SERVICES') #json.loads(os.getenv('VCAP_SERVICES'))
        
        if vcapServices is not None:
            print("Parsing VCAP_SERVICES")
            services = json.loads(vcapServices)
            svcName = "speech_to_text"
            if svcName in services:
                print("Speech to Text service found!")
                svc = services[svcName][0]["credentials"]
                self.username = svc["username"]
                self.password = svc["password"]
            else:
                print("ERROR: The Speech to Text service was not found")
        
        self.url = "https://stream.watsonplatform.net/speech-to-text/api/v1/recognize" 

        if(language == 'french'):
            model = 'fr-FR_BroadbandModel'
        else:
            model = 'en-US_BroadbandModel'

        self.r = requests.post(self.url,data=object, headers={'Content-Type':'audio/wav'}, params={'model':model}, auth=(self.username,self.password))
    def getText(self):
        return self.r

# Index page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Perform speech to text, translation and analysis upon stopping recording
@app.route('/speechToText', methods=['GET','POST'])
def speechToText():
    language = request.form['language']
    textService = SpeechToTextService(request.files['file'], language)
    response = textService.getText().json()
    text = ""
    print(response)
    for sentence in response['results']:
        text+=(sentence['alternatives'][0]['transcript'])
    if(language == 'french'):
        translatorService = LanguageTranslatorService(text)
        translatedText = translatorService.getTranslatedText()
    else:
        translatedText = text
    toneAnalyser = ToneAnalyserService(translatedText)
    ta = toneAnalyser.getAnalysedTone()
    toneAnswer = json.loads(ta)
    anger = 0.0
    disgust = 0.0
    fear = 0.0
    joy = 0.0
    sadness = 0.0

    for tone in toneAnswer['document_tone']['tone_categories'][0]['tones']:
        if(tone['tone_id'] == 'anger'):
            anger = tone['score']
        if(tone['tone_id'] == 'disgust'):
            disgust = tone['score']
        if(tone['tone_id'] == 'fear'):
            fear = tone['score']
        if(tone['tone_id'] == 'joy'):
            joy = tone['score']
        if(tone['tone_id'] == 'sadness'):
            sadness = tone['score']
    db = DBService({'anger':anger*100, 'disgust':disgust*100, 'fear':fear*100, 'joy':joy*100, 'sadness':sadness*100});
    results = db.getData();
    
    results.update({'originalText' : text})
    results.update({'translatedText' : translatedText})

    return json.dumps(results)

@app.errorhandler(500)
def internal_Server_error(error):
    return 'Error processing the request', 500

if __name__ == "__main__":
    

    # Get host/port from the Bluemix environment, or default to local
    HOST_NAME = os.getenv("VCAP_APP_HOST", "127.0.0.1")
    PORT_NUMBER = int(os.getenv("VCAP_APP_PORT", "5000"))

    app.run(host=HOST_NAME, port=int(PORT_NUMBER), debug=True)

    # Start the server
    print("Listening on %s:%d" % (HOST_NAME, port))
