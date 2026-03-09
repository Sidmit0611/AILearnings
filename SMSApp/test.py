import gspread
from google.oauth2.service_account import Credentials

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_file("smart-expense-tracker-creds.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = "1PVJXZ86PE8Q4ZLeB5l245aLYUkQlteKPwp3Cyb4PQgc"

sheet = client.open_by_key(sheet_id)
values_list = sheet.sheet1.row_values(1)
print(values_list)