import os
from apify_client import ApifyClient

# Initialize the ApifyClient with your Apify API token
# Replace '<YOUR_API_TOKEN>' with your token.
client = ApifyClient(os.getenv('APIFY_API'))

# Prepare the Actor input
run_input = {
    "startUrls": [
        {"url": "https://www.temu.com/de/100pcs-colored-acrylic-crystal-beads-round-crackle-glass-beads-for-faux-jewelry-making-bracelets-earring-necklace-keychains-adults-beading-diy-art-craft-projects-christmas-ornament-birthday-gifts-8mm-0-31in-g-601099512321944.html"},
        {"url": "https://www.temu.com/de/jewelry-making-accessories-o3-1485.html"},
    ],
    "proxy": {
        "useApifyProxy": True,
        "apifyProxyCountry": "DE",
        "apifyProxyGroups": ["RESIDENTIAL"],
    },
    "resultsLimit": 20,
}

# Run the Actor and wait for it to finish
run = client.actor("mscraper/temu-scraper").call(run_input=run_input)

# Fetch and print Actor results from the run's dataset (if there are any)
print("💾 Check your data here: https://console.apify.com/storage/datasets/" +
      run["defaultDatasetId"])
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)

# 📚 Want to learn more 📖? Go to → https://docs.apify.com/api/client/python/docs/quick-start
