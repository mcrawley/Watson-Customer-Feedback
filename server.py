#
# Copyright 2014 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-
import os
from os.path import join, dirname
import requests
import json
from flask import Flask, render_template, request, Response, stream_with_context, redirect, url_for
from flask.ext.wtf import Form
import logging
from wtforms.fields import StringField, BooleanField
from wtforms.validators import DataRequired
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
#app.config.from_object('config')
from flask import request
from flask import jsonify
import couchdb


class FeedbackForm(Form):
    feedback = StringField('feedback', validators=[DataRequired()])

class DBService(object):
    def __init__(self,object):
        # self.username = "711fcf22-faad-49bb-8b73-2d88476bff1f-bluemix"
        # self.password = "989dd36e0e52e04a7201ab24d837d259b5c94dec9d5d3b7355c21601bb51f984"
        # self.url = "https://711fcf22-faad-49bb-8b73-2d88476bff1f-bluemix:989dd36e0e52e04a7201ab24d837d259b5c94dec9d5d3b7355c21601bb51f984@711fcf22-faad-49bb-8b73-2d88476bff1f-bluemix.cloudant.com"
        
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
        app.logger.debug(i)
        self.statistics = {'count':i, 'anger':anger, 'disgust':disgust, 'fear':fear, 'sadness':sadness, 'joy':joy}
    def getData(self):
        return self.statistics
    

class ToneAnalyserService(object):
    def __init__(self,object):
        vcapServices = os.getenv("VCAP_SERVICES")
        # Local variables
        # self.url = "https://gateway.watsonplatform.net/tone-analyzer/api/v3/tone"
        # self.username = "24965395-78b5-4c85-81f0-461872e3415e"
        # self.password = "VX05cjaVmmOP"
    
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
        print(self.url)
        self.url = "https://gateway.watsonplatform.net/tone-analyzer/api/v3/tone"
        response = requests.post(self.url, params=({'version':'2016-05-19'}), data=json.dumps({'text':object}), headers=({'Content-Type':'application/json'}), auth=(self.username, self.password))
        self.r = response.content

    def getAnalysedTone(self):
        return self.r    

class LanguageTranslatorService(object):
    """Wrapper on the Text to Speech service"""

    # ws = GeventWebSocket(app)

    def __init__(self, object):
        """
        Construct an instance. Fetches service parameters from VCAP_SERVICES
        runtime variable for Bluemix, or it defaults to local URLs.
        """
        
        vcapServices = os.getenv("VCAP_SERVICES")
        # Local variables
        # self.url = "https://gateway.watsonplatform.net/language-translator/api/v2/translate"
        # self.username = "63811b21-49c3-46af-94c4-832ee315cf29"
        # self.password = "QHobAPrRVxa0"
    
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

        print(self.url)
        self.url = "https://gateway.watsonplatform.net/language-translator/api/v2/translate"
        response = requests.get(self.url, params=({'text':object, 'source':'fr', 'target':'en'}), auth=(self.username, self.password))
        self.r = response.content

    def getTranslatedText(self):
        return self.r

class SpeechToTextService(object):
    def __init__(self, object, language):
        """
        Construct an instance. Fetches service parameters from VCAP_SERVICES
        runtime variable for Bluemix, or it defaults to local URLs.
        """
        vcapServices = os.environ.get('VCAP_SERVICES') #json.loads(os.getenv('VCAP_SERVICES'))
        # Local variables
        # self.url = "https://stream.watsonplatform.net/speech-to-text/api/v1/recognize"
        # self.username = "e1b097d2-4644-4593-bce5-032d53d6e976"
        # self.password = "vvePCIkzuzlT"
        if vcapServices is not None:
            print("Parsing VCAP_SERVICES")
            services = json.loads(vcapServices)
            svcName = "speech_to_text"
            if svcName in services:
                print("Speech to Text service found!")
                svc = services[svcName][0]["credentials"]
                #self.url = svc["url"]
                self.username = svc["username"]
                self.password = svc["password"]
            else:
                print("ERROR: The Speech to Text service was not found")
        #audio = open(object)
        #self.r = requests.post(self.url, data=object, headers={'Content-Type': 'audio/wav'}, params={'model':'fr-FR_BroadbandModel'}, auth=(self.username, self.password))
        #WORKING CODE
        #audio = open('./FrenchSoccerClubComplaint.flac', 'rb');
        self.url = "https://stream.watsonplatform.net/speech-to-text/api/v1/recognize" 

        if(language == 'french'):
            model = 'fr-FR_BroadbandModel'
        else:
            model = 'en-US_BroadbandModel'


        self.r = requests.post(self.url,data=object, headers={'Content-Type':'audio/wav'}, params={'model':model}, auth=(self.username,self.password))
    def getText(self):
        return self.r

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/speechToText', methods=['GET','POST'])
def speechToText():
    language = request.form['language']
    textService = SpeechToTextService(request.files['file'], language)
    response = textService.getText().json()#.content.decode('utf-8')
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

    print(toneAnswer)
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
    # results['originalText'] = text
    # results.translatedText = translatedText
    return json.dumps(results)

@app.errorhandler(500)
def internal_Server_error(error):
    return 'Error processing the request', 500

# Global watson service wrapper
textToSpeech = None

if __name__ == "__main__":
    

    # Get host/port from the Bluemix environment, or default to local
    HOST_NAME = os.getenv("VCAP_APP_HOST", "127.0.0.1")
    PORT_NUMBER = int(os.getenv("VCAP_APP_PORT", "5000"))

    app.run(host=HOST_NAME, port=int(PORT_NUMBER), debug=True)

    # Start the server
    print("Listening on %s:%d" % (HOST_NAME, port))
