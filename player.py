from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from nba_api.stats.endpoints import commonallplayers

app = Flask(__name__)

# Define the desired order of columns
COLUMN_ORDER = [
    'Game Date', 'Matchup', 'W/L', 'MIN', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA',
    '3P%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV',
    'PF', '+/-'
]

def get_player_id(player_name):
    players_info = commonallplayers.CommonAllPlayers(is_only_current_season=1)
    players_data = players_info.get_data_frames()[0]

    player_info = players_data[players_data['DISPLAY_FIRST_LAST'].str.lower() == player_name.lower()]

    if not player_info.empty:
        player_id = player_info['PERSON_ID'].iloc[0]
        return player_id
    else:
        return None

def fetch_player_stats_html(player_id):
    nba_player_link = f"https://www.nba.com/player/{player_id}/"
    response = requests.get(nba_player_link)

    if response.status_code != 200:
        return None

    return response.text

def parse_player_stats(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    stats_div = soup.find('div', class_='MockStatsTable_statsTable__V_Skx')

    if not stats_div:
        return None

    table_rows = stats_div.find_all('tr')

    if not table_rows:
        return None

    json_data = []

    for row in table_rows[1:]:
        cells = row.find_all(['th', 'td'])
        row_data = [cell.text.strip() for cell in cells]
        row_dict = {COLUMN_ORDER[i]: value for i, value in enumerate(row_data)}
        json_data.append(row_dict)

    return json_data

@app.route('/api/player-stats', methods=['GET'])
def api_player_stats():

    player_name = request.args.get('player_name')

    if not player_name:
        return jsonify({'error': 'Player name is required.'})

    player_id = get_player_id(player_name)

    if not player_id:
        return jsonify({'error': f'Player {player_name} not found.'})

    html_content = fetch_player_stats_html(player_id)

    if not html_content:
        return jsonify({'error': f'Data not available for {player_name}.'})

    player_stats = parse_player_stats(html_content)

    if not player_stats:
        return jsonify({'error': 'Failed to parse player stats.'})

    return jsonify(player_stats)

if __name__ == '__main__':
    app.run(debug=True)
