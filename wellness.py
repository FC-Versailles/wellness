#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 09:15:01 2025

@author: fcvmathieu
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import pickle
import pandas as pd

# Define the scope and token file path
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
TOKEN_FILE = 'token.pickle'

def get_credentials():
    creds = None
    # Check if token file exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    # If no valid credentials, authenticate and save them
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_101127780883-ta4f42s2l78afbs74nm0do7mmb9mcdng.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def fetch_google_sheet(spreadsheet_id, range_name):
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    return pd.DataFrame(values[1:], columns=values[0])

# Specify the Google Sheet ID and range
SPREADSHEET_ID = '1tiCkE28kdrP4BOyUHCSo83WYRvwLdlALRuPiv-cDsHU'
RANGE_NAME = 'Feuille 1'  # Fetches all rows and columns in the sheet


# Fetch the data and display the DataFrame
df = fetch_google_sheet(SPREADSHEET_ID, RANGE_NAME)
print(df)

chemin = '/Users/fcvmathieu/Desktop//wellness/df.csv'  # Pour Windows
df.to_csv(chemin, index=False)  # `index=False` pour ne pas inclure l'index du DataFrame dans le fichier CSV
