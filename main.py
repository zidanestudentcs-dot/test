import requests
import json

# Facebook App Credentials
APP_ID = "4172288823044992"
APP_SECRET = "8e8378692a8cd80685b60b15287057f6"
ACCESS_TOKEN = "EAALA8LJ24EIBP1zZCKljG6pzo61JGE2ZCKCoZBnEyJqCVsRo9gTAvACxY1QgKsVQoO7mLo6KqJaNmPqTao6nQreaLU6hEXmfVk8eSlFhP8BHVrzrcoBoq8I0nlyIZBZA3ZAeRK7iTesRzPvoZBmh7YUkRzk4VwB6GAHOeSShh7CS5b5pawD8N8zKeXhMZCZC2XQrFKAtX312b29QlWnuuLJcZAnj4ot8JeVrhdlHbnfiAI7xOgPUyyU6RfAZBE5Tf2ZAhOrABG1vHihyAQoje9ZAx4d8xlPsTLbjUMXFiY7M00tUOe47BirZAYh2zNhZBaXesLdoVS2QyXcvpEhkUfv"

# Graph API Base URL
GRAPH_API_URL = "https://graph.facebook.com/v18.0"


def get_page_info(page_id):
    """
    Fetch page information from Facebook Graph API
    
    Args:
        page_id: Facebook Page ID or username
    
    Returns:
        Dictionary containing page information
    """
    # Fields to retrieve from the page
    fields = [
        'id',
        'name',
        'emails',
        'phone',
        'location',
        'single_line_address',
        'website',
        'about',
        'category',
        'cover',
        'fan_count',
        'verification_status',
        'username',
        'link'
    ]
    
    # Construct the API endpoint
    endpoint = f"{GRAPH_API_URL}/{page_id}"
    
    # Parameters for the request
    params = {
        'fields': ','.join(fields),
        'access_token': ACCESS_TOKEN
    }
    
    try:
        # Make the API request
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page info: {e}")
        if response.status_code == 400:
            print("Bad Request - Check your access token and page ID")
        elif response.status_code == 403:
            print("Forbidden - You may not have permission to access this page")
        return None


def get_pages_managed():
    """
    Get all pages managed by the access token owner
    
    Returns:
        List of pages
    """
    endpoint = f"{GRAPH_API_URL}/me/accounts"
    
    params = {
        'access_token': ACCESS_TOKEN
    }
    
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        return response.json().get('data', [])
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching managed pages: {e}")
        return []


def display_page_info(page_data):
    """
    Display page information in a readable format
    
    Args:
        page_data: Dictionary containing page information
    """
    if not page_data:
        print("No data to display")
        return
    
    print("\n" + "="*50)
    print("PAGE INFORMATION")
    print("="*50)
    
    print(f"\nPage Name: {page_data.get('name', 'N/A')}")
    print(f"Page ID: {page_data.get('id', 'N/A')}")
    print(f"Username: {page_data.get('username', 'N/A')}")
    print(f"Category: {page_data.get('category', 'N/A')}")
    print(f"Link: {page_data.get('link', 'N/A')}")
    
    print("\n--- CONTACT INFORMATION ---")
    print(f"Email: {', '.join(page_data.get('emails', ['N/A']))}")
    print(f"Phone: {page_data.get('phone', 'N/A')}")
    print(f"Website: {page_data.get('website', 'N/A')}")
    
    print("\n--- LOCATION ---")
    location = page_data.get('location', {})
    if location:
        print(f"Street: {location.get('street', 'N/A')}")
        print(f"City: {location.get('city', 'N/A')}")
        print(f"State: {location.get('state', 'N/A')}")
        print(f"Country: {location.get('country', 'N/A')}")
        print(f"Zip: {location.get('zip', 'N/A')}")
    else:
        print(f"Address: {page_data.get('single_line_address', 'N/A')}")
    
    print("\n--- ADDITIONAL INFO ---")
    print(f"About: {page_data.get('about', 'N/A')}")
    print(f"Followers: {page_data.get('fan_count', 'N/A')}")
    print(f"Verification: {page_data.get('verification_status', 'N/A')}")
    
    print("\n" + "="*50 + "\n")


def save_to_json(data, filename="page_data.json"):
    """
    Save page data to a JSON file
    
    Args:
        data: Data to save
        filename: Output filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to file: {e}")


def main():
    """
    Main function to run the script
    """
    print("Facebook Page Data Scraper")
    print("="*50)
    
    # Option 1: Get all pages you manage
    print("\nFetching pages you manage...")
    managed_pages = get_pages_managed()
    
    if managed_pages:
        print(f"\nFound {len(managed_pages)} managed page(s):")
        for i, page in enumerate(managed_pages, 1):
            print(f"{i}. {page.get('name')} (ID: {page.get('id')})")
        
        # Fetch detailed info for each managed page
        all_pages_data = []
        for page in managed_pages:
            page_id = page.get('id')
            print(f"\nFetching details for: {page.get('name')}")
            page_info = get_page_info(page_id)
            if page_info:
                display_page_info(page_info)
                all_pages_data.append(page_info)
        
        # Save all data to JSON
        if all_pages_data:
            save_to_json(all_pages_data, "all_pages_data.json")
    
    else:
        # Option 2: Query specific page by ID
        print("\nNo managed pages found or unable to fetch.")
        print("\nEnter a specific Page ID or username to query:")
        page_id = input("Page ID/Username: ").strip()
        
        if page_id:
            print(f"\nFetching information for page: {page_id}")
            page_info = get_page_info(page_id)
            
            if page_info:
                display_page_info(page_info)
                save_to_json(page_info, f"page_{page_id}_data.json")
            else:
                print("Failed to retrieve page information")


if __name__ == "__main__":
    main()
