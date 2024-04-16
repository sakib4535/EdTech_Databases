import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pymongo import MongoClient
import pandas as pd
import os


SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = "1ff8_A1pH2omeiNdmupDLbGQduCs7XzlZKc4vaG_QU6s"
MONGODB_URI = "mongodb://localhost:27017/"
MONGODB_DB = "edtech_database"
MONGODB_COLLECTION = "student_records"

def main():
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPE)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPE)
            credentials = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(credentials.to_json())

    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheets = service.spreadsheets()

        result = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range="Math_Database!A1:M102").execute()

        values = result.get('values', [])

        if not values:
            print("No Data Found")
        else:
            df = pd.DataFrame(values[1:], columns=values[0])
            client = MongoClient(MONGODB_URI)
            db = client[MONGODB_DB]
            collection = db[MONGODB_COLLECTION]
            records = df.to_dict(orient='records')
            collection.insert_many(records)
            return df


    except HttpError as error:
        print(error)

def print_database():
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION]
    documents = collection.find()
    for document in documents:
        print(document)

if __name__ == '__main__':
    df = main()
    if df is not None:
        print("Inserted data into MongoDB:")
        print(df)
        print("\nDatabase contents:")
        print_database()




