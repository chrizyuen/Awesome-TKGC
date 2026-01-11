import os
import re
import requests
import subprocess
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

def is_arxiv(url: str) -> bool:
    """Checks if a URL is an ArXiv link."""
    return 'arxiv.org' in url.lower()

def download_with_arxiv_dl(url: str, output_dir: str):
    """Downloads an ArXiv paper using arxiv-dl."""
    try:
        print(f"Downloading with arXiv-dl: {url}")
        # Identify if there's an ID in the URL
        # e.g., https://arxiv.org/abs/2305.10037 or https://arxiv.org/pdf/2305.10037.pdf
        match = re.search(r'(\d{4}\.\d{4,5})', url)
        if match:
            arxiv_id = match.group(1)
            # Try Windows style
            arxiv_dl_path = os.path.join('.venv', 'Scripts', 'arxiv-dl')
            if not os.path.exists(arxiv_dl_path):
                 # Try Mac/Linux style
                 arxiv_dl_path = os.path.join('.venv', 'bin', 'arxiv-dl')
            
            if not os.path.exists(arxiv_dl_path):
                 arxiv_dl_path = 'arxiv-dl' # Fallback to system path

            subprocess.run([arxiv_dl_path, arxiv_id, '-d', output_dir], check=True)
            print(f"Finished downloading ArXiv ID: {arxiv_id}")
        else:
            print(f"Could not extract ArXiv ID from URL: {url}")
    except Exception as e:
        print(f"Failed to download ArXiv paper {url}: {e}")

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

def find_all_readmes(root_dir: str) -> list[str]:
    """Scans for README.md files in all subdirectories."""
    readme_files = []
    for root, dirs, files in os.walk(root_dir):
        # Case insensitive check for README.md
        for file in files:
            if file.lower() == 'readme.md':
                readme_files.append(os.path.join(root, file))
    return readme_files

def main():
    root_dir = '.'
    output_dir = 'downloads'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Scanning for README.md files in '{root_dir}'...")
    readme_files = find_all_readmes(root_dir)
    print(f"Found {len(readme_files)} README files.")
    
    all_urls = set()
    for readme_path in readme_files:
        print(f"Processing {readme_path}...")
        urls = get_urls_from_markdown(readme_path)
        all_urls.update(urls)
        
    print(f"Found {len(all_urls)} unique URLs across all READMEs.")
    
    for url in all_urls:
        if is_arxiv(url):
            download_with_arxiv_dl(url, output_dir)
        elif is_pdf(url):
            download_pdf(url, output_dir)

if __name__ == "__main__":
    main()
