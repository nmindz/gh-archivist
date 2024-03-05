import subprocess
import os
import json
import sys
import contextlib
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path

global PROJECT_DIR
PROJECT_DIR = os.getcwd()

@contextlib.contextmanager
def temporary_change_dir(new_directory):
    """Temporarily change the working directory."""
    original_directory = os.getcwd()
    try:
        os.chdir(new_directory)
        yield
    finally:
        os.chdir(original_directory)


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
    file_handler = RotatingFileHandler(log_filename, maxBytes=10485760, backupCount=5)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)


setup_logging()

def run_command(command, parse_json=False):
    logging.debug(f"Executing command: {command}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    if result.returncode != 0:
        logging.error(f"Error executing command: {command}\nError: {result.stderr}")
        return None
    if parse_json:
        try:
            if result.stdout.strip() == "":
                logging.warning(f"No JSON output returned by command: {command}\nStandard Error Output: {result.stderr}")
                return None
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON output from command: {command}\nOutput: {result.stdout}\nError: {e}")
            return None
    else:
        return result.stdout.strip()


def clone_repos(prefix, username):
    repo_path = os.path.join(prefix, username)
    os.makedirs(repo_path, exist_ok=True)
    logging.info(f"Cloning repositories into {repo_path}")
    repos = run_command(f"gh repo list {username} --limit 100 --json url", parse_json=True)
    for repo in repos:
        repo_url = repo['url']
        repo_name = repo_url.split('/')[-1]  # Extract the repository name from the URL
        local_repo_path = os.path.join(repo_path, repo_name)
        if os.path.exists(local_repo_path):
            logging.info(f"Repository {repo_name} already exists, skipping clone.")
            continue
        logging.info(f"Cloning {repo_url}")
        run_command(f"git clone {repo_url}.git {local_repo_path}")


def list_releases_and_parse(owner, repo_name):
    cwd = os.getcwd()
    logging.debug(f"Project dir: {PROJECT_DIR}")
    logging.debug(f"Current working dir: {cwd}")
    command = f"gh release list --repo {owner}/{repo_name} --limit 100"
    parse_command = f"python {PROJECT_DIR}/parse_releases.py"
    process1 = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    process2 = subprocess.Popen(parse_command, stdin=process1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    output, error = process2.communicate()
    output1, error1 = process1.communicate()
    if process1.returncode != 0 or process2.returncode != 0:
        logging.error(f"Error listing releases for {owner}/{repo_name}\n{error}")
        logging.debug(f"Github CLI output: \n{output1}")
        logging.debug(f"CLI Parse output: \n{output}")
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON output for releases of {owner}/{repo_name}: {e}")
        return None


def process_repositories(prefix, username):
    base_path = os.path.join(prefix, username)
    if not os.path.exists(base_path):
        logging.error(f"The path specified does not exist: {base_path}")
        sys.exit(1)

    for repo_dir in os.listdir(base_path):
        repo_path = os.path.join(base_path, repo_dir)
        if os.path.isdir(repo_path) and os.path.exists(os.path.join(repo_path, '.git')):
            logging.info(f"Processing repository: {repo_dir}")
            download_assets_for_repo(repo_path)
        else:
            logging.info(f"Skipping non-repository folder: {repo_dir}")


def download_assets_for_repo(repo_path):
    # Ensure the .git directory exists to confirm it's a valid git repository
    git_dir_path = os.path.join(repo_path, '.git')
    if not os.path.exists(git_dir_path):
        logging.info(f"Skipping non-repository folder: {repo_path}")
        return

    with temporary_change_dir(repo_path):
        try:
            with open('.git/config', 'r') as git_config:
                config_lines = git_config.readlines()
            remote_origin_url = None
            for line in config_lines:
                if 'url = ' in line:
                    remote_origin_url = line.split('=')[1].strip()
                    break
            if remote_origin_url is None:
                logging.error("Remote origin URL not found in .git/config")
                return

            # Parse the URL to extract the owner and repo name
            if remote_origin_url.startswith("https"):
                owner_repo = remote_origin_url.split('/')[-2:]
            else:  # SSH format
                owner_repo = remote_origin_url.split(':')[-1].split('/')
            owner, repo_name = owner_repo[0], owner_repo[1].replace('.git', '')

            logging.info(f"Processing releases for {owner}/{repo_name}")
            command = f'gh api --paginate -H "Accept: application/vnd.github.v3+json" repos/{owner}/{repo_name}/releases'
            releases = run_command(command, parse_json=True)
            if releases is None:
                logging.error("Failed to list releases or no releases found.")
                return

            for release in releases:
                tag = release['tag_name']
                cwd = os.getcwd()
                # logging.debug(f"Current working dir: {cwd}")
                assets_dir = os.path.join(Path(cwd).parent, "_assets", repo_name, tag)
                logging.info(f"Downloading assets for {tag} to {assets_dir}")
                os.makedirs(assets_dir, exist_ok=True)
                run_command(f'gh release download "{tag}" --repo "{owner}/{repo_name}" --dir "{assets_dir}" --pattern "*"')

        except Exception as e:
            logging.error(f"Error processing repository: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logging.error("Usage: python script.py <PREFIX> <USERNAME>")
        sys.exit(1)
    prefix, username = sys.argv[1], sys.argv[2]
    logging.info(f"Starting script for user/organization: {username} with prefix: {prefix}")
    clone_repos(prefix, username)
    process_repositories(prefix, username)
    logging.info("Script completed successfully.")
