from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from app.extensions import db
from app.models.bicycle import Bicycle, Order, Category
from flask_login import current_user, login_required
import uuid

# Blueprint definitions
profile = Blueprint('profile', __name__)
main = Blueprint('main', __name__)
cart = Blueprint('cart', __name__)

@main.route('/')
def home():
    # Getting the filter parameters from the request
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    category_id = request.args.get('category_id', type=int)

    # Find the maximum price among all bicycles
    max_bicycle_price = db.session.query(db.func.max(Bicycle.price)).scalar() or 10000  # Default Value

    # Creating a query with filters
    bicycles_query = db.session.query(Bicycle)
    if min_price is not None:
        bicycles_query = bicycles_query.filter(Bicycle.price >= min_price)
    if max_price is not None:
        bicycles_query = bicycles_query.filter(Bicycle.price <= max_price)
    if category_id:
        bicycles_query = bicycles_query.filter(Bicycle.category_id == category_id)

    # Get a list of bicycles and categories
    bicycles = bicycles_query.all()
    categories = db.session.query(Category).all()

    return render_template(
        'home.html',
        bicycles=bicycles,
        categories=categories,
        max_bicycle_price=max_bicycle_price  # Transfer the max price to html
    )



# Cart initialization
@cart.route('/add_to_cart/<int:bicycle_id>', methods=['POST'])
@login_required
def add_to_cart(bicycle_id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(bicycle_id)
    flash('Bicycle was added to cart!', 'success')
    return redirect(url_for('main.home'))

# Cart view
@cart.route('/cart')
@login_required
def view_cart():
    if 'cart' not in session or not session['cart']:
        bicycles = []
    else:
        bicycles = Bicycle.query.filter(Bicycle.id.in_(session['cart'])).all()

    return render_template('cart/view_cart.html', bicycles=bicycles)

@cart.route('/remove_from_cart/<int:bicycle_id>', methods=['POST'])
@login_required
def remove_from_cart(bicycle_id):
    if 'cart' in session:
        session['cart'] = [bike_id for bike_id in session['cart'] if bike_id != bicycle_id]
        flash('Bicycle was deleted from cart!', 'info')

    return redirect(url_for('cart.view_cart'))

@cart.route('/checkout', methods=['POST'])
@login_required
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('main.home'))

    bicycles = Bicycle.query.filter(Bicycle.id.in_(session['cart'])).all()
    order_number = str(uuid.uuid4())[:8]

    # Создаем новый заказ
    new_order = Order(order_number=order_number, user_id=current_user.id)
    new_order.bicycles = bicycles
    db.session.add(new_order)
    db.session.commit()

    # Очищаем корзину
    session.pop('cart')
    flash('Your order was successfully confirmed!', 'success')
    return render_template('cart/order_confirmation.html', bicycles=bicycles, order_number=order_number)

# User profile view
@profile.route('/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    if request.method == 'POST':
        current_user.username = request.form['username']
        current_user.email = request.form['email']

        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if current_password and new_password and confirm_password:
            if not current_user.check_password(current_password):
                flash('Current password incorrect', 'danger')
                return redirect(url_for('profile.user_profile'))

            if new_password != confirm_password:
                flash('Password are not similarly!', 'danger')
                return redirect(url_for('profile.user_profile'))

            current_user.set_password(new_password)
            flash('Password was updated!', 'success')

        db.session.commit()
        flash('Info was updated!', 'success')
        return redirect(url_for('profile.user_profile'))

    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('profile/profile.html', user=current_user, orders=orders)


# View specific order
@profile.route('/order/<int:order_id>')
@login_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('You can not see this order!', 'danger')
        return redirect(url_for('profile.user_profile'))

    return render_template('profile/order_details.html', order=order)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/care')
def care():
    return render_template('care.html')
