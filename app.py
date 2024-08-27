from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import config
import json

app = Flask(__name__)
API_KEY = config.API_KEY

with open('static/teams.json', 'r') as file:
    teams_by_league = json.load(file)


def get_team_games(team, sport):
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
                    event_info = {
                        'name': event['name'],
                        'date': event['dates']['start']['localDate'],
                        'time': event['dates']['start']['localTime'],
                        'venue': event['_embedded']['venues'][0]['name'],
                        'lowest_price': None,
                        'currency': None,
                        'event_url': event['url']
                    }
                    if 'priceRanges' in event:
                        event_info['lowest_price'] = event['priceRanges'][0]['min']
                        event_info['currency'] = event['priceRanges'][0]['currency']

                    games.append(event_info)
    games.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))

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
    games = get_team_games(team, sport)
    if not games:
        message = "No games found for the specified team."
    else:
        message = ""
    return render_template('index.html', games=games, message=message)

if __name__ == "__main__":
    app.run(debug=True)