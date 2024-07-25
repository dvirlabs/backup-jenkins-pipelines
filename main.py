import os
import requests
from github import Github

# Environment variables for Jenkins and GitHub credentials
JENKINS_URL = os.getenv('JENKINS_URL')
JENKINS_USER = os.getenv('JENKINS_USER')
JENKINS_TOKEN = os.getenv('JENKINS_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')

def get_jenkins_pipelines():
    """Fetch Jenkins pipelines using the Jenkins API."""
    response = requests.get(f"{JENKINS_URL}/api/json", auth=(JENKINS_USER, JENKINS_TOKEN))
    response.raise_for_status()
    jobs = response.json().get('jobs', [])
    
    pipelines = {}
    for job in jobs:
        job_name = job['name']
        config_url = f"{JENKINS_URL}/job/{job_name}/config.xml"
        config_response = requests.get(config_url, auth=(JENKINS_USER, JENKINS_TOKEN))
        config_response.raise_for_status()
        pipelines[job_name] = config_response.text
    
    return pipelines

def backup_to_github(pipelines):
    """Backup Jenkins pipelines to GitHub."""
    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(GITHUB_REPO)
    
    for job_name, config in pipelines.items():
        file_path = f"jenkins_pipelines/{job_name}/config.xml"
        try:
            contents = repo.get_contents(file_path)
            repo.update_file(contents.path, f"Update {job_name} pipeline", config, contents.sha)
        except:
            repo.create_file(file_path, f"Add {job_name} pipeline", config)

def main():
    pipelines = get_jenkins_pipelines()
    backup_to_github(pipelines)
    print("Backup complete.")

if __name__ == "__main__":
    main()
