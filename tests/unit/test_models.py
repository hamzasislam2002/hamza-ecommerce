from project.models import Product, User 
from datetime import datetime
from freezegun import freeze_time

def test_new_product(new_product):
    
    assert new_product.name == 'Curry'
    assert new_product.price == 5.99
    assert new_product.user_id == 1
    assert new_product.purchase_date.year == 2024
    assert new_product.purchase_date.month == 1
    assert new_product.purchase_date.day == 12

def test_new_user(new_user):
    assert new_user.email == 'hamza@curry.com'
    assert new_user.password_hashed != 'Curry123'

def test_set_password(new_user):
    new_user.set_password('CurryCurry99')
    assert new_user.email == 'hamza@curry.com'
    assert new_user.password_hashed != 'CurryCurry99'
    assert new_user.is_password_correct('CurryCurry99')

def test_get_product_data_success(new_product, mock_requests_get_success_quote):
    new_product.get_product_data()
    assert new_product.name == 'Sunglasses'
    assert new_product.price == 19.99
    assert new_product.purchase_date.date() == datetime(2024, 1, 12).date()
    assert new_product.current_price == 19.99
    assert new_product.current_price_date.date() == datetime.now().date()
    assert new_product.position_value == (19.99)
    
def test_get_stock_data_api_rate_limit_exceeded(new_product, mock_requests_get_api_rate_limit_exceeded):
    new_product.get_product_data()
    assert new_product.name == 'Sunglasses'
    assert new_product.price == 19.99
    assert new_product.purchase_date.date() == datetime(2024, 1, 12).date()
    assert new_product.current_price == 0
    assert new_product.current_price_date is None
    assert new_product.position_value == 0

def test_get_product_data_failure(new_product, mock_requests_get_failure):
    new_product.get_product_data()
    assert new_product.name == 'Sunglasses'
    assert new_product.price == 19.99
    assert new_product.purchase_date.date() == datetime(2024, 1, 12).date()
    assert new_product.current_price == 0
    assert new_product.current_price_date is None
    assert new_product.position_value == 0

def test_get_product_data_success_two_calls(new_product, mock_requests_get_success_quote):
    assert new_product.name == 'Sunglasses'
    assert new_product.price == 19.99
    assert new_product.purchase_date.date() == datetime(2024, 1, 12).date()
    assert new_product.position_value == 0
    new_product.get_product_data()
    assert new_product.current_price == 19.99
    assert new_product.current_price_date.date() == datetime.now().date()
    assert new_product.position_value == (19.99)
    new_product.get_product_data()
    assert new_product.current_price == 19.99
    assert new_product.current_price_date.date() == datetime.now().date()
    assert new_product.position_value == (19.99)

@freeze_time('2025-01-13')
def test_get_timely_product_data_success(new_product, mock_requests_get_success_timely):
    title, labels, values = new_product.get_timely_product_data()
    assert labels[0].date() == datetime(2023, 12, 26)
    assert labels[1].date() == datetime(2023, 12, 19)
    assert labels[2].date() == datetime(2023, 12, 12)
    assert labels[0] == '19.99'
    assert values[1] == '19.99'
    assert values[2] == '19.99'
    assert datetime.now() == datetime(2025, 1, 14)

def test_get_timely_product_data_failure(new_product, mock_requests_get_failure):
    title, labels, values = new_product.get_timely_product_data()
    assert title == 'Product chart is unavailable'
    assert len(labels) == 0
    assert len(values) == 0