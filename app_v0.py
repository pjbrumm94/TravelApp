from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import pandas as pd
import openai
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Google Sheets authentication
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = "path/to/credentials.json"  # Replace with your actual path

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Google Sheet details
SHEET_ID = "your_google_sheet_id"  # Replace with actual Google Sheet ID
WORKSHEET_NAME = "Sheet1"  # Change based on your worksheet name

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "Missing file!", 400

    file = request.files['file']
    
    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Process the file
        data = process_file(filepath)
        
        # Generate itinerary using ChatGPT
        ai_response = generate_itinerary(data)
        
        return f"Generated Itinerary: {ai_response}" 
    
    return "Invalid file type", 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx'}

def process_file(filepath):
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)
    
    return df.to_string(index=False)

def fetch_google_sheet_data():
    """Fetch all responses from Google Sheets"""
    sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
    data = sheet.get_all_records()
    return pd.DataFrame(data).to_string(index=False)

@app.route('/fetch-sheet', methods=['GET'])
def fetch_sheet():
    """Fetch Google Sheets data and generate an itinerary using ChatGPT"""
    data = fetch_google_sheet_data()
    if not data:
        return jsonify({"error": "No data found in Google Sheet"}), 400
    
    ai_response = generate_itinerary(data)
    return jsonify({"itinerary": ai_response})

def generate_itinerary(data):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a travel expert who creates detailed itineraries based on user preferences."},
            {"role": "user", "content": f"Based on the following travel details, generate a detailed itinerary:\n{data}"}
        ]
    )
    return response['choices'][0]['message']['content']

if __name__ == '__main__':
    app.run(debug=True)

