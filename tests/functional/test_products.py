
def test_index_page(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'Welcome to' in response.data 

def test_get_product(test_client):
    response = test_client.get('/add_product')
    assert response.status_code == 200
    assert b'For reference, refer to the list' in response.data
    assert b'Product Name' in response.data
    assert b'Price' in response.data
    assert b'Quantity' in response.data

def test_post_product(test_client):
    response = test_client.post('/add_product',
                                data={'nameproduct': 'Headphones',
                                      'priceproduct': '49.99',
                                      'quantityproduct': '5'},
                                      follow_redirects=True)
    assert response.status_code == 200
    assert b'Headphones' in response.data
    assert b'49.99' in response.data
    assert b'5' in response.data
    