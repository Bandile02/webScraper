import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
from trello import TrelloClient

# Trello API credentials
TRELLO_API_KEY = '7e3bdf4e625f14bb76df90fc154e85a1'
TRELLO_TOKEN = 'ATTA48586a7887d5e68987053c7fd1d72a77fb859beba00c1ffed73a5c365aa7bbe1CE437763'
TRELLO_BOARD_ID = 'PFLsmGNh'  # Your Trello board ID
TRELLO_LIST_NAME = 'OnGoing'  # Trello list name
TRELLO_CARD_NAME = 'Profile'  # Trello card name

# Initialize Trello client
trello_client = TrelloClient(api_key=TRELLO_API_KEY, token=TRELLO_TOKEN)

# Function to get the Trello card ID by name
def get_trello_card_id(list_id, card_name):
    list_obj = trello_client.get_list(list_id)
    cards = list_obj.list_cards()
    for card in cards:
        if card.name == card_name:
            return card.id
    return None

# Function to add a comment to a Trello card
def add_comment_to_card(card_id, comment):
    card = trello_client.get_card(card_id)
    card.comment(comment)

# Function to scrape Forex Factory for monthly news
def scrape_forex_factory():
    url = 'https://www.forexfactory.com/calendar?month=this'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    events = []
    for row in soup.select('tr.calendar_row'):
        impact = row.select_one('.impact')
        if impact and ('high' in impact.get('class') or 'medium' in impact.get('class')):
            date_str = row.select_one('.date').text.strip()
            time_str = row.select_one('.time').text.strip()
            event = row.select_one('.event').text.strip()
            events.append((date_str, time_str, event))

    return events

# Function to find dates with events two hours apart
def find_dates_with_two_hour_gap(events):
    date_time_events = []
    for date_str, time_str, event in events:
        if time_str:  # Skip events with no time
            event_time = datetime.strptime(f"{date_str} {time_str}", "%m-%d-%Y %I:%M%p")
            date_time_events.append(event_time)

    date_time_events.sort()
    two_hour_gap_dates = set()

    for i in range(len(date_time_events) - 1):
        time_diff = abs((date_time_events[i + 1] - date_time_events[i]).total_seconds())
        if time_diff <= 7200:  # 2 hours in seconds
            two_hour_gap_dates.add(date_time_events[i].strftime("%Y-%m-%d"))
            two_hour_gap_dates.add(date_time_events[i + 1].strftime("%Y-%m-%d"))

    return sorted(two_hour_gap_dates)

# Function to process news and comment on Trello card
def process_news_and_comment():
    # Scrape Forex Factory
    events = scrape_forex_factory()
    two_hour_gap_dates = find_dates_with_two_hour_gap(events)

    if not two_hour_gap_dates:
        print("No dates with events two hours apart found.")
        return

    # Get Trello list and card
    board = trello_client.get_board(TRELLO_BOARD_ID)
    lists = board.all_lists()
    ongoing_list = next((lst for lst in lists if lst.name == TRELLO_LIST_NAME), None)
    if not ongoing_list:
        print(f"List '{TRELLO_LIST_NAME}' not found on board '{TRELLO_BOARD_ID}'")
        return

    profile_card = next((card for card in ongoing_list.list_cards() if card.name == TRELLO_CARD_NAME), None)
    if not profile_card:
        print(f"Card '{TRELLO_CARD_NAME}' not found in list '{TRELLO_LIST_NAME}'")
        return

    # Add dates as a comment
    comment = "Dates with events two hours apart:\n" + "\n".join(two_hour_gap_dates)
    add_comment_to_card(profile_card.id, comment)
    print(f"Added comment to card '{TRELLO_CARD_NAME}':\n{comment}")

# Main function
if __name__ == "__main__":
    process_news_and_comment()
