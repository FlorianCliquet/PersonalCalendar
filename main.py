import os
import json
import pytz
from datetime import datetime as dt, timedelta
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
dotenv_path = './../ConfigShit/PersonalCalendar/.env'
load_dotenv(dotenv_path)

# Set up environment variables
print("\n" + "=" * 60)
print("Environment Variables Loaded:")
print("=" * 60)
print(f"JSON_FOLDER: {os.getenv('JSON_FOLDER')}")
print(f"TOKEN_PATH: {os.getenv('TOKEN_PATH')}")
print(f"CREDENTIALS_PATH: {os.getenv('CREDENTIALS_PATH')}")
print(f"ANALYTICS_CONFIG_PATH: {os.getenv('ANALYTICS_CONFIG_PATH')}")

# Set up environment variables
json_folder = os.getenv('JSON_FOLDER')
token_path = os.getenv('TOKEN_PATH')
credentials_path = os.getenv('CREDENTIALS_PATH')
analytics_config_path = os.getenv('ANALYTICS_CONFIG_PATH')

# Google Calendar API variables
SCOPES = ["https://www.googleapis.com/auth/calendar"]
paris_timezone = pytz.timezone('Europe/Paris')

# Function to read JSON data from a file
def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to write JSON data to a file
def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to get Google Calendar credentials
def get_credentials():
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds

# Function to create a Google Calendar event
def create_google_calendar_event(service, calendar_id, event_info):
    event = {
        'summary': event_info['name'],
        'start': {
            'dateTime': event_info['start_time'],
            'timeZone': 'Europe/Paris',
        },
        'end': {
            'dateTime': event_info['end_time'],
            'timeZone': 'Europe/Paris',
        }
    }
    try:
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"  - Event created: {event_info['name']} ({event_info['start_time']} to {event_info['end_time']})")
    except HttpError as error:
        print(f"  ! An HTTP error occurred: {error}")
        print(f"  ! Error details: {error.content}")

# Function to calculate the duration in hours between two time strings
def calculate_duration(start_time, end_time):
    start_dt = dt.strptime(start_time, '%H:%M')
    end_dt = dt.strptime(end_time, '%H:%M')
    duration = end_dt - start_dt
    return duration.total_seconds() / 3600

# Function to set up analytics configuration
def setup_analytics_config(day_info):
    print("\nSetting up analytics configuration...")
    config = {}
    for activity in day_info['activities']:
        track = input(f"Do you want to track analytics for '{activity['name']}'? (yes/no): ").strip().lower()
        if track == 'yes':
            config[activity['name']] = {'name': activity['name']}
            is_money = input(f"Is '{activity['name']}' a paid activity? (yes/no): ").strip().lower()
            if is_money == 'yes':
                wage = float(input(f"Enter the hourly wage for '{activity['name']}': ").strip())
                config[activity['name']]['wage'] = wage
    write_json(analytics_config_path, config)
    print("Analytics configuration saved.")

# Function to load or create analytics configuration
def get_analytics_config(day_info):
    if os.path.exists(analytics_config_path):
        return read_json(analytics_config_path)
    else:
        setup_analytics_config(day_info)
        return read_json(analytics_config_path)

# Main function
def main():
    # Get Google Calendar credentials and service
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    
    # Read JSON data from files
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json') and 'analytics_config' not in f]
    day_types = {}
    for file in json_files:
        file_path = os.path.join(json_folder, file)
        day_types[file.split('.')[0]] = read_json(file_path)

    # Read calendar entries
    calendar_path = os.path.join(json_folder, 'calendar.json')
    calendar = read_json(calendar_path)
    
    # Set up analytics configuration using the first day type for initial setup
    if len(day_types) > 0:
        first_day_type = list(day_types.values())[0]
        analytics_config = get_analytics_config(first_day_type)
    else:
        print("No day types found in JSON folder.")
        return

    analytics_data = {key: 0 for key in analytics_config.keys()}

    print("\nCreating events in Google Calendar...")
    day = 0
    # Iterate over calendar entries and create events
    for entry in calendar:
        print("\n" + "=" * 60)
        print(f"Processing entry {day + 1} - Date: {entry['date']}")
        print("=" * 60)
        day += 1
        date = entry['date']
        day_type = entry['type']

        if day_type in day_types:
            day_info = day_types[day_type]
        else:
            print(f"  ! Unknown day type '{day_type}' for date {date}. Skipping...")
            continue
        print(f"  * Creating events for {date}, this is a {day_type} day...")
        for activity in day_info['activities']:
            start_time = f"{date}T{activity['start_time']}:00+02:00"  # Adjust for Paris timezone
            end_time = f"{date}T{activity['end_time']}:00+02:00"    # Adjust for Paris timezone
            event_info = {
                'name': activity['name'],
                'start_time': start_time,
                'end_time': end_time
            }
            # Create the Google Calendar event
            create_google_calendar_event(service, 'primary', event_info)

            # Calculate the duration of each activity for analytics
            duration = calculate_duration(activity['start_time'], activity['end_time'])
            if activity['name'] in analytics_config:
                analytics_data[activity['name']] += duration

    # Print the analytics
    print("\n" + "=" * 60)
    print("Analytics Summary")
    print("=" * 60)
    total_earnings = 0
    for activity, duration in analytics_data.items():
        if 'wage' in analytics_config[activity]:
            earnings = duration * analytics_config[activity]['wage']
            total_earnings += earnings
            print(f"  Total time spent on {activity}: {duration:.2f} hours, Earnings: €{earnings:.2f}")
        else:
            print(f"  Total time spent on {activity}: {duration:.2f} hours")
    if total_earnings > 0:
        print(f"  Total earnings: €{total_earnings:.2f}")
    print("=" * 60)

if __name__ == "__main__":
    main()