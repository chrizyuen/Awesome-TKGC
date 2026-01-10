import requests
import os
import subprocess

def clone_all_public_repos(username):
    page = 1
    while True:
        # 1. Define the API endpoint for the user's repos with pagination
        api_url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=100"
        
        try:
            # 2. Fetch the list of repositories
            response = requests.get(api_url)
            response.raise_for_status()
            repos = response.json()

            if not repos:
                if page == 1:
                    print(f"No public repositories found for user: {username}")
                break

            # 3. Create a directory for the user's repos (only on first page)
            if page == 1:
                if not os.path.exists(username):
                    os.makedirs(username)
                
                os.chdir(username)

            # 4. Loop through and clone each repo
            for repo in repos:
                repo_name = repo['name']
                clone_url = repo['clone_url']
                
                lower_repo_name = repo_name.lower()
                if lower_repo_name.startswith("awesome-"):
                    print(f"Cloning {repo_name}...")
                    # Use subprocess to run the git command
                    subprocess.run(["git", "clone", clone_url])
            
            page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from GitHub: {e}")
            break

    print(f"\nFinished! All public repos for {username} are in the '{username}' folder.")



if __name__ == "__main__":
    target_user = input("Enter the GitHub username: ")
    clone_all_public_repos(target_user)