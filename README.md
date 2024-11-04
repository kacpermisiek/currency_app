# currency_app

This is a simple app built with FastAPI for managing orders in a small online shop.  
This application supports:
* Creating orders and saving them to a database
* Updating the order status
* Fetching Currency exchange rates from an external API

It uses the PostgresSQL database to store the orders.


## External API
This application uses the [NBP-API](https://api.nbp.pl/en.html) to fetch the currency exchange rates.

## Installation
To install the application, you need to have Python 3.10 or higher and poetry installed on your machine.

1. Clone the repository
2. Install the dependencies by running `poetry install`
3. Create docker container with PostgresSQL by running `docker-compose up db -d`
4. Run the application by running `poetry run uvicorn currency_app.api.main:app --reload`
5. The application should be available at `http://localhost:8000/api`

## Run tests
To run the tests, you need to have the database running.
1. Run the tests by running `pytest`

### Documentation is available at `http://localhost:8000`
