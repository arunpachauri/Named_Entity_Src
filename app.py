from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os, sys
import pandas as pd
from collections import Counter
from flask import send_file
import spacy
from spacy import displacy

# Upload folder location will upload text file in cur dir > uploads.
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
 
# Define allowed files
ALLOWED_EXTENSIONS = {'txt'}
 
app = Flask(__name__)
 
# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

words = []

# Load the small English model
nlp = spacy.load("en_core_web_sm")# Process the text

@app.route('/',methods = ['POST', 'GET'])
def result():
    # This function will return result based on selected input or file upload option.
    return render_template("result.html")


@app.route('/download',methods = ['GET'])
def downloadFile ():
    # This function will download result file in txt format.
    path = "entity_table.csv"
    return send_file(path, as_attachment=True)

@app.route('/file_upload',methods = ['POST'])
def file_upload():
   if request.method == 'POST':
        # This function will upload file and do the spell corrector.
        file = request.files['customFile']
        if file:
            data = file.read()
            # Ensure the text is a string
            data = data.decode("utf-8")
        if data is not None:
            doc = named_entity(data)
            if doc:
                # Use displaCy to render the Named Entities as HTML
                html = displacy.render(doc, style="ent", page=True)  # page=True renders full HTML page
                highlighted_text, percent_table = calculate_percent_entities(doc, data)
            return render_template('result.html', content=html)
   else:
      return render_template("result.html")

def named_entity(data):
    if isinstance(data, str):
        # Process the text
        doc = nlp(data)
        return doc

def calculate_percent_entities(doc, data):
    # Extract named entities and percentages
    entity_data = []
    percent_entities = []
    
    # Iterate over entities
    for ent in doc.ents:
        if ent.label_ == "PERCENT":  # Filter only PERCENT entities
            percent_entities.append(ent.text)
            print(ent.text, ent.label_)
        entity_data.append((ent.text, ent.label_))

    # Create a dataframe for the table
    entity_df = pd.DataFrame(entity_data, columns=["Entity", "Label"])
    
    # Filter for PERCENT entities
    percent_df = entity_df[entity_df["Label"] == "PERCENT"]

    # Write the PERCENT entities table to a CSV file
    try:
        percent_df.to_csv("entity_table.csv", index=False)
        print("CSV file created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    
    # Highlight named entities in the text
    highlighted_text = data
    for ent in doc.ents:
        # Replace the original text with highlighted format (e.g., [entity (label)])
        highlighted_text = highlighted_text[:ent.start_char] + f"[{ent.text} ({ent.label_})]" + highlighted_text[ent.end_char:]

    return highlighted_text, percent_df

if __name__ == '__main__':
   app.run(debug = True)