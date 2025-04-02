import pandas as pd
from openai import OpenAI
client  = OpenAI()

csv_file = "data/example.csv"

if csv_file:
    df = pd.read_csv(csv_file)
            
    # Call OpenAI
    prompt = f"Create a combined travel itinerary combining this information: {df}"
    response = client.responses.create(
        model="gpt-4o",
        input=prompt
        )
    itinerary = response.output_text
print(itinerary)
