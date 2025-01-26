import requests

class MockSuccessResponse(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url
        self.headers = {'hello': '6789'}

    def json(self):
        return {
            "Global Quote": {
                "01. product": "Sunglasses",
                "02. price": "19.99",
                "03. date": "2024-01-12"
            }
        }
    
class MockFailedResponse(object):
    def __init__(self, url):
        self.status_code = 404
        self.url = url
        self.headers = {'hello': '6789'}

    def json(self):
        return {'error': 'bad'}


def test_index_page(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'Welcome to' in response.data 

def test_get_product(test_client, add_products_for_default_user, mock_requests_get_success_quote):
    response = test_client.get('/add_product')
    assert response.status_code == 200
    assert b'For reference, refer to the list' in response.data
    assert b'Product Name' in response.data
    assert b'Price' in response.data
    assert b'Quantity' in response.data
    assert b'Purchase Date' in response.data

def test_get_add_product_not_logged_in(test_client):
    response = test_client.get('/add_product', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page.' in response.data

def test_post_product(test_client, log_in_default_user, mock_requests_get_success_quote):
    response = test_client.post('/add_product',
                                data={'nameproduct': 'Headphones',
                                      'priceproduct': '49.99',
                                      'quantityproduct': '5',
                                      'purchase_date': '2024-01-12'},
                                      follow_redirects=True)
    assert response.status_code == 200
    assert b'Headphones' in response.data
    assert b'49.99' in response.data
    assert b'5' in response.data
    assert b'Added new product!' in response.data

def test_post_add_product_not_logged_in(test_client):
    response = test_client.post('/add_product',
                                data={'nameproduct': 'Headphones',
                                      'priceproduct': '49.99',
                                      'quantityproduct': '5',
                                      'purchase_date': '2024-01-12'},
                                      follow_redirects=True)
    assert response.status_code == 200
    assert b'Added new product!' not in response.data
    assert b'Please log in to access this page.!' in response.data

def test_get_product_list_logged_in(test_client, add_products_for_default_user):

    headers = [b'Product Name', b'Product Price', b'Purchase Date']
    data = [b'Curry', b'5.99', b'2024-01-12',
            b'Sunglasses', b'19.99', b'2024-01-12',
            b'Bicycle', b'74.99', b'2024-01-12']
    
    response = test_client.get('/product-list', follow_redirects=True)
    assert response.status_code == 200
    assert b'List of Products' in response.data
    for header in headers:
        assert header in response.data
    for element in data:
        assert element in response.data

def test_get_product_list_not_logged_in(test_client):
    response = test_client.get('/product-list', follow_redirects=True)
    assert response.status_code == 200
    assert b'List of Products' not in response.data
    assert b'Please log in to access this page.' in response.data

def test_monkeypatch_get_success(monkeypatch):
    def test_get(url):
        return MockSuccessResponse(url)
    
    url='https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', test_get)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.url == url
    assert 'Sunglasses' in r.json()['Global Quote']['01. product']
    assert '19.99' in r.json()['Global Quote']['02. price']
    assert '2024-01-12' in r.json()['Global Quote']['03. date']

def test_monkeypatch_get_failure(monkeypatch):
    def test_get(url):
        return MockFailedResponse(url)
    
    url='https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', test_get)
    r = requests.get(url)
    print(r.json())
    assert r.status_code == 404
    assert r.url == url
    assert 'bad' in r.json()['error']

def test_get_product_detail_page(test_client, add_products_for_default_user, mock_requests_get_success_weekly):
    response = test_client.get('/products/3', follow_redirects=True)
    assert response.status_code == 200
    assert b'Product Details' in response.data
    assert b'canvas id="productChart"' in response.data

def test_get_stock_detail_page_failed_response(test_client, add_products_for_default_user, mock_requests_get_failure):
    response = test_client.get('/products/3', follow_redirects=True)
    assert response.status_code == 200
    assert b'Product Details' in response.data
    assert b'canvas id="productChart"' not in response.data


def test_get_product_detail_page_incorrect_user(test_client, log_in_second_user):
    response = test_client.get('/products/3')
    assert response.status_code == 403
    assert b'Product Details' not in response.data
    assert b'canvas id="productChart"' not in response.data

def test_get_product_detail_page_invalid_product(test_client, log_in_default_user):
    response = test_client.get('/products/234')
    assert response.status_code == 404
    assert b'Product Details' not in response.data


