"""
app.py file will be used here for unit tests
"""

from project.products.routes import Products
import pytest
from pydantic import ValidationError

def test_validate_products_simple():
    """
    GIVEN opportunity to enter information about product
    WHEN product information is entered
    THEN check that validation was successful
    """
    product_info = Products(
        nameproduct = 'Headphones',
        priceproduct = '49.99',
        quantityproduct = '2'
    )

    assert product_info.nameproduct == 'Headphones'
    assert product_info.priceproduct == 49.99
    assert product_info.quantityproduct == 2

def test_invalid_quantity_data():
     """
    GIVEN opportunity to enter information about product
    WHEN product information is entered incorrectly such as quantity
    THEN check for ValueError
    """
     
     with pytest.raises(ValueError):
          Products(
            nameproduct = 'Headphones',
            priceproduct = '49.99',
            quantityproduct = '2.14387'
          )

def test_missing_all_data():
    """
        GIVEN opportunity to enter information about product
        WHEN product information is entered incorrectly such as quantity
        THEN check for ValidationError
    """

    with pytest.raises(ValidationError):
         Products()



    