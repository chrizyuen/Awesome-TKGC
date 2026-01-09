import requests

def get_latest_zenodo_records(query="", size=5):
    url = "https://zenodo.org/api/records"
    params = {
        "q": query,
        "sort": "mostrecent",
        "size": size
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        for record in data['hits']['hits']:
            title = record['metadata']['title']
            date = record['created']
            link = record['links']['self_html']
            print(f"[{date}] {title}\nLink: {link}\n")
    else:
        print(f"Error: {response.status_code}")

# Run the monitor
get_latest_zenodo_records(query="climate change")