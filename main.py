import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://fabtcg.com/en/coverage/calling-london-2025/standings/"
PLAYER_NAME = []
WEBHOOK_URL = ""
CHECK_INTERVAL = 60

def get_latest_round():
    """
    Tries to find the latest round that has been posted by checking
    round URLs from 1 to 18 and returning the most recent successful one.
    """
    for i in range(1, 19):
        url = f"{BASE_URL}{i}"
        print(f"Checking round {i} at URL: {url}")
        res = requests.get(url)
        if res.status_code == 200:
            print(f"Found round {i}")
            return i, res.text
        
    return None, None

def find_player(html):
    soup = BeautifulSoup(html, "html.parser")
    table_block = soup.find("div", class_="table-block")
    if not table_block:
        return None
    
    # Find the main standings table
    table = table_block.find("table")
    if not table:
        return 
    
    # Check if any players have dropped out of the tournament
    dropped_section = soup.find("div", class_="dropped-players")
    if dropped_section:
        dropped_table = dropped_section.find("table")
        if dropped_table:
            dropped_rows = dropped_table.find_all("tr")
            for row in dropped_rows:
                row_text = row.get_text(" | ", strip=True)
                for player in PLAYER_NAME[:]: # Copy
                    if player.lower() in row_text.lower():
                        print(f"Player {player} has dropped from the tournament")
                        PLAYER_NAME.remove(player)

    rows = table.find_all("tr")
    found_players = []

    # Search for each player in the table rows
    for player in PLAYER_NAME:
        for row in rows:
            row_text = row.get_text(" | ", strip=True)
            first_part = row_text.split('|')[0].strip()
            if first_part.isdigit() and player.lower() in row_text.lower():
                print(f"Found {player}")
                found_players.append(row_text)

    # Return results sorted by standing
    if found_players:
        found_players.sort(key=lambda x: int(x.split('|')[0].strip()))
        return "\n".join(found_players)
    return None

def send_discord_message(content):
    data = {"content": content}
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Webhook error: {response.text}")

def has_actual_standings(html):
    """
    Checks if a round has actual standings data yet.
    """
    soup = BeautifulSoup(html, "html.parser")
    table_block = soup.find("div", class_="table-block")
    if not table_block:
        return False

    table = table_block.find("table")
    if not table:
        return False

    rows = table.find_all("tr")
    for row in rows:
        row_text = row.get_text(" | ", strip=True)
        first_part = row_text.split('|')[0].strip()
        if first_part.isdigit():
            return True
    return False

def main():
    last_result = ""
    last_round_with_data = 0
    print("Running...")
    while True:
        current_round = last_round_with_data + 1
        url = f"{BASE_URL}{current_round}"
        print(f"Checking round {current_round} at: {url}")
        res = requests.get(url)
        
        if res.status_code == 200:
            result = find_player(res.text)
            if result:
                # Check if next round already has data
                next_round_url = f"{BASE_URL}{current_round + 1}"
                next_round_res = requests.get(next_round_url)
                
                if next_round_res.status_code == 200:
                    if has_actual_standings(next_round_res.text):
                        print(f"Round {current_round + 1} has finished, checking next round...")
                        last_round_with_data = current_round
                        continue
                    else:
                        print(f"Round {current_round + 1} underway...")
                        if result != last_result:
                            message = f"Round {current_round} results:\n```{result}```"
                            send_discord_message(message)
                            last_result = result
                        last_round_with_data = current_round
                else:
                    print(f"Round {current_round + 1} underway...")
                    if result != last_result:
                        message = f"Round {current_round} results:\n```{result}```"
                        send_discord_message(message)
                        last_result = result
                    last_round_with_data = current_round
            else:
                print(f"No standings found in round: {current_round}")
        else:
            print(f"Round {current_round} not available yet")
        
        print(f"New check in {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()