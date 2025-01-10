from project.models import Product, User 

def test_new_product(new_product):
    
    assert new_product.name == 'Curry'
    assert new_product.price == 5.99

def test_new_user(new_user):
    assert new_user.email == 'hamza@curry.com'
    assert new_user.password_hashed != 'Curry123'