# Watson-Customer-Feedback
The Watson-Customer-Feedback application is a Python web application which uses IBM Watson cloud-based services for gathering and analysing verbal customer feedback. Users can record verbal feedback in either English or French, using the microphone in their computer. This audio recording will be converted to text using the Watson Speech To Text service and, when the French language is selected, this text will be translated into English using the Watson Language Translator service. The Watson Tone Analyzer service is then used to analyse the likelihood that tones of anger, disgust, fear, joy or sadness are being expressed in the customer's feedback. This data is stored using IBM's Cloudant database service and a statistical summary of customer feedback to-date is displayed in the application. 

# Getting Started
1. Create a Bluemix account at https://console.ng.bluemix.net/registration/ or use an existing Bluemix account
2. Download and install Cloud-foundry CLI tool, available here: https://github.com/cloudfoundry/cli
3. Ensure you have curl working on your machine
3. Connect to Bluemix and create the necessary services and application using the following steps

  To create the services, in command line:

  ```cf api https://api.au-syd.mybluemix.net```
  
  ```cf login -u {username or email}```
  
  ```cf create-service speech_to_text standard speech-to-text-service```
  
  ```cf create-service language_translator standard language-translator-service```
  
  ```cf create-service tone_analyzer standard tone-analyzer-service```
  
  ```cf create-service cloudantNoSQLDB Lite cloudant-service```

  To instantiate the database (required for application to work):
  - Access the cloudant service from the Bluemix console and navigate to service credentials
  - In command line:
    
    ```curl -X PUT -u {username} '{url}/customer_feedback' ```
     
    ```curl -X GET - u {username} '{url}/customer_feedback'```
      
    You will be prompted for your password (also available in service credentials) for each request. The second request should return the details of the newly created database. {username} and {url} refer to the username and url given in the service credentials. 
    
    To delete the database (only required for troubleshooting), in command line:
      
    ```curl -X DELETE -u {username} '{url}/customer_feedback'```

To load the application on the cloud:  
  - In command line:
  
  Navigate to (inside) project folder
    
  ```cf push```
  
Alternatively, the services can be created using the IBM Bluemix dashboard and bound/connected to the application once it has been pushed via CLI (as above).

# Troubleshooting

Logs for the Bluemix application can be accessed from CLI:

```cf logs customer-feedback-project```
  
If a 'broken-pipe' is encountered or the application fails to connect to the services:

    - Ensure each service is bound to the application. To do this, navigate to the Bluemix dashboard > select a service > select 'Connections'
    - Check the VCAP services exist for the application. This can be found by selecting the application from the Bluemix dashboard and navigating to Runtime > Environment Variables

If network response object indicates that you have made too many requests, this is unfortunately a limitation of using the Cloudant service with a free/trial Bluemix account. In this situation you can either:

- Wait an undefined period of time to start using the service again (such that your request restrictions are no longer exceeded)
- If loss of current data is acceptable, delete and recreate the database, following the steps below:

  - In command line:
   ```curl -X DELETE -u {username} '{url}/customer_feedback'```
   ```curl -X PUT -u {username} '{url}/customer_feedback'```


  

  
  
  

