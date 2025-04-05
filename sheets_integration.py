import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os
from datetime import datetime, timedelta
import json

class GoogleSheetsConnector:
    def __init__(self, spreadsheet_id, cache_duration_minutes=60):
        """
        Initialize the Google Sheets connector
        
        Args:
            spreadsheet_id (str): The ID of your Google Spreadsheet
            cache_duration_minutes (int): How long to cache the data before refreshing
        """
        self.spreadsheet_id = spreadsheet_id
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.last_cache_time = None
        self.cached_data = None
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        
    def _get_credentials(self):
        """Get valid user credentials from storage or user."""
        creds = None
        # The file token.json stores the user's access and refresh tokens
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                
        return creds

    def _fetch_sheet_data(self, range_name):
        """Fetch data from Google Sheets."""
        creds = self._get_credentials()
        service = build('sheets', 'v4', credentials=creds)
        
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()
        
        return result.get('values', [])

    def get_data(self, sheet_name, use_cache=True):
        """
        Get data from Google Sheets with optional caching
        
        Args:
            sheet_name (str): Name of the sheet to fetch
            use_cache (bool): Whether to use cached data if available
            
        Returns:
            pandas.DataFrame: The sheet data as a DataFrame
        """
        current_time = datetime.now()
        
        # Check if we should use cached data
        if (use_cache and 
            self.cached_data is not None and 
            self.last_cache_time is not None and 
            current_time - self.last_cache_time < self.cache_duration):
            return self.cached_data
        
        # Fetch fresh data
        data = self._fetch_sheet_data(sheet_name)
        
        if not data:
            return pd.DataFrame()
            
        # Convert to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Update cache
        self.cached_data = df
        self.last_cache_time = current_time
        
        return df

    def get_sales_data(self):
        """
        Get sales data in the format expected by the dashboard
        
        Returns:
            pandas.DataFrame: Formatted sales data
        """
        # Fetch the raw data
        df = self.get_data('Sales')  # Replace with your actual sheet name
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'])
        
        # Convert numeric columns
        numeric_columns = ['sales_amount', 'quantity', 'cost']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df

def setup_sheets_connection(config_file='sheets_config.json'):
    """
    Setup Google Sheets connection using configuration file
    
    Args:
        config_file (str): Path to configuration file
        
    Returns:
        GoogleSheetsConnector: Configured connector instance
    """
    if not os.path.exists(config_file):
        # Create default config if it doesn't exist
        default_config = {
            'spreadsheet_id': 'YOUR_SPREADSHEET_ID',
            'cache_duration_minutes': 60
        }
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f"Created default config file: {config_file}")
        print("Please update the spreadsheet_id in the config file")
        return None
        
    with open(config_file, 'r') as f:
        config = json.load(f)
        
    return GoogleSheetsConnector(
        spreadsheet_id=config['spreadsheet_id'],
        cache_duration_minutes=config.get('cache_duration_minutes', 60)
    ) 