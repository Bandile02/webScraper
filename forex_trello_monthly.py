import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from trello import TrelloClient

# Trello API credentials (read from environment variables)
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
TRELLO_BOARD_ID = 'PFLsmGNh'  # Your Trello board ID
TRELLO_LIST_NAME = 'OnGoing'  # Trello list name
TRELLO_CARD_NAME = 'Profile'  # Trello card name

# Initialize Trello client
trello_client = TrelloClient(api_key=TRELLO_API_KEY, token=TRELLO_TOKEN)

# Function to get the Trello card by name
def get_trello_card(list_id, card_name):
    list_obj = trello_client.get_list(list_id)
    cards = list_obj.list_cards()
    for card in cards:
        if card.name == card_name:
            return card
    return None

# Function to fetch existing comments on the card
def fetch_existing_comments(card):
    comments = card.fetch_comments()
    return [comment['data']['text'] for comment in comments]


    events = []
    for row in soup.select('tr.calendar_row'):
        impact = row.select_one('.impact')
        if impact and ('high' in impact.get('class') or 'medium' in impact.get('class')):
            date_str = row.select_one('.date').text.strip()
            time_str = row.select_one('.time').text.strip()
            event = row.select_one('.event').text.strip()
            events.append((date_str, time_str, event))

    return events

# Function to add new comments to the card
def add_new_comments(card, events):
    existing_comments = fetch_existing_comments(card)
    for date_str, time_str, event in events:
        comment = f"Event: {event} | Date: {date_str} | Time: {time_str}"
        if comment not in existing_comments:
            card.comment(comment)
            print(f"Added comment: {comment}")

# Main function
def main():

    # Get the board
    board = trello_client.get_board(TRELLO_BOARD_ID)

    # Get the list
    lists = board.all_lists()
    ongoing_list = next((lst for lst in lists if lst.name == TRELLO_LIST_NAME), None)
    if not ongoing_list:
        print(f"List '{TRELLO_LIST_NAME}' not found on board '{TRELLO_BOARD_ID}'")
        return

    # Get the card
    profile_card = get_trello_card(ongoing_list.id, TRELLO_CARD_NAME)
    if not profile_card:
        print(f"Card '{TRELLO_CARD_NAME}' not found in list '{TRELLO_LIST_NAME}'")
        return

    if not events:
        print(f"No high or mid-impact events found for {date_to_scrape}.")
        return

    # Add new comments to the card
    add_new_comments(profile_card, events)

if __name__ == "__main__":
    main()
