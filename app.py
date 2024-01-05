import re
from flask import Flask, request, jsonify
import nltk
import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

def analyze_pii(text):

    def find_numeric_sequences(input_string):
        pattern = r'\b\d+\b'
        numeric_sequences = re.findall(pattern, input_string)
        return numeric_sequences

    def find_alphanumeric_words_with_letters_and_digits(input_string):
        pattern = r'\b(?=\w*\d)(?=\d*\w)[A-Za-z0-9]+\b'
        alphanumeric_words = re.findall(pattern, input_string)
        return alphanumeric_words

    def is_first_name(token):
        return token.pos_ == 'PROPN' and token.is_alpha and len(token) > 1 and token.text.lower() not in {'card', 'license', 'id', 'pan', 'adhaar', 'voter'}

    def pos_tagging_and_named_entity_recognition(text):
        tokens = nltk.word_tokenize(text)
        pos_tags = nltk.pos_tag(tokens)
        nouns = [word for word, pos in pos_tags if pos.startswith('NNP')]
        noun_text = ' '.join(nouns)
        doc = nlp(noun_text)
        personal_names = [token.text for token in doc if is_first_name(token)]
        return list(set(personal_names))

    def extract_cleaned_proper_nouns(text):
        filter = str([pos_tagging_and_named_entity_recognition(text)])
        proper_noun_text = ' ' + (filter)
        doc = nlp(proper_noun_text)
        filtered_proper_nouns = [ent.text for ent in doc.ents if ent.label_ not in ['ORG', 'GPE']]
        return filtered_proper_nouns

    def load_names(file_path):
        with open(file_path, 'r') as file:
            names = [line.strip() for line in file]
        return names

    def train_model(names):
        data = names + ['noname'] * len(names)
        labels = ['name'] * len(names) + ['noname'] * len(names)
        model = make_pipeline(CountVectorizer(), MultinomialNB())
        model.fit(data, labels)
        return model

    def identify_names(model, input_paragraph):
        input_words = re.findall(r'\b\w+\b', input_paragraph)
        probabilities = model.predict_proba(input_words)
        identified_names = [word for word, prob in zip(input_words, probabilities[:, 0]) if prob > 0.5]
        return identified_names

    numeric_sequences = find_numeric_sequences(text)
    alphanumeric_words = find_alphanumeric_words_with_letters_and_digits(text)
    filtered_proper_nouns = extract_cleaned_proper_nouns(text)

    file_path = 'Names.txt'
    names = load_names(file_path)
    name_model = train_model(names)
    joblib.dump(name_model, 'name_model.joblib')
    user_input = text
    output_names = identify_names(name_model, user_input)

    detected_pii = list(set(numeric_sequences + alphanumeric_words + filtered_proper_nouns + output_names))
    

    # Define a mapping of PII types using regular expressions
    pii_type_mapping = {
        'name': r'^[A-Za-z\s]+$',  # Simple check for alphabetical characters and spaces
        'Aadhaar Number': r'^\d{12}$',  # 12-digit Aadhaar number
        'Mobile Number': r'^\d{10}$'  # 10-digit mobile number
        # Add more PII types and their regex patterns as needed
    }

    # Create a list of dictionaries with PII type and value
    pii_result = []
    
    for pii_value in detected_pii:
        # Check against each PII type regex pattern and analyze surrounding words
        for pii_type, pattern in pii_type_mapping.items():
            if re.match(pattern, pii_value.strip()) :
                pii_result.append({'pii_type': pii_type, 'pii_value': pii_value})

        # Check against each PII type regex pattern and analyze surrounding words
        if re.match(r'\b(?=\w*\d)(?=\d*\w)[A-Za-z0-9]+\b', pii_value.strip()) :
            # Analyze surrounding words for alphanumeric sequences
            words_before = re.findall(r'\b\w+\b', text[:text.find(pii_value)])[-4:]
            words_after = re.findall(r'\b\w+\b', text[text.find(pii_value) + len(pii_value):])
            if 'Passport' in words_before:
                pii_result.append({'pii_type': 'Passport Number', 'pii_value': pii_value})

            elif 'Voter' in words_before:
                pii_result.append({'pii_type': 'Voter ID Number', 'pii_value': pii_value})

            elif 'License' in words_before:
                pii_result.append({'pii_type': 'Drivers License Number', 'pii_value': pii_value})

            elif 'PAN' in words_before:
                pii_result.append({'pii_type': 'PAN Number', 'pii_value': pii_value})

            elif 'account' in words_before:
                pii_result.append({'pii_type': 'Account Number', 'pii_value': pii_value})

    return pii_result

@app.route('/analyze-pii', methods=['POST'])
def analyze_pii_endpoint():
    try:
        data = request.get_json()

        if 'paragraph' not in data:
            raise ValueError("Missing 'paragraph' field in the request JSON.")

        paragraph = data['paragraph']
        detected_pii = analyze_pii(paragraph)

        response = {
            'pii_detected': detected_pii,
            'error': None
        }

    except Exception as e:
        response = {
            'error': str(e),
            'pii_detected': None
        }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
