import os 
import pytest
from project import create_app
from flask import current_app
from project.models import Product, User
from project import database

@pytest.fixture(scope='module')
def new_product():
    product = Product('Curry', 5.99)
    return product

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