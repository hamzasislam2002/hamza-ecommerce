from flask import current_app, render_template, request, session, flash, url_for, redirect
from . import products_blueprint
from pydantic import BaseModel, ValidationError, Field
from project.models import Product
from project import database
from sqlalchemy import select, desc
import click


@products_blueprint.before_request
def products_before_request():
        current_app.logger.info('Calling before_request() for the Flask application')

@products_blueprint.after_request
def products_after_request(response):
    current_app.logger.info('Calling after_request() for the Flask application')
    return response

@products_blueprint.teardown_request
def products_teardown_request(error=None):
    current_app.logger.info('Calling before_request() for the Flask application')


@products_blueprint.route('/')
def index():
    return render_template('products/index.html')

class Products(BaseModel):
    nameproduct: str
    priceproduct: float
    quantityproduct: int = Field(None, description="Quantity for informational purposes")

@products_blueprint.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        for k, v in request.form.items():
            print(f'{k}: {v}')

        try:
            product_info = Products(
                
                nameproduct = request.form['nameproduct'],
                priceproduct = request.form['priceproduct'],
                # quantityproduct = request.form['quantityproduct']
                
                
            )
            print(product_info)

            new_products = Product(
                product_info.nameproduct,
                product_info.priceproduct)
                # product_info.quantityproduct)
            
            database.session.add(new_products)
            database.session.commit()

            quantityproduct = request.form.get('quantityproduct', None)
            if quantityproduct:
                session['quantityproduct'] = quantityproduct  # Store in session for temporary use

            # session['nameproduct'] = product_info.nameproduct
            # session['priceproduct'] = product_info.priceproduct
            # session['quantityproduct'] = product_info.quantityproduct

            flash(f"Added a new product ({product_info.nameproduct})!", 'success')
            current_app.logger.info(f"Added new product ({product_info.nameproduct})")

            return redirect(url_for('products.cart'))
        except ValidationError as error:
            print(error)
    
    return render_template('products/add_products.html')

@products_blueprint.route('/product-list')
def productList():
    
    # products = Product.query.all()
    # products = [
    #     {"Product": "Headphones", "Price": 49.99},
    #     {"Product": "Sunglasses", "Price": 19.99},
    #     {"Product": "Saucepan", "Price": 24.99},
    #     {"Product": "Shampoo", "Price": 6.99},
    #     {"Product": "Yoga Mat", "Price": 20.99},
    #     {"Product": "Blanket", "Price": 15.99},
    #     {"Product": "Cookbook", "Price": 7.99},
    #     {"Product": "Eiffel Tower Lego Set", "Price": 37.99},
    #     {"Product": "Starbucks Coffee Roast", "Price": 5.99},
    #     {"Product": "Bicycle", "Price": 74.99},
    # ]

    query = select(Product).order_by(desc(Product.price)) 

    result = database.session.execute(query).scalars().all()

    return render_template('products/product-list.html', products=result)

@products_blueprint.route('/cart')
def cart():
    return render_template('products/cart.html')

# @products_blueprint.cli.command('create_default_set')
# def create_default_set():
#     product_more_one = Product('Curry', '3.99')
#     product_more_two = Product('Playstation 5', '399.99')
#     database.session.add(product_more_one)
#     database.session.add(product_more_two)
#     database.session.commit()

# @products_blueprint.cli.command('create')
# @click.argument('name')
# @click.argument('price')
# def create(name, price):
#     product_more_info = Product(name, price)
#     database.session.add(product_more_info)
#     database.session.commit()