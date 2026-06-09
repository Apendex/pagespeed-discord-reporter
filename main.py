import os
import json
import requests
import urllib.parse
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Constants
PAGESPEED_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
TARGET_CATEGORIES = ["performance", "accessibility", "best-practices", "seo"]

def get_pagespeed_data(url: str, strategy: str = "mobile") -> Optional[Dict[str, Any]]:
    """Fetches PageSpeed Insights data for a specific URL and strategy."""
    params: Dict[str, Any] = {
        "url": url,
        "strategy": strategy,
        "category": TARGET_CATEGORIES
    }
    
    api_key = os.getenv("PAGESPEED_INSIGHTS_API_KEY")
    if api_key:
        params["key"] = api_key
        
    print(f"Fetching {strategy} data for {url}...\n")
    
    try:
        response = requests.get(PAGESPEED_API_URL, params=params)
        response.raise_for_status()
        full_data = response.json()
        
        lighthouse_result = full_data.get('lighthouseResult', {})
        categories = lighthouse_result.get('categories', {})
        
        if not categories:
            print("No category data found in the response.")
            return None
            
        # Extract the simple scores for printing
        print(f"--- Results for {url} ({strategy.capitalize()}) ---")
        for category in TARGET_CATEGORIES:
            if category in categories:
                score_data = categories[category].get('score')
                if score_data is not None:
                    score = int(score_data * 100)
                    display_name = category.replace('-', ' ').title()
                    print(f"{display_name:<16}: {score}")
        
        # Return the full data to be saved in JSON
        return full_data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def save_results_to_json(data: Dict[str, Any], filename: str = "pagespeed_insights_results.json") -> None:
    """Saves the PageSpeed results to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"\nResults successfully saved to {filename}")

def create_gist(data: Dict[str, Any], strategy: str) -> Optional[str]:
    """Creates a GitHub Gist with the Full Lighthouse JSON for a specific strategy."""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print(f"\nSkipping Gist creation for {strategy}: GITHUB_TOKEN not found.")
        return None

    print(f"\nCreating {strategy.capitalize()} Gist...")
    
    # We only Gist the lighthouseResult part as that's what the viewer expects
    lighthouse_data = data.get(strategy, {}).get("lighthouseResult", {})
    
    gist_data = {
        "description": f"Lighthouse Report ({strategy}) for {data.get('url')} - {data.get('timestamp')}",
        "public": False,
        "files": {
            f"lighthouse_{strategy}.json": {
                "content": json.dumps(lighthouse_data, indent=4)
            }
        }
    }

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.post("https://api.github.com/gists", json=gist_data, headers=headers)
        response.raise_for_status()
        gist_response = response.json()
        gist_id = gist_response.get("id")
        
        # Format for the Google Lighthouse Viewer
        viewer_url = f"https://googlechrome.github.io/lighthouse/viewer/?gist={gist_id}"
        print(f"{strategy.capitalize()} Gist created: {viewer_url}")
        return viewer_url
    except requests.exceptions.RequestException as e:
        print(f"Error creating {strategy} Gist: {e}")
        return None

def print_mobile_and_desktop_values(filename: str = "pagespeed_insights_results.json") -> None:
    """Reads and prints the mobile and desktop values from the JSON file."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            
        print("\n=== Data from JSON file ===")
        print(f"Target URL: {data.get('url')}")
        print(f"Checked At: {data.get('timestamp')}")
        
        if data.get("mobile_viewer_url"):
            print(f"Mobile Report:   {data.get('mobile_viewer_url')}")
        if data.get("desktop_viewer_url"):
            print(f"Desktop Report:  {data.get('desktop_viewer_url')}")
        
        for strategy in ["mobile", "desktop"]:
            if strategy in data:
                print(f"\n--- {strategy.capitalize()} ---")
                # Navigate to the lighthouse categories in the full response
                strategy_full_data = data[strategy]
                lighthouse_result = strategy_full_data.get('lighthouseResult', {})
                categories = lighthouse_result.get('categories', {})
                
                for category in TARGET_CATEGORIES:
                    if category in categories:
                        score_data = categories[category].get('score')
                        if score_data is not None:
                            score = int(score_data * 100)
                            display_name = category.replace('-', ' ').title()
                            print(f"{display_name}: {score}")
            else:
                print(f"\nNo {strategy} data found in the file.")
    except FileNotFoundError:
        print(f"Error: '{filename}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode '{filename}'.")

if __name__ == "__main__":
    target_url = os.getenv("WEBSITE_URL", "https://berylprojectengineering.com/")
    
    # Structure the root dictionary with metadata fields
    # Format: "January 9, 2026, 9:52:00 AM"
    timestamp_format = "%B %d, %Y, %I:%M:%S %p"
    # Remove leading zero from day if present (standard Python strftime leaves it)
    now = datetime.now()
    formatted_timestamp = now.strftime(timestamp_format).replace(" 0", " ")
    
    # Generate the public web URL
    encoded_url = urllib.parse.quote(target_url, safe='')
    public_report_url = f"https://pagespeed.web.dev/analysis?url={encoded_url}"
    
    all_results = {
        "url": target_url,
        "report_url": public_report_url,
        "timestamp": formatted_timestamp
    }
    
    has_data = False
    for device_strategy in ["mobile", "desktop"]:
        strategy_data = get_pagespeed_data(target_url, strategy=device_strategy)
        if strategy_data:
            all_results[device_strategy] = strategy_data
            has_data = True
            
    if has_data:
        # First save locally
        save_results_to_json(all_results)
        
        # Then create Gists for mobile and desktop to get viewer URLs
        if os.getenv("GITHUB_TOKEN"):
            mobile_viewer = create_gist(all_results, "mobile")
            desktop_viewer = create_gist(all_results, "desktop")
            
            if mobile_viewer:
                all_results["mobile_viewer_url"] = mobile_viewer
            if desktop_viewer:
                all_results["desktop_viewer_url"] = desktop_viewer
                
            # Save again with the new URLs included
            save_results_to_json(all_results)
            
        print_mobile_and_desktop_values()

        # Chain the next scripts
        print("\n--- Starting Image Generation ---")
        subprocess.run(["python", "generate_image.py"], check=True)
        
        print("\n--- Sending to Discord ---")
        subprocess.run(["python", "discord.py"], check=True)
        
        print("\nWorkflow Complete!")