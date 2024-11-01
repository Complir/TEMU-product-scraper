import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def scrape_temu():
    # Get credentials from environment variables
    username = os.getenv('OXYLABS_USERNAME')
    password = os.getenv('OXYLABS_PASSWORD')

    if not username or not password:
        print("❌ Error: Missing Oxylabs credentials!")
        print("Please create a .env file with your credentials:")
        print("OXYLABS_USERNAME=your_username")
        print("OXYLABS_PASSWORD=your_password")
        return

    # API endpoint
    url = "https://realtime.oxylabs.io/v1/queries"

    # Request payload
    payload = {
        "source": "universal_ecommerce",
        "url": "https://www.temu.com/dk/makeup-o3-26.html",
        "geo_location": "Denmark",
        "render": "html",
        "parse": True,
        "parsing_instructions": {
            "items": {
                "selector": "._2KkHWtYf",
                "output": {
                    "title": {
                        "selector": "._3n5ZQDD0",
                        "type": "text"
                    },
                    "price": {
                        "selector": "._2fNrPpGV",
                        "type": "text"
                    },
                    "url": {
                        "selector": "a",
                        "type": "attribute",
                        "attribute": "href"
                    }
                }
            }
        }
    }

    try:
        print("🔄 Sending request to Oxylabs API...")
        response = requests.post(
            url,
            json=payload,
            auth=(username, password),
            headers={'Content-Type': 'application/json'}
        )

        # Check if request was successful
        response.raise_for_status()

        print("✅ Request successful!")
        data = response.json()

        # Save raw response
        with open('raw_response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        if 'results' in data and len(data['results']) > 0:
            result = data['results'][0]

            if 'content' in result and 'items' in result['content']:
                items = result['content']['items']
                print(f"\nFound {len(items)} products:")

                for i, item in enumerate(items, 1):
                    print(f"\nProduct {i}:")
                    print(f"Title: {item.get('title', 'N/A')}")
                    print(f"Price: {item.get('price', 'N/A')}")
                    print(f"URL: {item.get('url', 'N/A')}")
            else:
                print("No parsed items found in response")

    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response text: {e.response.text}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    scrape_temu()
