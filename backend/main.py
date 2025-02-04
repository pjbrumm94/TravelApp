from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from fastapi.middleware.cors import CORSMiddleware
import os

openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure you have your OpenAI key in environment variables

app = FastAPI()
