import requests
import json
import re
from typing import Dict, List, Optional

class FacebookPageScraper:
    def __init__(self, app_id: str, app_secret: str, access_token: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v19.0"
        
    def get_user_pages(self) -> List[Dict]:
        """Get all pages managed by the user"""
        try:
            url = f"{self.base_url}/me/accounts"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,username,location,link,phone,emails'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', [])
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching pages: {e}")
            return []
    
    def get_page_details(self, page_id: str) -> Optional[Dict]:
        """Get detailed information about a specific page"""
        try:
            url = f"{self.base_url}/{page_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,username,location,link,phone,emails,about,description,contact_address,single_line_address,hours,website'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page details for {page_id}: {e}")
            return None
    
    def extract_emails_from_text(self, text: str) -> List[str]:
        """Extract email addresses from text using regex"""
        if not text:
            return []
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    def get_page_posts(self, page_id: str, limit: int = 10) -> List[Dict]:
        """Get recent posts from a page to extract contact information"""
        try:
            url = f"{self.base_url}/{page_id}/posts"
            params = {
                'access_token': self.access_token,
                'fields': 'message,story,created_time',
                'limit': limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', [])
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching posts for {page_id}: {e}")
            return []
    
    def extract_contact_info_from_posts(self, page_id: str) -> Dict:
        """Extract contact information from page posts"""
        posts = self.get_page_posts(page_id)
        all_emails = []
        phone_numbers = []
        
        for post in posts:
            message = post.get('message', '') + ' ' + post.get('story', '')
            emails = self.extract_emails_from_text(message)
            all_emails.extend(emails)
            
            # Simple phone number extraction (basic pattern)
            phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            phones = re.findall(phone_pattern, message)
            phone_numbers.extend(phones)
        
        return {
            'emails_from_posts': list(set(all_emails)),
            'phones_from_posts': list(set(phone_numbers))
        }
    
    def get_page_insights(self, page_id: str) -> Optional[Dict]:
        """Get basic insights about the page"""
        try:
            url = f"{self.base_url}/{page_id}/insights"
            params = {
                'access_token': self.access_token,
                'metric': 'page_impressions,page_engaged_users',
                'period': 'day'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching insights for {page_id}: {e}")
            return None
    
    def scrape_all_pages_info(self) -> List[Dict]:
        """Main function to scrape all information from managed pages"""
        print("Fetching user pages...")
        pages = self.get_user_pages()
        
        if not pages:
            print("No pages found or error accessing pages.")
            return []
        
        print(f"Found {len(pages)} pages. Gathering detailed information...")
        
        results = []
        
        for page in pages:
            print(f"Processing page: {page.get('name')}")
            
            # Get detailed page information
            page_details = self.get_page_details(page['id'])
            
            # Extract contact info from posts
            contact_from_posts = self.extract_contact_info_from_posts(page['id'])
            
            # Get page insights
            insights = self.get_page_insights(page['id'])
            
            # Combine all information
            page_info = {
                'page_id': page.get('id'),
                'page_name': page.get('name'),
                'username': page.get('username'),
                'page_link': page.get('link'),
                'location': page_details.get('location') if page_details else None,
                'contact_address': page_details.get('contact_address') if page_details else None,
                'single_line_address': page_details.get('single_line_address') if page_details else None,
                'official_phone': page_details.get('phone'),
                'official_emails': page_details.get('emails', []),
                'website': page_details.get('website'),
                'about': page_details.get('about'),
                'emails_from_posts': contact_from_posts['emails_from_posts'],
                'phones_from_posts': contact_from_posts['phones_from_posts'],
                'insights': insights
            }
            
            results.append(page_info)
            
            print(f"Completed: {page.get('name')}")
            print("-" * 50)
        
        return results
    
    def save_results(self, results: List[Dict], filename: str = "facebook_pages_data.json"):
        """Save results to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving results: {e}")

def main():
    # Replace these with your actual credentials
    # IMPORTANT: Never commit real tokens to code!
    APP_ID = "4172288823044992"
    APP_SECRET = "8e8378692a8cd80685b60b15287057f6"
    ACCESS_TOKEN = "EAALA8LJ24EIBP1zZCKljG6pzo61JGE2ZCKCoZBnEyJqCVsRo9gTAvACxY1QgKsVQoO7mLo6KqJaNmPqTao6nQreaLU6hEXmfVk8eSlFhP8BHVrzrcoBoq8I0nlyIZBZA3ZAeRK7iTesRzPvoZBmh7YUkRzk4VwB6GAHOeSShh7CS5b5pawD8N8zKeXhMZCZC2XQrFKAtX312b29QlWnuuLJcZAnj4ot8JeVrhdlHbnfiAI7xOgPUyyU6RfAZBE5Tf2ZAhOrABG1vHihyAQoje9ZAx4d8xlPsTLbjUMXFiY7M00tUOe47BirZAYh2zNhZBaXesLdoVS2QyXcvpEhkUfv"
    
    # Initialize the scraper
    scraper = FacebookPageScraper(APP_ID, APP_SECRET, ACCESS_TOKEN)
    
    # Scrape all pages information
    results = scraper.scrape_all_pages_info()
    
    # Display results
    if results:
        print("\n" + "="*60)
        print("SCRAPING RESULTS SUMMARY")
        print("="*60)
        
        for result in results:
            print(f"\nPage: {result['page_name']} (@{result['username']})")
            print(f"ID: {result['page_id']}")
            print(f"Link: {result['page_link']}")
            
            if result['location']:
                print(f"Location: {result['location']}")
            
            if result['single_line_address']:
                print(f"Address: {result['single_line_address']}")
            
            if result['official_phone']:
                print(f"Official Phone: {result['official_phone']}")
            
            if result['official_emails']:
                print(f"Official Emails: {', '.join(result['official_emails'])}")
            
            if result['website']:
                print(f"Website: {result['website']}")
            
            if result['emails_from_posts']:
                print(f"Emails from posts: {', '.join(result['emails_from_posts'])}")
            
            if result['phones_from_posts']:
                print(f"Phones from posts: {', '.join(result['phones_from_posts'])}")
            
            print("-" * 40)
        
        # Save results to file
        scraper.save_results(results)
    else:
        print("No data collected.")

if __name__ == "__main__":
    main()
