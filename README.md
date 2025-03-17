<div align="center">
<p>
  <img src="images/logo.png" alt="Logo FaktaIklim">
</p>
</div>

## Table of Contents

- [About the Project](#about-the-project)
  - [Built With](#built-with)
- [Installation](#installation)
- [Running the app](#running-the-app)

## About The Project

<b>FaktaIklim</b> is a web application to verify information and trace hoax news related to climate.<br>
This is the back-end part of FaktaIklim application.<br>

### Built With

* [Python](https://www.python.org)
* [FastAPI](https://fastapi.tiangolo.com)
* [PostgreSQL](https://www.postgresql.org)

## Installation

1. Clone the repository
   ```sh
   $ git clone https://gitlab.prosa.ai/prosa-ai/platform/fair-forward-backend.git
   ```
2. Change active directory to the project folder
   ```sh
   $ cd fair-forward-frontend
   ```
3. Install required dependencies
   ```sh
   $ pip install -r requirements.txt
   ```
4. Edit database configuration file located in `api/database.py`.
5. Edit configuration file located in `api/config.py`.

## Running the app

To run the application:
1. Run PostgreSQL as database server
2. Run Uvicorn
    ```sh
    $ uvicorn main:app
    ```
