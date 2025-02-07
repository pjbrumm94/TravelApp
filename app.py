from flask import Flask, render_template, request
import gspread
import pandas as pd
import openai

# Flask app
app = Flask(__name__)
