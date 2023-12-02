# PII-Evaluation
 A Flask API to analyse text paragraphs and identify personally identifiable information (PII) within them
 The API takes a text paragraph as input and returns a response containing an array of PII found in the text.


Here is an example of the expected request and response:


Request:
  {

  "body": "Priyanshu Sharma is a Mtech CSE student from Jadavpur University. His hometown is in Asansol. He has completed Btech from Jadavpur University. He recently applied for a Driving License in West Bengal with the help of his ADHAAR and Voter Card. The ADHAAR number of Priyanshu is 4567000007865 and the Voter ID number is SYG882745586. But the problem is that the address in the adhaar and the voter id are different. So therefore he was advised to provide his PAN Card having PAN no- AKKJM7875665D and the Bank account statement with an account in State Bank Of India, the account number is 6356278255789.

  }



Response:
{

  "pii_detected": [ Priyanshu, 4567000007865, SYG882745586, AKKJM7875665D, 6356278255789 ],

  “error": "nil"

}




*If there is any error then it reflects on the value corresponding to error in the json.




Specifications:

A Flask API that accepts POST requests with JSON payloads.


Implements a function within the API that analyses the input paragraph for PII.


Identifies PII and returns it in an array in the response.

Solution:

The API has been built on the analyze_pii endpoint using libraries like NLTK and Spacy for Named Entity Recognition using the concept of POS tagging for proper nouns from which common nouns have been eliminated.This helps to detect names and surnames of individuals. Further, regular expressions have been used to identify Personally Identifiable Information like Adhaar, Voter, Pan ID etc. considering the fact that such IDs worldwide are sequences of either numeric or alphanumeric characters. The API can be set up on a local device by running the app.py python file in an IDE like VS Code and then sending required text as input requests via JSON payloads, using suitable commands, as mentioned below.

Before running the api, ensure that all required libraries are installed in the local system. This can be done by using the pip command to download and install them.

In VS Code, open the integrated terminal by pressing Ctrl + (backtick) or go to View -> Terminal. Open Terminal in VS Code and then select the Git Bash option. 

Type the following commands in the terminal screen.
pip install Flask 
pip install spacy
pip install nltk
python -m spacy download en_core_web_sm

NLTK requires additional data for various tasks such as tokenization, stemming, etc. To download this data, you can use the NLTK downloader. In your terminal, run a Python interpreter: Type 'python' in the bash console.

import nltk
nltk.download()

Enter the bash command "python app.py" to run the file. Wait for a while till a development server on http://127.0.0.1:5000 is created. Close the python environment and go to bash again. Send in a POST request using the curl command as: 

curl -X POST -H "Content-Type: application/json" -d '{"paragraph": "Input text here."}' http://127.0.0.1:5000/analyze-pii

Replace the input text field with your required input. The output containing the detected PII from the text would be displayed as output in the terminal screen.

You can use the following commands if you are using Windows Powershell in VS Code:

$url = "http://127.0.0.1:5000/analyze-pii"
$jsonPayload = '{"paragraph": "Your text here."}'

$response = Invoke-RestMethod -Uri $url -Method Post -Body $jsonPayload -Headers @{"Content-Type"="application/json"}

$response

Replace "Your text here." with the actual text you want to analyze.
$url: The URL of your Flask API endpoint.
$jsonPayload: The JSON payload to be sent in the POST request.
Invoke-RestMethod: A PowerShell cmdlet for making HTTP requests.

Save this PowerShell script in a file with a .ps1 extension and run it in the PowerShell environment. This script should send a POST request to the Flask API and display the API response in the PowerShell console.

Thank You!