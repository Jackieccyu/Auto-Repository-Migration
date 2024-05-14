import requests
import csv
import json
import subprocess
import os

# Bitbucket credentials
bitbucket_user = "jackie"
bitbucket_pass = ""

# GitHub credentials
github_user = 'Jackieccyu'
github_access_token = ''
github_org = ''

# Function to get Bitbucket project keys
def get_bitbucket_project_keys():
    url = "https://bitbucket.wtfast.net/rest/api/1.0/projects"
    params = {
        "limit": 100,
        "start": 0
    }
    project_keys = []
    while True:
        response = requests.get(url, auth=(bitbucket_user, bitbucket_pass), params=params)
        if response.status_code == 200:
            data = response.json()
            for project in data.get("values", []):
                project_key = project.get("key")
                if project_key:
                    project_keys.append(project_key)
            if not data.get("isLastPage", True):
                params["start"] += params["limit"]
            else:
                break
        else:
            print("Failed to get projects from Bitbucket Server")
            break
    return project_keys

# Function to get Bitbucket repositories for a project
def get_bitbucket_repos(project_key):
    url = f"https://bitbucket.wtfast.net/rest/api/1.0/projects/{project_key}/repos"
    repo_list = []
    start = 0
    limit = 100
    while True:
        params = {
            "start": start,
            "limit": limit
        }
        response = requests.get(url, auth=(bitbucket_user, bitbucket_pass), params=params)
        if response.status_code == 200:
            data = response.json()
            repos = data.get("values", [])
            for repo in repos:
                repo_name = repo.get("name")
                clone_url = repo.get("links", {}).get("clone", [{}])[0].get("href")
                if repo_name and clone_url:
                    repo_info = {"name": repo_name, "clone_url": clone_url}
                    repo_list.append(repo_info)
            start += limit
            if not data.get("isLastPage", True):
                continue
            else:
                break
        else:
            print(f"Failed to get repositories for project '{project_key}'")
            break
    return repo_list

# Get Bitbucket project keys
project_keys = get_bitbucket_project_keys()
total_repo_count = 0


# Iterate over Bitbucket projects and repositories
for project_key in project_keys:
    repos = get_bitbucket_repos(project_key)
    if repos:
        repo_count = len(repos)
        total_repo_count += repo_count
        print(f"Repositories for project '{project_key}': {repo_count}")
        for repo in repos:
            print(f"Repo Name: {repo['name']}, Clone URL: {repo['clone_url']}")
        print()  # Output an empty line as a separator between projects

print(f"Total repositories: {total_repo_count}")



# Function to read a CSV file
def read_csv_file(filename):
    data = []
    try:
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    return data

# Call the function to read the CSV file
csv_filename = "bitbucket migration.csv"
csv_data = read_csv_file(csv_filename)

# Print the data
for row in csv_data:
    print(row)


# Convert the data in the CSV file to a dictionary
csv_dict = {row[1].replace("-", "").lower(): row for row in csv_data}

# Search the CSV dictionary for a matching repository name
def search_csv_dict(repo_name):
    repo_name = repo_name.lower()
    matching_rows = []
    for key, value in csv_dict.items():
        if value[1].lower() == repo_name or value[0].rsplit("/", 1)[-1].lower() == repo_name:
            matching_rows.append(value)
    return matching_rows

# Create the GitHub repository name
def create_github_name(matching_row):
    github_name = matching_row[1]
    return github_name

# Get the GitHub origin (clone URL) based on the project key and repository name
def get_github_origin(project_key, repo_name):
    # Implement the logic to retrieve the GitHub clone URL based on the repository name and project key
    # You can use the GitHub API or any other method to fetch the clone URL
    # For now, let's assume the clone URL is a placeholder value
    github_clone_url = f"https://github.com/{github_org}/{repo_name}.git"
    return github_clone_url

# Create a GitHub repository
def create_github_repo(repo_name):
    api_url = f"https://api.github.com/orgs/{github_org}/repos"
    r = requests.post(api_url, data=json.dumps({
        "name": repo_name,
        "private": True,
        'has_issues': True,
        'has_projects': False,
        'has_wiki': False,
        'allow_merge_commit': True,
        'allow_rebase_merge': True,
    }), headers={
        'User-Agent': 'jackie@wtfast.com',
        'Content-Type': 'application/json'
    }, auth=(github_user, github_access_token))

    if r.status_code >= 200 and r.status_code < 300:
        return True
    return False

# Archive a GitHub repository
def archive_github_repo(repo_name):
    api_url = f"https://api.github.com/repos/{github_org}/{repo_name}"
    r = requests.patch(api_url, data=json.dumps({
        "name": repo_name,
        "archived": True,
    }), headers={
        'User-Agent': 'jackie@wtfast.com',
        'Content-Type': 'application/json'
    }, auth=(github_user, github_access_token))
    print(r.url)

    if r.status_code >= 200 and r.status_code < 300:
        return True
    return False

# Create a directory
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)   

# Clone a repository
def clone(bitbucket_origin, path):
    process = subprocess.Popen(
        ["git", "clone", "--mirror", bitbucket_origin, path], stdout=subprocess.PIPE)
    process.communicate()[0]

# Convert large files to LFS format
# def lfs(path):
#     conf = []
#     process = subprocess.Popen(
#         ["git", "lfs", "migrate", "info", "--above=100MB"], stdout=subprocess.PIPE, cwd=path)
#     for line in iter(process.stdout.readline, b''):
#         parts = line.split()
#         if len(parts) > 0:
#             conf.append(parts[0])
#     process.communicate()
#     while len(conf) > 0:
#         file_path = conf.pop()
#         process = subprocess.Popen(
#             ["git", "lfs", "migrate", "import", f'--include="{file_path}"'], stdout=subprocess.PIPE, cwd=path)
#         process.communicate()


# Push the repository to GitHub
def push(github_origin, path):
    process = subprocess.Popen(["git", "push", "--mirror", github_origin], stdout=subprocess.PIPE, cwd=path)
    process.communicate()

# Get Bitbucket project keys
project_keys = get_bitbucket_project_keys()
total_repo_count = 0

# Iterate over Bitbucket projects and repositories
for project_key in project_keys:
    repos = get_bitbucket_repos(project_key)
    if repos:
        for repo in repos:
            repo_name = repo["name"].lower()
            matching_rows = search_csv_dict(repo_name)
            if matching_rows:
                for matching_row in matching_rows:
                    print(f"Match found: {repo_name} - {matching_row} {repo['clone_url']}")
                github_name = create_github_name(matching_rows[0])
                print(f"GitHub Name: {github_name}")
                github_origin = get_github_origin(project_key, github_name)
                print(f"GitHub Clone URL: {github_origin}")
                print(f"Clone URL: {repo['clone_url']}")
                # Create GitHub repository
                if create_github_repo(github_name):
                    print(f"GitHub repository '{github_name}' created successfully")
                    #Create folder
                    repo_directory = os.path.join("/Users/jackieyu/Desktop/Automigration/repos", github_name)
                    create_directory(repo_directory)
                    print(f"Match found: {repo_name} - {matching_row} {repo['clone_url']}")
                    # Clone the repository
                    print(f"Cloning repository '{github_name}' from {repo['clone_url']}")
                    clone(repo['clone_url'], repo_directory)
                    print(f"Repository '{github_name}' cloned successfully")
                    # # Convert large files to LFS format
                    # print(f"Converting large files to LFS format in '{github_name}'")
                    # lfs(repo_directory)
                    # print(f"Large files converted to LFS format successfully")
                    # Push repository to GitHub
                    print(f"Pushing repository '{github_name}' to GitHub")
                    push(github_origin, repo_directory)
                    print(f"Repository '{github_name}' pushed to GitHub successfully")
                else:
                    print(f"Failed to create GitHub repository '{github_name}'")
                print()
                total_repo_count += 1

print(f"Total Created repositories: {total_repo_count}")
