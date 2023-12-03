import requests
from bs4 import BeautifulSoup
from nba_api.stats.endpoints import commonallplayers

def get_player_id(player_name):
    players_info = commonallplayers.CommonAllPlayers(is_only_current_season=1)
    players_data = players_info.get_data_frames()[0]

    player_info = players_data[players_data['DISPLAY_FIRST_LAST'].str.lower() == player_name.lower()]

    if not player_info.empty:
        player_id = player_info['PERSON_ID'].iloc[0]
        return player_id
    else:
        return None

def scrape_player_data(player_name):
    player_id = get_player_id(player_name)

    if not player_id:
        print(f"Player {player_name} not found.")
        return

    nba_player_link = f"https://www.nba.com/player/{player_id}/"
    response = requests.get(nba_player_link)

    if response.status_code != 200:
        print(f"Failed to fetch data from {nba_player_link}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    stats_div = soup.find('div', class_='MockStatsTable_statsTable__V_Skx')

    if not stats_div:
        print(f"Div with class 'MockStatsTable_statsTable__V_Skx' not found.")
        return None

    # Find all <tr> elements within the specified <div>
    table_rows = stats_div.find_all('tr')

    if not table_rows:
        print("No table rows found.")
        return None

    # Extract and print the text content of each cell in the table
    for row in table_rows:
        cells = row.find_all(['th', 'td'])  # Adjust if needed
        row_data = [cell.text.strip() for cell in cells]
        print(" | ".join(row_data))

if __name__ == "__main__":
    player_name = input("Enter the player's name: ")
    scrape_player_data(player_name)
