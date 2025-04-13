# Standings Tracker

This Python script automatically tracks the round-by-round tournament standings of players you want to follow and sends Discord notifications whenever standings are updated.

## What It Does

- Periodically checks the standings page for each new round.
- Finds and extracts information about the players you're following.
- Detects if a player has dropped from the event.
- Sends an update to a specified Discord webhook if new data is found.


## Usage
- BASE_URL = url you want to watch for example "https://fabtcg.com/en/coverage/pro-tour-london/standings/"
- PLAYER_NAME = list of player names
- WEBHOOK_URL = Go to discord -> Server Settings -> integrations -> Webhooks -> create new one and/or copy webhook URL here

(make venv optionally before this)
pip install -r requirements.txt

run the main.py