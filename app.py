from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'shophub-secret-key-2026')

database_url = os.environ.get('DATABASE_URL', 'sqlite:///shophub.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    old_price = db.Column(db.Integer, nullable=True)
    icon = db.Column(db.String(10), default='📦')
    description = db.Column(db.Text, default='')
    stock = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.Text, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_icon = db.Column(db.String(10), default='📦')
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product')


# ===================== YORDAMCHI FUNKSIYALAR =====================

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Avval tizimga kiring!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Bu sahifa faqat adminlar uchun!', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


def format_price(price):
    return f"{price:,}".replace(',', ' ')


app.jinja_env.globals['format_price'] = format_price



@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash('Parollar mos kelmadi!', 'error')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Bu username band!', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Bu email band!', 'error')
            return render_template('register.html')

        hashed = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Ro'yxatdan o'tdingiz! Kiring.", 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Xush kelibsiz, {user.username}!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash("Username yoki parol noto'g'ri!", 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Tizimdan chiqdingiz.', 'success')
    return redirect(url_for('login'))

# === VAQTINCHALIK — ishlatib bo'lgach O'CHIRISH KERAK ===
@app.route('/change-admin-pass')
def change_admin_pass():
    user = User.query.filter_by(username='admin').first()
    user.password = generate_password_hash('YangiParol123')
    db.session.commit()
    return 'Parol almashtirildi!'
# shu yergacha
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    products = Product.query.order_by(Product.created_at.desc()).limit(8).all()
    return render_template('index.html', products=products)


@app.route('/products')
def products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    query = Product.query
    if category != 'all':
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    products = query.all()
    return render_template('products.html', products=products, category=category, search=search)


@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', {})
    items = []
    total = 0
    for product_id, qty in cart_items.items():
        product = Product.query.get(int(product_id))
        if product:
            items.append({'product': product, 'quantity': qty, 'subtotal': product.price * qty})
            total += product.price * qty
    return render_template('cart.html', items=items, total=total)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    cart = session.get('cart', {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session['cart'] = cart
    flash("Mahsulot savatga qo'shildi!", 'success')
    return redirect(request.referrer or url_for('products'))


@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    product_id = request.form.get('product_id')
    action = request.form.get('action')
    cart = session.get('cart', {})
    if action == 'increase':
        cart[product_id] = cart.get(product_id, 0) + 1
    elif action == 'decrease':
        cart[product_id] = cart.get(product_id, 1) - 1
        if cart[product_id] <= 0:
            cart.pop(product_id, None)
    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = session.get('cart', {})
    if not cart_items:
        flash("Savat bo'sh!", 'error')
        return redirect(url_for('cart'))

    if request.method == 'POST':
        items = []
        total = 0
        for product_id, qty in cart_items.items():
            product = Product.query.get(int(product_id))
            if product:
                items.append({'product': product, 'quantity': qty})
                total += product.price * qty

        order = Order(
            user_id=session['user_id'],
            customer_name=request.form['name'],
            customer_phone=request.form['phone'],
            customer_address=request.form['address'],
            total=total
        )
        db.session.add(order)
        db.session.flush()

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                product_name=item['product'].name,
                product_icon=item['product'].icon,
                price=item['product'].price,
                quantity=item['quantity']
            )
            db.session.add(order_item)

        db.session.commit()
        session['cart'] = {}
        flash('Buyurtma muvaffaqiyatli qabul qilindi!', 'success')
        return redirect(url_for('my_orders'))

    items = []
    total = 0
    for product_id, qty in cart_items.items():
        product = Product.query.get(int(product_id))
        if product:
            items.append({'product': product, 'quantity': qty})
            total += product.price * qty

    return render_template('checkout.html', items=items, total=total)


@app.route('/my_orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('my_orders.html', orders=orders)


@app.route('/admin')
@admin_required
def admin_dashboard():
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_users = User.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           total_products=total_products,
                           total_orders=total_orders,
                           total_users=total_users,
                           pending_orders=pending_orders,
                           recent_orders=recent_orders)


@app.route('/admin/products')
@admin_required
def admin_products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)


@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    if request.method == 'POST':
        product = Product(
            name=request.form['name'],
            category=request.form['category'],
            price=int(request.form['price']),
            old_price=int(request.form['old_price']) if request.form['old_price'] else None,
            icon=request.form['icon'],
            description=request.form['description'],
            stock=int(request.form['stock'])
        )
        db.session.add(product)
        db.session.commit()
        flash("Mahsulot qo'shildi!", 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', product=None)


@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.category = request.form['category']
        product.price = int(request.form['price'])
        product.old_price = int(request.form['old_price']) if request.form['old_price'] else None
        product.icon = request.form['icon']
        product.description = request.form['description']
        product.stock = int(request.form['stock'])
        db.session.commit()
        flash('Mahsulot yangilandi!', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', product=product)


@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Mahsulot o'chirildi!", 'success')
    return redirect(url_for('admin_products'))


@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)


@app.route('/admin/orders/update/<int:order_id>', methods=['POST'])
@admin_required
def admin_update_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form['status']
    db.session.commit()
    flash('Buyurtma holati yangilandi!', 'success')
    return redirect(url_for('admin_orders'))


@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)



def create_tables():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(role='admin').first():
            admin = User(
                username='admin',
                email='admin@shophub.uz',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)

        if Product.query.count() == 0:
            demo_products = [
                Product(name='Smartphone Pro Max', category='electronics', price=4500000, old_price=5500000, icon='📱'),
                Product(name='Wireless Headphones', category='electronics', price=850000, old_price=1200000, icon='🎧'),
                Product(name='Laptop UltraSlim', category='electronics', price=8900000, old_price=10500000, icon='💻'),
                Product(name='Smart Watch', category='electronics', price=1800000, old_price=2200000, icon='⌚'),
                Product(name='Premium Jacket', category='clothing', price=650000, old_price=900000, icon='🧥'),
                Product(name='Running Shoes', category='clothing', price=450000, old_price=600000, icon='👟'),
                Product(name='Sunglasses', category='accessories', price=350000, old_price=500000, icon='🕶️'),
                Product(name='Coffee Maker', category='home', price=950000, old_price=1300000, icon='☕'),
            ]
            db.session.add_all(demo_products)

        db.session.commit()


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
