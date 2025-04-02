import os
import pandas as pd
import openai
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Set your OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    itinerary = None

    if request.method == "POST":
        csv_file = request.files.get("data/example.csv")

        if csv_file:
            df = pd.read_csv(csv_file)
            
            # Call OpenAI
            prompt = f"Create a travel itinerary based on this information: {df}"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            itinerary = response['choices'][0]['message']['content']

    return render_template("index.html", itinerary=itinerary)

if __name__ == "__main__":
    app.run(debug=True)

