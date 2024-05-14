import requests

def get_golang_repos(project_key, bitbucket_user, bitbucket_pass):
    url = f"https://bitbucket.wtfast.net/rest/api/1.0/projects/{project_key}/repos"
    repos = []
    start = 0
    limit = 300
    
    try:
        while True:
            params = {'start': start, 'limit': limit}
            response = requests.get(url, params=params, auth=(bitbucket_user, bitbucket_pass))
            response.raise_for_status()
            data = response.json()
            
            for repo in data['values']:
                repo_name = repo['slug']
                repo_url = f"bitbucket.wtfast.net/projects/{project_key}/repos/{repo_name}"
                repos.append(repo_url)
            
            is_last_page = data['isLastPage']
            if is_last_page:
                break
            else:
                start += limit
        
        return repos
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# 呼叫函數並取得 Golang projects 中的 repo 名稱
project_key = 'XRDCHK'
bitbucket_user = 'jackie'
bitbucket_pass = ''

repo_urls = get_golang_repos(project_key, bitbucket_user, bitbucket_pass)
for url in repo_urls:
    print(url)


# TED TEST TT TRAIN WBP WIN XRDCHK