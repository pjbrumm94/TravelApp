import os
import openai
from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Load OpenAI API Key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Google Sheets authentication
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = "path/to/credentials.json"

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Your Google Sheet ID
SHEET_ID = "#########"
WORKSHEET_NAME = "#######"

def fetch_travel_data():
    sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
    data = sheet.get_all_records()
    return data

def generate_itinerary(travel_details):
    prompt = f"Create a detailed travel itinerary for the following trip details: {travel_details}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    
    return response["choices"][0]["message"]["content"]

@app.route("/generate-itinerary", methods=["GET"])
def generate():
    travel_data = fetch_travel_data()
    if not travel_data:
        return jsonify({"error": "No travel data found"}), 400

    itinerary = generate_itinerary(travel_data[-1])  # Process the latest entry
    return jsonify({"itinerary": itinerary})

if __name__ == "__main__":
    app.run(debug=True)
