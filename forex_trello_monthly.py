import os
from requests_html import HTMLSession
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

# Function to scrape Forex Factory for news on a specific date
def scrape_forex_factory(date):
    url = f'https://www.forexfactory.com/calendar?day={date}'
    session = HTMLSession()
    try:
        response = session.get(url)
        response.html.render()  # Render JavaScript
        soup = response.html

        events = []
        for row in soup.find('tr.calendar_row'):
            impact = row.find('.impact', first=True)
            if impact and ('high' in impact.attrs.get('class', []) or 'medium' in impact.attrs.get('class', [])):
                date_str = row.find('.date', first=True).text.strip()
                time_str = row.find('.time', first=True).text.strip()
                event = row.find('.event', first=True).text.strip()
                events.append((date_str, time_str, event))

        return events
    except Exception as e:
        print(f"Error fetching forex news: {e}")
        return []

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
    # Specify the date to scrape (January 19, 2024)
    date_to_scrape = 'jan19.2024'

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

    # Scrape Forex Factory for the specified date
    events = scrape_forex_factory(date_to_scrape)

    if not events:
        print(f"No high or mid-impact events found for {date_to_scrape}.")
        return

    # Add new comments to the card
    add_new_comments(profile_card, events)

if __name__ == "__main__":
    main()
