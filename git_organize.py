import os
import subprocess
import shutil
import re

def get_repo_author(repo_path):
    """
    Extracts the author/organization name from the git remote origin URL.
    """
    try:
        # Get the remote origin URL
        result = subprocess.run(
            ["git", "-C", repo_path, "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True
        )
        url = result.stdout.strip()
        
        # Parse URL to extract author
        # Supports:
        # https://github.com/Author/Repo.git
        # git@github.com:Author/Repo.git
        
        # Regex for standard GitHub structure (and similar)
        # Matches content between 'github.com/' or 'github.com:' and the next '/'
        match = re.search(r'github\.com[:/]([^/]+)/', url)
        if match:
            return match.group(1)
            
    except subprocess.CalledProcessError:
        # Not a git repo or no remote named origin
        pass
    except Exception as e:
        print(f"Error processing {repo_path}: {e}")
        
    return None

def organize_repos():
    # Get current working directory
    current_dir = os.getcwd()
    print(f"Scanning directories in {current_dir}...")

    # List all items in the current directory
    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)
        
        # Skip if not a directory
        if not os.path.isdir(item_path):
            continue
            
        # Check if it's a git repository
        if not os.path.exists(os.path.join(item_path, ".git")):
            continue
            
        # Get author
        author = get_repo_author(item_path)
        
        if author:
            # Skip if the directory name matches the author (already organized or is the author folder)
            if item == author:
                continue
                
            author_dir = os.path.join(current_dir, author)
            
            # Create author directory if it doesn't exist
            if not os.path.exists(author_dir):
                print(f"Creating directory: {author}")
                os.makedirs(author_dir)
            
            # Determine destination path
            destination = os.path.join(author_dir, item)
            
            # Move the repo
            if not os.path.exists(destination):
                print(f"Moving {item} to {author}/{item}")
                try:
                    shutil.move(item_path, destination)
                except Exception as e:
                    print(f"Failed to move {item}: {e}")
            else:
                print(f"Skipping {item}: Destination {destination} already exists.")

if __name__ == "__main__":
    organize_repos()
