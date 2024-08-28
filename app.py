from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import pytz
from dateutil.parser import isoparse

load_dotenv()

EST = pytz.timezone('America/New_York')
app = Flask(__name__)
API_KEY = os.getenv('TICKETMASTER_API_KEY')

def convert_to_est(iso_datetime_str):
    utc_time = isoparse(iso_datetime_str)
    est_time = utc_time.astimezone(EST)
    return est_time.strftime('%I:%M %p %Z')

def format_date(iso_date_str):
    date_obj = datetime.strptime(iso_date_str, '%Y-%m-%d')
    return date_obj.strftime('%m/%d/%Y')

with open('static/teams.json', 'r') as file:
    teams_by_league = json.load(file)


def get_tm_event(team, sport):
    url = f"https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        'apikey': API_KEY,
        'keyword': team,
        'classificationName': 'Sports'
    }
    
    response = requests.get(url, params=params)
    data = response.json()

    games = []
    if '_embedded' in data:
        for event in data['_embedded']['events']:
            if team.lower() in event['name'].lower():
                if any(classification.get('subGenre', {}).get('name', '').lower() == sport.lower() for classification in event.get('classifications', [])):
                    iso_date = event['dates']['start']['localDate']
                    event_info = {
                        'name': event['name'],
                        'date': format_date(iso_date),
                        'time': convert_to_est(event['dates']['start']['dateTime']),
                        'venue': event['_embedded']['venues'][0]['name'],
                        'lowest_price': None,
                        'currency': None,
                        'event_url': event['url'],
                        'iso_date': iso_date 
                    }
                    if 'priceRanges' in event:
                        event_info['lowest_price'] = event['priceRanges'][0]['min']
                        event_info['currency'] = event['priceRanges'][0]['currency']

                    games.append(event_info)
    if games:
        games.sort(key=lambda x: datetime.strptime(x['iso_date'], '%Y-%m-%d'))

    return games

@app.route('/')
def index():
    return render_template('index.html', games=[], message="Search for a team to begin")

@app.route('/get_teams', methods=['POST'])
def get_teams():
    league = request.json.get('league')
    teams = teams_by_league.get(league, [])
    return jsonify(teams=teams)

@app.route('/', methods=['POST'])
def index_post():
    sport = request.form['sport']
    team = request.form['team']

    if not sport or not team:
        message = "Please select both a league and a team."
        return render_template('index.html', games=[], message=message)

    games = get_tm_event(team, sport)
    if not games:
        message = "No games found for the specified team."
    else:
        message = ""
    return render_template('index.html', games=games, message=message)

if __name__ == "__main__":
    app.run(debug=True)