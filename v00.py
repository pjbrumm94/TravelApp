import pandas as pd
from openai import OpenAI
client  = OpenAI()

def loadGS(name, id):
    url = f"https://docs.google.com/spreadsheets/d/{id}/gviz/tq?tqx=out:csv&sheet={name}"
    return(pd.read_csv(url))

def llm_prompt(data):
    # Call OpenAI
    prompt = f"Create a combined travel itinerary combining this information:{data}"
    response = client.responses.create(
        model="gpt-4o",
        input=prompt
        )
    return(response.output_text)

# Main Script
sheet_name  = 'TravelCriteria'
sheet_id    = '1q-xznX5gGTMO9eEcYhJl_uMiKdOuju9A3tujfZvdXlU'

# Load Google Sheet into DataFrame
data        = loadGS(sheet_name, sheet_id)
# Send Google Sheet data to llm prompt
itinerary   = llm_prompt(data)
print(itinerary)
