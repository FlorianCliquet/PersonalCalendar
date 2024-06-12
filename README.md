# PersonalCalendar

PersonalCalendar is a Python script that automates the creation of Google Calendar events from JSON files in a specified folder. It also provides detailed analytics on time spent on various activities and calculates earnings from paid activities.

## Features

- Create Google Calendar events based on predefined daily schedules.
- Track time spent on different activities.
- Calculate earnings for paid activities.
- Easy setup and configuration with JSON files.

## Prerequisites

- Python 3.6 or higher
- Google Calendar API enabled
- Google OAuth2 credentials

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/FlorianCliquet/PersonalCalendar.git
cd PersonalCalendar
```
### 2. Install required packages
```bash
pip install -r requirements.txt
```
### 3. Set up Google API credentials
Follow the steps to create OAuth2 credentials and download the credentials.json file from the Google Developer Console. Save this file in the root directory of the project.

### 4. Create a .env file
Create a .env file in the root directory with the following variables:
```env
GOOGLECALENDAR_API = your/google/api
JSON_FOLDER=./json/
TOKEN_PATH=path/to/your/tokens
ANALYTICS_CONFIG_PATH=./json/analytics_config.json
CREDENTIALS_PATH=path/to/your/crendetials
```
### 5. Prepare JSON files
Place your JSON files in the json folder. These files should contain your daily schedules and calendar entries.

Example JSON Files
Daily Schedule JSON (e.g., default_day.json, morning_shift.json, afternoon_shift.json)
```json
{
    "activities": [
        {
            "name": "Activity1",
            "start_time": "06:00",
            "end_time": "07:30"
        },
        {
            "name": "Activity2",
            "start_time": "08:00",
            "end_time": "13:15"
        },
        // Add more activities as needed
    ]
}
```
Calendar JSON (calendar.json)
```json
[
    {
        "date": "2024-06-01",
        "type": "morning_shift"
    },
    {
        "date": "2024-06-02",
        "type": "afternoon_shift"
    }
    // Add more dates and types as needed
]
```
### 6. Run the Script
```bash
python main.py
```

## Usage
When you run the script for the first time, it will prompt you to configure analytics for each activity. You can specify whether you want to track time and/or calculate earnings for each activity.

### Analytics Configuration
The script generates an analytics_config.json file based on your inputs. Here is an example:
```json
{
    "Activity1": {
        "name": "Activity1",
        "wage": 15.0
    },
    "Activity2": {
        "name": "Activity2"
    }
}
```
## Output
```yaml
============================================================
Processing entry 1 - Date: 2024-06-01
============================================================
  * Creating events for 2024-06-01, this is a morning_shift day...
  - Event created: Activity1 (2024-06-01T06:00:00+02:00 to 2024-06-01T07:30:00+02:00)
  - Event created: Activity2 (2024-06-01T08:00:00+02:00 to 2024-06-01T13:15:00+02:00)

============================================================
Analytics Summary
============================================================
  Total time spent on Activity1: 1.50 hours, Earnings: €22.50
  Total time spent on Activity2: 5.25 hours
  Total earnings: €22.50
============================================================
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

##
This project is licensed under the MIT License. See the LICENSE file for details.
