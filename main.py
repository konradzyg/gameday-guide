import requests
from datetime import datetime
import api_key

API_KEY = api_key.API_KEY

def get_team_games(team):
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
                if any(classification.get('subGenre', {}).get('name', '').lower() == 'nfl' for classification in event.get('classifications', [])):
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

def print_games(games):
    for game in games:
        print(f"Event: {game['name']}")
        print(f"Date: {game['date']} Time: {game['time']}")
        print(f"Venue: {game['venue']}")
        if game['lowest_price']:
            print(f"Lowest Price: {game['lowest_price']} {game['currency']}")
        else:
            print("Price information not available")
        print(f"Ticketmaster Page: {game['event_url']}")
        print("-" * 40)

if __name__ == "__main__":
    team = input("Enter the NFL team name: ")
    games = get_team_games(team)
    if games:
        print_games(games)
    else:
        print("No games found for the specified team.")
