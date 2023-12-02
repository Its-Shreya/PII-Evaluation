import nltk
import spacy

# Download NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Load SpaCy model for named entity recognition
nlp = spacy.load("en_core_web_sm")

def is_first_name(token):
    # Additional filters to identify first names
    return token.pos_ == 'PROPN' and token.is_alpha and len(token) > 1 and token.text.lower() not in {'card', 'license', 'id', 'pan', 'adhaar','voter'}

def pos_tagging_and_named_entity_recognition(text):
    # Tokenize the text using NLTK
    tokens = nltk.word_tokenize(text)
    print(tokens)
    # Perform POS tagging using NLTK
    pos_tags = nltk.pos_tag(tokens)

    # Extract nouns based on POS tagging
    nouns = [word for word, pos in pos_tags if pos.startswith('NNP')]

    # Join the nouns to form a string for SpaCy processing
    noun_text = ' '.join(nouns)

    # Use SpaCy for named entity recognition
    doc = nlp(noun_text)

    # Extract personal names based on additional filters
    personal_names = [token.text for token in doc if is_first_name(token)]
    

    return list(set(personal_names))

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
# Example usage
input_text = "John Sharma is a Mtech CSE student from Jadavpur University. His hometown is in Asansol. He has completed Btech from Jadavpur University. He recently applied for a Driving License in West Bengal with the help of his ADHAAR and Voter Card. The ADHAAR number of John is 4567000007865 and the Voter ID number is SYG882745586. But the problem is that the address in the adhaar and the voter id are different. So therefore he was advised to provide his PAN Card having PAN no- AKKJM7875665D and the Bank account statement with an account in State Bank Of India, the account number is 6356278255789."
result = list(extract_cleaned_proper_nouns(input_text))
print("Personal Names:", result)
