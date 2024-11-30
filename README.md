# faz-bot-app-collect

faz-bot app for Wynncraft data collection

## Table of Contents

- [Installation](#installation)
    - [Requirements](#requirements)
    - [Steps](#steps)
- [Usage](#usage)
- [Notes and Tips](#notes-and-tips)
- [Bug Reports and Feature Requests](#bug-reports-and-feature-requests)
- [License](#license)

## Installation

> [!NOTE]
> - The database installation step only needs to be completed once, even if you are using multiple faz-bot components.
> - This manual is made for Linux. Might require more steps if you are running Windows.

### Requirements

- git: [git-scm.com](https://git-scm.com/downloads)
- uv: [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)
- MySQL (non-docker): [mysql.com](https://dev.mysql.com/downloads/mysql/)
- Docker (docker): [docker.com](https://www.docker.com/)

### Steps

1. Clone this repository

```sh
git clone https://github.com/FAZuH/faz-bot-app-collect
```

Change directory into the repository with `cd faz-bot-app-collect`.

2. Set environment variables

Copy with `cp .env-example .env`, and fill the placeholders in `.env`.

3. Initialize the database
    
    **Non-docker**
   - Download and install MySQL. Make sure your MySQL server is up and running.
   - Do `export MYSQL_FAZCORD_DATABASE=faz-cord` (temporary) and run `uv run faz-initdb` to initialize the database.
   
    **Docker**
   - Run `docker compose up --detach mysql` to pull a mariadb docker image, and run a container from it. This should also create a "mysql" volume and "faz-bot-network" network for the docker containers.
   - Do `export MYSQL_FAZCORD_DATABASE=faz-cord` (temporary) and run `uv run faz-initdb` to initialize the database.

## Usage

**Non-docker** Run the app with `uv run faz-bot-collect`.

**Docker** Run the app with `docker compose up --detach faz-bot-app-discord`

## Notes and Tips

- Application logs are stored on `logs` directory, in the root of the repository.
- If you are using docker, you can find where docker is storing your mysql volume data with `docker inspect volume mysql`.

## Bug Reports and Feature Requests

You can report bug or request for features on the [issue tracker](https://github.com/FAZuH/faz-bot-app-collect/issues).

## License

`faz-bot-app-collect` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
