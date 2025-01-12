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
    print(f"Added comment to card: {comment}")

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
    profile_card = next((card for card in ongoing_list.list_cards() if card.name == TRELLO_CARD_NAME), None)
    if not profile_card:
        print(f"Card '{TRELLO_CARD_NAME}' not found in list '{TRELLO_LIST_NAME}'")
        return

    # Add a comment to the card
    comment = "This is a test comment added using the Trello API."
    add_comment_to_card(profile_card.id, comment)

if __name__ == "__main__":
    main()
