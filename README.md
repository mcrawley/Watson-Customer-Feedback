# Watson-Customer-Feedback
The Watson-Customer-Feedback application is a Python web application which uses IBM Watson cloud-based services for gathering and analysing verbal customer feedback. Users can record verbal feedback in either English or French, using the microphone in their computer. This audio recording will be converted to text using the Watson Speech To Text service and, when the French language is selected, this text will be translated into English using the Watson Language Translator service. The Watson Tone Analyzer service is then used to analyse the likelihood that tones of anger, disgust, fear, joy or sadness are being expressed in the customer's feedback. This data is stored using IBM's Cloudant database service and a statistical summary of customer feedback to-date is displayed in the application. 

## Functional Requirements ##

- Users are able to submit verbal comments consisting of 2 -3 sentences to the application using, at worst, an inbuilt microphone in their computer
- Users are able to submit verbal comments in languages other than English
- The application will provide users with a textual display of their comments in English, and where appropriate, the language originally used
- Tone analysis will be conducted on each instance of customer feedback and results will be retained
- An accumulative representation of customer feedback results will be displayed to the user upon submission of their own feedback
- The user will not be able to view current feedback statistics until they have submitted their own feedback

## Non-Functional Requirements ##

- Security
  - IBM Bluemix account details and individual service credentials should not be exposed in the source code of the application
- Scalability
  - The application is scalable in terms of the number of languages it supports
  - The application is scalable in terms of the capacity of the customer feedback database
- Usability
  - The user interface is simple to use and requires no previous technical knowledge
  - If issues arise regarding the processing of audio provided by the user, they will be informed in a clear and prompt manner
- Availability
  - The application itself and all IBM services will have minimal downtime

## Getting Started ##
1. Create a Bluemix account at https://console.ng.bluemix.net/registration/ or use an existing Bluemix account
2. Download and install Cloud-foundry CLI tool, available here: https://github.com/cloudfoundry/cli
3. Ensure you have curl working on your machine
4. Connect to Bluemix and create the necessary services and application using the following steps
  
  **To create the services**, in command line:

  ```cf api https://api.au-syd.mybluemix.net```
  
  ```cf login -u {username or email}```
  
  ```cf create-service speech_to_text standard speech-to-text-service```
  
  ```cf create-service language_translator standard language-translator-service```
  
  ```cf create-service tone_analyzer standard tone-analyzer-service```
  
  ```cf create-service cloudantNoSQLDB Lite cloudant-service```

  **To instantiate the database** (required for application to work):
  - Access the cloudant service from the Bluemix console and navigate to service credentials
  - In command line:
    
    ```curl -X PUT -u {username} '{url}/customer_feedback' ```
     
    ```curl -X GET - u {username} '{url}/customer_feedback'```
      
    You will be prompted for your password (also available in service credentials) for each request. The second request should return the details of the newly created database. {username} and {url} refer to the username and url given in the service credentials. 
    
    To delete the database (only required for troubleshooting), in command line:
      
    ```curl -X DELETE -u {username} '{url}/customer_feedback'```

  **To load the application onto the cloud**:  
  - Clone the project
  - In command line:
  
    Navigate to (inside) project folder
    
    ```cf push```
  
Alternatively, the services can be created using the IBM Bluemix dashboard and bound/connected to the application once it has been pushed via CLI (as above).

## Running the application in the cloud ##
  
  To use the audio recording functionality of the application, please view the application in Chrome and ensure 'https://' is present at the start of the application url when viewing the application from Bluemix. If not, simply add to the start of the url and press Enter. 

## Testing the application  
  Sample English and French .m4a audio files are available in the repository in the samples folder. To test the application, press the Start Recording button and play the audio at the same time. When played at full volume, this audio should be detected by an inbuilt microphone and produce results sufficient for demonstration purposes. Please note, the accuracy of the speech to text and translation services will be compromised by low volume or lack of clarity. 
  
  Alternatively, sample .flac files are available in the samples folder. To use these directly, in server.py replace the following code:
  
  ```self.r = requests.post(self.url,data=object, headers={'Content-Type':'audio/wav'}, params={'model':model}, auth=(self.username,self.password))```
  
  with:
  
  ```audio = open('./samples/filename.flac', 'rb')
  
  self.r = requests.post(self.url,data=audio, headers={'Content-Type':'audio/flac'}, params={'model':model}, auth=(self.username,self.password))```

## Running the application locally ##

As the application makes use of the VCAP services provided by Bluemix to authenticate to each service, the source code must be modified to run the application locally while still allowing connection to the required services. 

 1. Obtain the credentials (username and password) for each service using the Bluemix dashboard. 
 2. In server.py, when initialising each service class (DBService, ToneAnalyserService, LanguageTranslatorService, SpeechToTextService), instantiate the username and password attributes using the credentials. 
 
 Example:
  ```` 
  class ToneAnalyserService(object):
  def __init__(self,object):
  self.username = "placeYourToneAnalyserServiceUsernameHereAsAString"
  self.password = "placeYourToneAnalyserServicePasswordAsAString"
  ````
 3. Ensure you have python and all project dependencies installed on your machine
 4. Start up a local server using python and run the application, in command line:
 
 ```python -m SimpleHTTPServer 5000```
 
 In a separate command line instance, navigate to the project folder and run:
 
 ```python ./server.py```
 
 The application should now be accessible on localhost:5000

## Troubleshooting ##

Logs for the Bluemix application can be accessed from CLI:

```cf logs customer-feedback-project```
  
If a 'broken-pipe' is encountered or the application fails to connect to the services:

   - Ensure each service is bound to the application. To do this, navigate to the Bluemix dashboard > select a service > select 'Connections'
   - Check the VCAP services exist for the application. This can be found by selecting the application from the Bluemix dashboard and navigating to Runtime > Environment Variables

If the network response object indicates that you have made too many requests, this is unfortunately a limitation of using the Cloudant service with a free/trial Bluemix account. In this situation you can either:

- Wait an undefined period of time to start using the service again (such that your request restrictions are no longer exceeded)
- If loss of current data is acceptable, delete and recreate the database, following the steps below:

  - In command line:
  
   ```curl -X DELETE -u {username} '{url}/customer_feedback'```
   
   ```curl -X PUT -u {username} '{url}/customer_feedback'```
   
## Code Repository ##
The code repository is summarised as follows:
 - The templates folder contains index.html for the application's markup and inline styling
 - script.js is required for recording and uploading audio and to make an AJAX request when a user stops the audio recording
 - recorder.js is an open source project used to capture and upload audio recordings as .wav files
 - server.py is the backend program resopnsible for routing, making HTTP requests to IBM services and rendering the html page
 - requirements.txt contains project dependencies
 - manifest.yml is used when uploading the application to the cloud and for subsequent updates. This file contains the name and hostname of the application which is important when managing applications in Bluemix
 - The version of Python being used can be found in runtime.txt

## Resources ##

- To integrate Watson services with a Python web application a github project, available at https://github.com/watson-developer-cloud/text-to-speech-python was used as a reference. This project details how to use VCAP services for service authentication, how to structure a basic Python application using the Flask framework and how to make requests to services.

- Watson Developer Cloud API Documentation was used when implementing the service request, specifically available at:
 - http://www.ibm.com/watson/developercloud/tone-analyzer/api/v3/
 - https://www.ibm.com/watson/developercloud/speech-to-text/api/v1/
 - http://www.ibm.com/watson/developercloud/language-translator/api/v2/
 
- To troubleshoot problems experienced during integration of cloud services with the web application, the IBM Developer Works discussion forum was used.

- To use the Cloudant service with a Python application, an IBM blog article was used (https://cloudant.com/blog/using-python-with-cloudant/#.WCAV55N97GI) and couchDB documentation was used as a supporting reference (https://pythonhosted.org/CouchDB/getting-started.html).

- To implement audio recording and uploading functionality the source code from a sample project, available at https://webaudiodemos.appspot.com/AudioRecorder/index.html, was used as a reference. recorder.js is an open source github project available at https://github.com/mattdiamond/Recorderjs which is used by the web application to record and upload audio as a .wav file. 

 
  

  
  
  

