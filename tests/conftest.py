import os 
import pytest
from project import create_app
from flask import current_app
from project.models import Product, User
from project import database
from datetime import datetime
import requests

class MockSuccessResponseQuote(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url

        def json(self):
            return {
                "Global Quote": {
                "01. product": "Bicycle",
                "02. price": "74.99",
                "03. date": "2024-01-12"
                }
            }

class MockApiRateLimitExceededResponse(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url

    def json(self):
        return {
            'Note': 'Thank You'
        }
    
class MockFailedResponse(object):
    def __init__(self, url):
        self.status_code = 404
        self.url = url

        def json(self):
            return {'error': 'bad'}
        
class MockSuccessResponseTimely(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url

    def json(self):
        return {
            'Meta Data': {
                "1. Product": "Sunglasses" ,
                "2. Last Refreshed": "2024-01-10"
            },
            'Adjusted Time Prices': {
                "2023-01-03": {
                    "3. close": "19.99"
                },
                "2023-12-26": {
                    "3. close": "19.99"
                },
                "2023-12-19": {
                    "3. close": "19.99"
                },
                "2023-12-12": {
                    "3. close": "19.99"
                }
            }
        }


@pytest.fixture(scope='function')
def mock_requests_get_success_timely(monkeypatch):
    def test_get(url):
        return MockSuccessResponseTimely(url)
    
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', test_get)

@pytest.fixture(scope='module')
def new_product():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    flask_app.extensions['mail'].suppress = True

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            product = Product('Curry', 5.99, 1, datetime(2024, 1, 12))
            yield product

@pytest.fixture(scope='module')
def test_client():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    flask_app.extensions['mail'].suppress = True

    # testing_client = flask_app.test_client()

    # ctx = flask_app.app_context()
    # ctx.push()

    # current_app.logger.info('In the test_client() fixture...')

    # ctx.pop()

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            current_app.logger.info('In the test_client() fixture...')

            # database.create_all()


        yield testing_client

        # with flask_app.app_context():
        #     database.drop_all()

@pytest.fixture(scope='module')
def new_user():
    user = User('hamza@curry.com', 'Curry123')
    return user

@pytest.fixture(scope='module')
def register_default_user(test_client):
    test_client.post('/users/register',
                     data={'email': 'hamza@curry.com',
                           'password': 'Curry123'},
                      follow_redirects=True)
    
    yield

    test_client.get('/users/logout', follow_redirects=True)

@pytest.fixture(scope='function')
def email_default_user(test_client, log_in_default_user):
    query = database.select(User).where(User.email == 'hamza@curry.com')
    user = database.session.execute(query).scalar_one_or_none()
    user.email_confirmed = True
    # user.email_confirmed_on = datetime(2020, 7, 8)
    database.session.add(user)
    database.session.commit()

    yield user

    query = database.select(User).where(User.email == 'hamza@curry.com')
    user = database.session.execute(query).scalar_one_or_none()
    user.email_confirmed = False
    user.email_confirmed_on = None
    database.session.add(user)
    database.session.commit()

@pytest.fixture(scope='function')
def after_reset_default_user_password():
    query = database.select(User).where(User.email == 'hamza@curry.com')
    user = database.session.execute(query).scalar_one()
    user.set_password('hehe123')
    database.session.add(user)
    database.session.commit()

@pytest.fixture(scope='function')
def add_products_for_default_user(test_client, log_in_default_user):
    test_client.post('/add_products', data={'nameproduct': 'Curry',
                                            'priceproduct': '5.99',
                                            'purchasedate': '2024-01-12'})
    test_client.post('/add_products', data={'nameproduct': 'Sunglasses',
                                            'priceproduct': '19.99',
                                            'purchasedate': '2024-01-12'})
    test_client.post('/add_products', data={'nameproduct': 'Bicycle',
                                            'priceproduct': '19.99',
                                            'purchasedate': '2024-01-12'})
    return

@pytest.fixture(scope='function')
def mock_requests_get_success_quote(monkeypatch):
    # Create a mock for the requests.get() call to prevent making the actual API call
    def test_get(url):
        return MockSuccessResponseQuote(url)

    url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', test_get)

@pytest.fixture(scope='function')
def mock_requests_get_api_rate_limit_exceeded(monkeypatch):
    def test_get(url):
        return MockApiRateLimitExceededResponse(url)

    url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', test_get)

@pytest.fixture(scope='function')
def mock_requests_get_failure(monkeypatch):
    def test_get(url):
        return MockFailedResponse(url)

    url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', test_get)

@pytest.fixture(scope='module')
def register_second_user(test_client):
    test_client.post('/users/register',
                     data={'email': 'hamza@chicken.com',
                           'password': 'chicken123'})


@pytest.fixture(scope='function')
def log_in_second_user(test_client, register_second_user):
    test_client.post('/users/login',
                     data={'email': 'hamza@chicken.com',
                           'password': 'chicken123'})

    yield

    test_client.get('/users/logout', follow_redirects=True)