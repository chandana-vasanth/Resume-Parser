import os
from PyPDF2 import PdfReader
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import names

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

nltk.download('names')  # Download the names dataset for NLTK

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'docx'}

def convert_to_plain_text(file_path):
    if file_path.endswith('.pdf'):
        pdf_text = ""
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
        return pdf_text
    elif file_path.endswith('.docx'):
        from docx import Document
        doc = Document(file_path)
        doc_text = "\n".join([p.text for p in doc.paragraphs])
        return doc_text
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as txt_file:
            return txt_file.read()
    else:
        return "Unsupported file format"

def is_name(word):
    # Check if the word is a common name using NLTK's names.words() dataset
    return word in names.words() or word.lower() in names.words()

def extract_information(text):
    email_pattern = r'\S+@\S+'
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    qualification_pattern = r'(Bachelor|Master|Ph\.?D\.?)\'?s? (of)? (\w+)'
    college_pattern = r'(.+) University|College|Institute'
    specialization_pattern = r'in (\w+)'

    name = ""
    email = ""
    mobile_number = ""
    highest_qualification = ""
    college = ""
    specialization = ""
    year_of_graduation = ""

    sentences = sent_tokenize(text)
    for sentence in sentences:
        words = word_tokenize(sentence)
        for word in words:
            if is_name(word):
                name = word
                break

    email_match = re.search(email_pattern, text)
    if email_match:
        email = email_match.group()
    parts = email.split("@")
    name = ''.join(filter(str.isalpha, parts[0]))
    name=name.capitalize()

    phone_match = re.search(phone_pattern, text)
    if phone_match:
        mobile_number = phone_match.group()

    qualification_match = re.search(qualification_pattern, text)
    college_match = re.search(college_pattern, text)
    specialization_match = re.search(specialization_pattern, text)

    if qualification_match:
        highest_qualification = qualification_match.group(3)
    
    if college_match:
        college = college_match.group(1)
    
    if specialization_match:
        specialization = specialization_match.group(1)

    year_matches = re.findall(r'(\d{4})', text)
    if year_matches:
        year_of_graduation = year_matches[-1]
    
    print(name)

    return {
        'Name': name,
        'Email': email,
        'Mobile Number': mobile_number,
        'Highest Qualification': highest_qualification,
        'College': college,
        'Specialization': specialization,
        'Year of Graduation': year_of_graduation,
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        text = convert_to_plain_text(file_path)
        extracted_info = extract_information(text)
        
        return render_template('result.html', info=extracted_info)
    else:
        return "Invalid file format"

if __name__ == '__main__':
    app.run(debug=True)
