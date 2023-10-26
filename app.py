import os
from PyPDF2 import PdfReader  # Use PdfReader instead of PdfFileReader
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'docx'}


def convert_to_plain_text(file_path):
    if file_path.endswith('.pdf'):
        pdf_text = ""
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            for page in pdf_reader.pages:  # Use reader.pages instead of reader.getNumPages()
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
        
        # Convert the file to plain text
        text = convert_to_plain_text(file_path)
        
        return text  # Display the plain text in the web application
    else:
        return "Invalid file format"

if __name__ == '__main__':
    app.run(debug=True)
