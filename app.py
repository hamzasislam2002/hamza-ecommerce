from flask import Flask, render_template, request, session, redirect, url_for, flash
from pydantic import BaseModel, ValidationError
import os
from project import create_app

app = create_app()

# app = Flask(__name__)

# app.secret_key = 'BAD_SECRET_KEY'

# config_type = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
# app.config.from_object(config_type)

# from project.products import products_blueprint
# from project.users import users_blueprint

# app.register_blueprint(products_blueprint)
# app.register_blueprint(users_blueprint, url_prefix='/users')

# class Products(BaseModel):
#     nameproduct: str
#     priceproduct: float
#     quantityproduct: int

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/about')
# def about():
#     return render_template('about.html', nameOfperson='Hamza')

# @app.route('/add_product', methods=['GET', 'POST'])
# def add_product():
#     if request.method == 'POST':
#         for k, v in request.form.items():
#             print(f'{k}: {v}')

#         try:
#             product_info = Products(
                
#                 nameproduct = request.form['nameproduct'],
#                 priceproduct = request.form['priceproduct'],
#                 quantityproduct = request.form['quantityproduct']
                
#             )
#             print(product_info)

#             session['nameproduct'] = product_info.nameproduct
#             session['priceproduct'] = product_info.priceproduct
#             session['quantityproduct'] = product_info.quantityproduct

#             flash(f"Added a new product ({product_info.nameproduct})!", 'success')
#             app.logger.info(f"Added new product ({product_info.nameproduct})")

#             return redirect(url_for('cart'))
#         except ValidationError as error:
#             print(error)
    
#     return render_template('add_products.html')

# @app.route('/product-list')
# def productList():
#     products = [
#         {"Product": "Headphones", "Price": 49.99},
#         {"Product": "Sunglasses", "Price": 19.99},
#         {"Product": "Saucepan", "Price": 24.99},
#         {"Product": "Shampoo", "Price": 6.99},
#         {"Product": "Yoga Mat", "Price": 20.99},
#         {"Product": "Blanket", "Price": 15.99},
#         {"Product": "Cookbook", "Price": 7.99},
#         {"Product": "Eiffel Tower Lego Set", "Price": 37.99},
#         {"Product": "Starbucks Coffee Roast", "Price": 5.99},
#         {"Product": "Bicycle", "Price": 74.99},
#     ]
#     render_template('product-list.html')

# @app.route('/cart')
# def cart():
#     return render_template('cart.html')