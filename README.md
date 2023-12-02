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
