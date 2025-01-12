import os
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from trello import TrelloClient

class ForexTrelloUpdater:
    def __init__(self):
        # Initialize Trello credentials
        self.api_key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        
        # Trello configuration
        self.board_id = 'PFLsmGNh'
        self.list_name = 'OnGoing'
        self.card_name = 'Profile'
        
        # Forex Factory configuration
        self.base_url = "https://www.forexfactory.com/calendar"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        }
        
        # Initialize Trello client
        self.trello = TrelloClient(
            api_key=self.api_key,
            token=self.token
        )
    
    def get_card(self):
        """Get the target Trello card"""
        try:
            # Get board
            board = self.trello.get_board(self.board_id)
            
            # Find target list
            target_list = None
            for lst in board.list_lists():
                if lst.name == self.list_name:
                    target_list = lst
                    break
                    
            if not target_list:
                raise Exception(f"List '{self.list_name}' not found")
            
            # Find target card
            target_card = None
            for card in target_list.list_cards():
                if card.name == self.card_name:
                    target_card = card
                    break
                    
            if not target_card:
                raise Exception(f"Card '{self.card_name}' not found")
                
            return target_card
            
        except Exception as e:
            print(f"Error accessing Trello: {e}")
            return None

    def get_forex_news(self) -> List[Dict]:
        """Fetch high-impact forex news"""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []
            current_date = None
            
            for row in soup.find_all('tr', class_='calendar_row'):
                impact = row.find('td', class_='impact')
                if impact and 'high' in str(impact).lower():
                    # Get date if available
                    date_cell = row.find('td', class_='calendar__date')
                    if date_cell and date_cell.text.strip():
                        current_date = date_cell.text.strip()
                    
                    # Extract event details
                    news_item = {
                        'date': current_date,
                        'time': self._get_cell_text(row, 'calendar__time'),
                        'currency': self._get_cell_text(row, 'calendar__currency'),
                        'event': self._get_cell_text(row, 'calendar__event'),
                        'forecast': self._get_cell_text(row, 'calendar__forecast'),
                        'previous': self._get_cell_text(row, 'calendar__previous')
                    }
                    news_items.append(news_item)
            
            return news_items
            
        except Exception as e:
            print(f"Error fetching forex news: {e}")
            return []
    
    def _get_cell_text(self, row: BeautifulSoup, class_name: str) -> str:
        """Extract text from a table cell"""
        cell = row.find('td', class_=class_name)
        return cell.text.strip() if cell else 'N/A'

    def create_comment(self, news_items: List[Dict]) -> str:
        """Create a formatted comment from news items"""
        if not news_items:
            return "No high-impact forex events found."
        
        comment = f"🔔 High Impact Forex Events - Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Group events by date
        current_date = None
        for item in news_items:
            # Add date header if it's a new date
            if item['date'] != current_date:
                current_date = item['date']
                comment += f"📅 {current_date}\n"
            
            # Add event details
            comment += (
                f"⏰ {item['time']} | {item['currency']}\n"
                f"📊 {item['event']}\n"
                f"Forecast: {item['forecast']} | Previous: {item['previous']}\n"
                f"-------------------\n"
            )
        
        return comment

    def update_trello(self):
        """Main method to update Trello card with forex news"""
        print("Starting Forex News update...")
        
        # Get Trello card
        card = self.get_card()
        if not card:
            return
        
        # Get forex news
        news_items = self.get_forex_news()
        
        # Create and post comment
        comment = self.create_comment(news_items)
        try:
            card.comment(comment)
            print(f"Successfully updated Trello card with {len(news_items)} events")
        except Exception as e:
            print(f"Error posting comment to Trello: {e}")

def main():
    # Check for required environment variables
    if not os.getenv('TRELLO_API_KEY') or not os.getenv('TRELLO_TOKEN'):
        print("Error: Missing Trello credentials")
        print("Please set TRELLO_API_KEY and TRELLO_TOKEN environment variables")
        return
    
    # Run the updater
    updater = ForexTrelloUpdater()
    updater.update_trello()

if __name__ == "__main__":
    main()
