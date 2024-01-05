# Import necessary libraries
from flask import Flask, request, jsonify
# Flask for creating a web application, request for handling HTTP requests, jsonify for JSON responses
import re 
# Regular expression library for pattern matching
import nltk 
# Natural Language Toolkit for natural language processing tasks
import spacy
# SpaCy for advanced natural language processing tasks

# Import CountVectorizer to convert a collection of text data into a bag-of-words model
from sklearn.feature_extraction.text import CountVectorizer

# Import Multinomial Naive Bayes classifier for text classification
from sklearn.naive_bayes import MultinomialNB

# Import make_pipeline to simplify the creation of a pipeline of processing steps
from sklearn.pipeline import make_pipeline

# Import joblib for saving and loading the trained model
import joblib

# Download NLTK data required for tokenization and POS tagging
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Load SpaCy model for named entity recognition
nlp = spacy.load("en_core_web_sm")

# Create a Flask web application
app = Flask(__name__)

# Function to analyze personally identifiable information (PII) in a given text
def analyze_pii(text):

    # Function to find numeric sequences in the text
    def find_numeric_sequences(input_string):
        # The regular expression pattern r'\b\d+\b' is designed to match sequences of one or more digits (\d) that are surrounded by word boundaries (\b).The \d is a shorthand character class representing any digit (0-9), and the + quantifier specifies that there should be at least one or more digits in the sequence.
        pattern = r'\b\d+\b'
        # Used to find all occurrences of a specified pattern in a given string
        numeric_sequences = re.findall(pattern, input_string)
        return numeric_sequences

    def find_alphanumeric_words_with_letters_and_digits(input_string):
        # The pattern is looking for sequences of alphanumeric characters. The sequence must have at least one digit,  at least one non-digit character and should be surrounded by word boundaries. (?=\w*\d) is a positive lookahead assertion. This part checks if, looking forward in the string, there is a sequence of zero or more word characters (\w) followed by at least one digit (\d).[A-Za-z0-9] is a character class that includes uppercase letters (A-Z), lowercase letters (a-z), and digits (0-9).
        pattern = r'\b(?=\w*\d)(?=\d*\w)[A-Za-z0-9]+\b'
        alphanumeric_words = re.findall(pattern, input_string)
        return alphanumeric_words

    # Function to check if a SpaCy token represents a first name
    def is_first_name(token):
        # Additional filters to identify first names by eliminating common nouns
        return token.pos_ == 'PROPN' and token.is_alpha and len(token) > 1 and token.text.lower() not in {'card', 'license', 'id', 'pan', 'adhaar','voter'}
    
    # Function to perform POS tagging and named entity recognition using SpaCy
    def pos_tagging_and_named_entity_recognition(text):
        # Tokenize the text using NLTK
        tokens = nltk.word_tokenize(text)
        
        # Perform POS tagging using NLTK
        pos_tags = nltk.pos_tag(tokens)

        # Extract proper nouns based on POS tagging (inbuilt labels)
        nouns = [word for word, pos in pos_tags if pos.startswith('NNP')]

        # Join the nouns to form a string for SpaCy processing
        noun_text = ' '.join(nouns)

        # Use SpaCy for named entity recognition
        doc = nlp(noun_text)

        # Extract personal names based on preset additional filters
        personal_names = [token.text for token in doc if is_first_name(token)]
    

        return list(set(personal_names))

    # Function to extract cleaned proper nouns (excluding organizations and locations) using NLTK and SpaCy
    def extract_cleaned_proper_nouns(text):
        # Tokenize the text using NLTK
        filter=str([pos_tagging_and_named_entity_recognition(text)])

        # Join the proper nouns to form a string for SpaCy processing
        proper_noun_text = ' '+(filter)

        # Use SpaCy for named entity recognition
        doc = nlp(proper_noun_text)

        # Filter out organizations (ORG) and locations (GPE)
        filtered_proper_nouns = [ent.text for ent in doc.ents if ent.label_ not in ['ORG', 'GPE']]

        return filtered_proper_nouns

    # Function to load names from a text file
    def load_names(file_path):
    # Open the file and read names, stripping whitespace
        with open(file_path, 'r') as file:
            names = [line.strip() for line in file]
        return names

    # Function to train a name identification model
    def train_model(names):
        # Creating a dataset with names and non-names
        data = names + ['noname'] * len(names)
        labels = ['name'] * len(names) + ['noname'] * len(names)

        # Creating a pipeline with a bag-of-words model and Naive Bayes classifier
        model = make_pipeline(CountVectorizer(), MultinomialNB())

        # Training the model
        model.fit(data, labels)

        return model

    # Function to identify names from a paragraph
    def identify_names(model, input_paragraph):
        # Tokenize the paragraph into words
        input_words = re.findall(r'\b\w+\b', input_paragraph)

        # Obtain probabilities for each class using the trained model
        probabilities = model.predict_proba(input_words)

        # Assuming 'name' is the first class, filter words based on the probability threshold
        identified_names = [word for word, prob in zip(input_words, probabilities[:, 0]) if prob > 0.5]

        return identified_names
    
    # Apply the defined functions to extract PII from the text
    numeric_sequences = find_numeric_sequences(text)
    alphanumeric_words = find_alphanumeric_words_with_letters_and_digits(text)
    filtered_proper_nouns = extract_cleaned_proper_nouns(text)
    # Identify names from the paragraph
    
    # File path to the text file containing names
    file_path = 'Names.txt'

    # Load names from the text file
    names = load_names(file_path)

    # Train the name identification model
    name_model = train_model(names)

    # Save the trained model for future use
    joblib.dump(name_model, 'name_model.joblib')

    # Accept user input for a paragraph
    user_input = text

    # Identify names from the paragraph
    output_names = identify_names(name_model, user_input)



    # Combine all detected PII into a set to avoid repetitions and convert it back to a list
    detected_pii = list(set(numeric_sequences + alphanumeric_words + filtered_proper_nouns + output_names))
    return detected_pii

# Define a route for the '/analyze-pii' endpoint that accepts POST requests
@app.route('/analyze-pii', methods=['POST'])
def analyze_pii_endpoint():
    try:
        # Extract JSON data from the request
        data = request.get_json()

        # Check if the 'paragraph' field is present in the request JSON
        if 'paragraph' not in data:
            raise ValueError("Missing 'paragraph' field in the request JSON.")

        # Get the paragraph from the JSON data
        paragraph = data['paragraph']
        
        # Analyze PII in the paragraph
        detected_pii = analyze_pii(paragraph)

        # Prepare the response JSON with detected PII
        response = {
            'pii_detected': detected_pii
        }

    except Exception as e:
        # If an error occurs, include the error message in the response
        response = {
            'error': str(e)
        }

    # Return the response as a JSON object
    return jsonify(response)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
