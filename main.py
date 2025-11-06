import requests
import sys

def scrape_public_page_simple(page_name, access_token):
    """Simple public page scraper"""
    url = f"https://graph.facebook.com/v19.0/{page_name}"
    params = {
        'access_token': access_token,
        'fields': 'id,name,username,link,about,website,fan_count,category'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            print(f"Error: {data['error']['message']}")
            return None
        
        return data
    except Exception as e:
        print(f"Request failed: {e}")
        return None

# Usage
if __name__ == "__main__":
    ACCESS_TOKEN = "YOUR_TOKEN_HERE"
    
    if len(sys.argv) > 1:
        page_name = sys.argv[1]
        result = scrape_public_page_simple(page_name, ACCESS_TOKEN)
        
        if result:
            print("Page found:")
            for key, value in result.items():
                print(f"{key}: {value}")
        else:
            print("Page not found or access denied")
    else:
        print("Usage: python simple_face.py <page_username>")
