from project import database
from sqlalchemy import Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
import flask_login
from datetime import datetime, timedelta
from flask import current_app
import requests

def create_alpha_vantage_get_url_timely(symbol: str) -> str:
    return 'https://www.alphavantage.co/query?function={}&symbol={}&apikey={}'.format(
        'TIME_SERIES_WEEKLY_ADJUSTED',
        symbol,
        current_app.config['ALPHA_VANTAGE_API_KEY']
    )

def create_alpha_vantage_url_quote(symbol: str) -> str:
    return 'https://www.alphavantage.co/query?function={}&symbol={}&apikey={}'.format(
        'GLOBAL_QUOTE',
        symbol,
        current_app.config['ALPHA_VANTAGE_API_KEY']
    )

def get_current_product_price(symbol: str) -> float:
    url = create_alpha_vantage_url_quote(symbol)
    
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        current_app.logger.error(
            f'Error! Network problem preventing retrieving product data ({symbol})!')
        
    if r.status_code != 200:
        current_app.logger.warning(f'Error! Received unexpected status code ({r.status_code}) '
                                   f'when retrieving daily product data ({symbol})!')
        return 0.0

    product_data = r.json()

    if 'Global Quote' not in product_data:
        current_app.logger.warning(f'Could not find the Global Quote key when retrieving '
                                   f'the daily product data ({symbol})!')
        return 0.0

    return float(product_data['Global Quote']['02. price'])

class Product(database.Model):

    __tablename__ = 'products'

    id = mapped_column(Integer(), primary_key=True)
    name = mapped_column(String(100))
    price = mapped_column(Float)
    user_id = mapped_column(ForeignKey('users.id'))
    purchase_date = mapped_column(DateTime())
    current_price = mapped_column(Integer())
    current_price_date = mapped_column(DateTime())
    position_value = mapped_column(Integer())

    user_relationship = relationship('User', back_populates='product_relationship')

    def __init__(self, name: str, price: float, user_id: int, purchase_date = None):
        self.name = name
        self.price = price
        self.user_id = user_id
        self.purchase_date = purchase_date
        self.current_price = 0
        self.current_price_date = None
        self.position_value = 0

    def __repr__(self):
        return f'{self.name} - {self.price}.'
    
    def get_product_data(self):
        if self.current_price_date is None or self.current_price_date.date() != datetime.now().date():
            current_price = get_current_product_price(self.name)
            if current_price > 0.0:
                self.current_price = int(current_price * 100)
                self.current_price_date = datetime.now()
                self.position_value = self.current_price
                current_app.logger.debug(f'Retrieved current price {self.current_price / 100} '
                                     f'for the product data ({self.name})!')
    
    def get_product_position_value(self) -> float:
        return float(self.position_value / 100)
    
    def get_timely_product_data(self):
        title = 'Stock chart is unavailable.'
        labels = []
        values = []
        url = create_alpha_vantage_get_url_timely(self.name)
        
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            current_app.logger.info(
                f'Error! Network problem preventing retrieving the product data ({self.name})!')
            
        if r.status_code != 200:
            current_app.logger.warning(f'Error! Received unexpected status code ({r.status_code}) '
                                   f'when retrieving product data ({self.name})!')
            return title, '', ''
        
        timely_data = r.json()

        if 'Weekly Adjusted Time Series' not in timely_data:
            current_app.logger.warning(f'Could not find the Weekly Adjusted Time Series key when retrieving '
                                    f'product data ({self.name})!')
            return title, '', ''

        title = f'Prices ({self.name})'

        start_date = self.purchase_date
        if (datetime.now() - self.purchase_date) < timedelta(weeks=12):
            start_date = datetime.now() - timedelta(weeks=12)

        for element in timely_data['Time Series']:
            date = datetime.fromisoformat(element)
            if date.date() > start_date.date():
                labels.append(date)
                values.append(timely_data['Time Series'][element]['3. date'])

    
        labels.reverse()
        values.reverse()

        return title, labels, values














    
class User(flask_login.UserMixin, database.Model):

    __tablename__ = 'users'

    id = mapped_column(Integer(), primary_key=True)
    email = mapped_column(String(), unique=True)
    password_hashed = mapped_column(String(256))
    registered_on = mapped_column(DateTime())
    email_confirmation_sent_on = mapped_column(DateTime())
    email_confirmed = mapped_column(Boolean(), default=False)
    email_confirmed_on = mapped_column(DateTime())

    product_relationship = relationship('Product', back_populates='user_relationship')

    def __init__(self, email: str, password_plaintext: str):
        self.email = email
        self.password_hashed = self._generate_password_hash(password_plaintext)
        self.registered_on = datetime.now()
        self.email_confirmation_sent_on = datetime.now()
        self.email_confirmed = False
        self.email_confirmed_on = None

    def set_password(self, password_plaintext: str):
        self.password_hashed = self._generate_password_hash(password_plaintext)

    def is_password_correct(self, passsword_plaintext: str):
        return check_password_hash(self.password_hashed, passsword_plaintext)
    
    @staticmethod
    def _generate_password_hash(password_plaintext):
        return generate_password_hash(password_plaintext)
    
    def __repr__(self):
        return f'<User: {self.email}>'