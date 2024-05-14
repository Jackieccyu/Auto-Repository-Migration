import requests
import csv
import json
import subprocess
import os

# Bitbucket credentials
bitbucket_user = ""
bitbucket_pass = ""

# GitHub credentials
github_user = ''
github_access_token = ''
github_org = ''


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
def search_csv_dict(repo_name, project_keys):
    repo_name = repo_name.lower()
    matching_rows = []
    for key, value in csv_dict.items():
        if key in project_keys:  # 添加对 project_keys 的条件检查
            if value[1].lower() == repo_name or value[0].rsplit("/", 1)[-1].lower() == repo_name or value[0]:
                matching_rows.append(value)
    return matching_rows


# Iterate over Bitbucket projects and repositories
for project_key in project_keys:
    repos = get_bitbucket_repos(project_key)
    if repos:
        for repo in repos:
            repo_name = repo["name"].lower()
            matching_rows = search_csv_dict(repo_name, project_keys)
            if matching_rows:
                for matching_row in matching_rows:
                    print(f"Match found: {repo_name} - {matching_row} {repo['clone_url']}")