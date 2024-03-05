# gh-archivist

A lazy attempt (thanks ChatGPT) at a late night to clone/mirror a Github user/organization's repositories as well as download all artifacts for all published tags - if they exist/are available.

This tool will only clone the repos and the artifacts to your local machine.
This won't publish any repositories to your account or make anything beyond that.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **GitHub CLI**: This project requires the [GitHub CLI](https://cli.github.com/) tool (`gh`) to be installed on your machine. The GitHub CLI is used for interacting with GitHub from the command line, and this project uses it to automate interactions with GitHub repositories and releases.

- **Logged in to GitHub via GitHub CLI**: You must be logged in (actually, you might not need that - but if it fails/rates limit you, then do) to your GitHub account through the GitHub CLI to use the features of this project. This authentication allows the scripts to interact with *your* GitHub repositories (or private repos you might have access to).

## Getting Started

To get started with this project, you first need to ensure the GitHub CLI is installed and that you are authenticated (unless only mirroring from public repositories). Follow the steps below to set up everything:

### Installing GitHub CLI

The GitHub CLI can be installed on macOS, Windows, and Linux. Please refer to the [official installation guide](https://cli.github.com/manual/installation) for detailed instructions for your operating system.

### Logging in to GitHub

Once the GitHub CLI is installed, you need to log in to your GitHub account using the CLI. Open your terminal or command prompt and run the following command:

```sh
gh auth login
```

Follow the prompts to authenticate. You'll be asked to choose a GitHub instance, provide your credentials, and select your preferred protocol for Git operations. For more details on the authentication process, check the official gh auth login documentation.

### Usage

```
python run.py "C:\path\to\your\desired\folder" username
```

### Contributing

Contributions to this project are welcome. Please follow the standard fork and pull request workflow.
License

### License

This project is licensed under the BSD 3-Clause Clear License. For more details, see the [LICENSE](LICENSE) file in this repository.