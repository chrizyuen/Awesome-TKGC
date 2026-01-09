import os
import re
import requests
from urllib.parse import urlparse
from typing import Set

def get_urls_from_markdown(file_path: str) -> Set[str]:
    """Extracts all URLs from a markdown file."""
    urls = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Match URLs in markdown links [text](url)
            markdown_links = re.findall(r'\[.*?\]\((https?://.*?)\)', content)
            urls.update(markdown_links)
            
            # Match plain URLs
            plain_urls = re.findall(r'(https?://[^\s)\]]+)', content)
            urls.update(plain_urls)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return urls

def is_pdf(url: str) -> bool:
    """Checks if a URL points to a PDF by extension or content-type."""
    if url.lower().endswith('.pdf'):
        return True
    
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' in content_type:
            return True
    except Exception:
        pass
    return False

def download_pdf(url: str, output_dir: str):
    """Downloads a PDF from a URL."""
    try:
        # Create a safe filename
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename.lower().endswith('.pdf'):
            filename += ".pdf"
        
        # Remove invalid characters
        filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
        
        filepath = os.path.join(output_dir, filename)
        
        # Avoid overwriting
        if os.path.exists(filepath):
            print(f"File already exists: {filename}")
            return

        print(f"Downloading: {url} -> {filename}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Finished: {filename}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main():
    readme_path = 'README.md'
    output_dir = 'downloads'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Scanning {readme_path}...")
    urls = get_urls_from_markdown(readme_path)
    print(f"Found {len(urls)} unique URLs.")
    
    pdf_urls = [url for url in urls if is_pdf(url)]
    print(f"Found {len(pdf_urls)} PDF links.")
    
    for url in pdf_urls:
        download_pdf(url, output_dir)

if __name__ == "__main__":
    main()
