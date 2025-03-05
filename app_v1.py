import os
import openai
import gspread
import googlemaps
from collections import Counter
from flask import Flask, jsonify
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

# Google Sheets authentication
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = "path/to/credentials.json"

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

SHEET_ID = "your_google_sheet_id"
WORKSHEET_NAME = "Form Responses 1"

def fetch_travel_data():
    """Fetch all responses from Google Sheets"""
    sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
    data = sheet.get_all_records()
    return data

def find_common_destination(travel_data):
    """Finds the best compromise destination for all travelers"""

    locations = []
    distances = []
    travel_types = []
    budgets = []

    for entry in travel_data:
        locations.append(entry["Current Location"])
        distances.append(int(entry["Max Distance (miles)"]))
        travel_types.extend(entry["Preferred Travel Type"].split(", "))
        budgets.append(entry["Budget"])

    # Find central location
    central_location = locations[0]  # Start with first location
    avg_distance = sum(distances) // len(distances)  # Average max distance

    # Find the most popular travel type
    most_common_type = Counter(travel_types).most_common(1)[0][0]

    # Find the most common budget
    most_common_budget = Counter(budgets).most_common(1)[0][0]

    # Use Google Maps to find a good meeting point within avg_distance
    geocode_result = gmaps.geocode(central_location)
    if not geocode_result:
        return None

    user_lat = geocode_result[0]["geometry"]["location"]["lat"]
    user_lng = geocode_result[0]["geometry"]["location"]["lng"]

    places_result = gmaps.places_nearby(
        location=(user_lat, user_lng),
        radius=avg_distance * 1609,  # Convert miles to meters
        keyword=most_common_type,
        type="tourist_attraction"
    )

    best_destination = places_result["results"][0]["name"] if places_result["results"] else "a location fitting your group's preferences"

    return best_destination, most_common_type, most_common_budget

def generate_group_itinerary(travel_data):
    """Generate a single itinerary considering multiple users' inputs"""
    destination, travel_type, budget = find_common_destination(travel_data)

    prompt = f"""
    A group of travelers with different preferences are planning a trip.
    - They are traveling from different locations but want to meet at a central destination.
    - They prefer {travel_type} experiences.
    - Their budget preference is {budget}.
    - The best destination for them is {destination}.
    
    Create a detailed itinerary for this group.
    """

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

    itinerary = generate_group_itinerary(travel_data)
    return jsonify({"itinerary": itinerary})

if __name__ == "__main__":
    app.run(debug=True)

