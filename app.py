from flask import Flask, request, jsonify, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func 
import os
import enum

app = Flask(__name__)

# --- Database Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'subscriptions.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 1. Define Enums ---
class FrequencyType(enum.Enum):
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"

class StatusType(enum.Enum):
    ACTIVE = "Active"
    PAUSED = "Paused"
    CANCELLED = "Cancelled"

# --- 2. Data Models ---
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relationship: One Category has many Subscriptions
    subscriptions = db.relationship('Subscription', backref='category_obj', lazy=True)

    def to_json(self):
        return {"id": self.id, "name": self.name}

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.Enum(FrequencyType), nullable=False)
    status = db.Column(db.Enum(StatusType), nullable=False, default=StatusType.ACTIVE)

    # FOREIGN KEY: Links to the Category Table
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            'frequency': self.frequency.value, 
            # Safe navigation: checks if category_obj exists
            'category': self.category_obj.name if self.category_obj else None,
            'status': self.status.value
        }

# --- 3. Helper Functions ---
def get_or_create_category(category_name):
    """
    Helper to look up a category by name (case-insensitive).
    If it doesn't exist, create it automatically.
    """
    # 1. Try to find the category
    category = Category.query.filter(func.lower(Category.name) == category_name.lower()).first()
    
    # 2. If it doesn't exist, create it!
    if not category:
        category = Category(name=category_name.capitalize()) # capitalize() makes it look nice (e.g. "gaming" -> "Gaming")
        db.session.add(category)
        db.session.commit() 
        
    return category

# --- 4. Database Initialization ---
with app.app_context():
    db.create_all()
    # Seed default categories if table is empty
    if not Category.query.first():
        defaults = ["Entertainment", "Utilities", "Health"]
        for d in defaults:
            db.session.add(Category(name=d))
        db.session.commit()

# --- 5. Error Handling ---
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request', 'message': str(error.description)}), 400)

@app.errorhandler(404)
def not_found(error):
    message = error.description if error.description else "Resource not found"
    return make_response(jsonify({'error': 'Not Found', 'message': message}), 404)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500)

# --- 6. API Endpoints ---

# CATEGORY: LIST 
@app.route('/categories', methods=['GET'])
def get_categories():
    cats = Category.query.all()
    return jsonify([c.to_json() for c in cats]), 200

# CATEGORY: CREATE
@app.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    if not data or 'name' not in data:
        return bad_request(type('obj', (object,), {'description': 'Missing required field: name'}))
    
    # Check if unique
    if Category.query.filter_by(name=data['name']).first():
         return bad_request(type('obj', (object,), {'description': f"Category '{data['name']}' already exists"}))

    new_cat = Category(name=data['name'])
    db.session.add(new_cat)
    db.session.commit()
    return jsonify({'message': 'Category created', 'category': new_cat.to_json()}), 201

# SUBSCRIPTION: CREATE
@app.route('/subscriptions', methods=['POST'])
def create_subscription():
    try:
        data = request.get_json()
        
        # 1. Validate existence of required fields
        required = ['name', 'price', 'frequency', 'category']
        if not data or not all(k in data for k in required):
            return bad_request(type('obj', (object,), {'description': f'Missing required fields. Needs: {required}'}))
        
        # 2. Validate Price
        try:
            price = float(data['price'])
            if price < 0: raise ValueError
        except ValueError:
            return bad_request(type('obj', (object,), {'description': 'Price must be a positive number'}))

        # 3. Validate Frequency Enum
        try:
            freq_enum = FrequencyType(data['frequency'])
        except ValueError:
            allowed = [e.value for e in FrequencyType]
            return bad_request(type('obj', (object,), {'description': f'Invalid frequency. Allowed: {allowed}'}))

        # 4. Status
        status_enum = StatusType.ACTIVE
        if 'status' in data:
            try:
                status_enum = StatusType(data['status'])
            except ValueError:
                allowed = [e.value for e in StatusType]
                return bad_request(type('obj', (object,), {'description': f'Invalid status. Allowed: {allowed}'}))

        # 5. Handle Category (Get existing or Create new)
        cat_obj = get_or_create_category(data['category'])

        new_sub = Subscription(
            name=data['name'],
            price=price,
            frequency=freq_enum,
            category_id=cat_obj.id, 
            status=status_enum
        )
        db.session.add(new_sub)
        db.session.commit()
        
        return jsonify({
            'message': 'Created', 
            'subscription': new_sub.to_json(),
            'note': f"Category '{cat_obj.name}' was linked successfully."
        }), 201
        
    except Exception as e:
        return internal_error(e)

# SUBSCRIPTION: READ ALL
@app.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    subs = Subscription.query.all()
    return jsonify([sub.to_json() for sub in subs]), 200

# SUBSCRIPTION: READ BY CATEGORY 
@app.route('/subscriptions/category/<string:category>', methods=['GET'])
def get_subscriptions_by_category(category):
    # FIXED: We must JOIN the Category table to filter by name
    subs = Subscription.query.join(Category).filter(
        func.lower(Category.name) == category.lower()
    ).all()
    
    if not subs:
        return jsonify({
            'message': f'No subscriptions found in category: {category}', 
            'subscriptions': []
        }), 200 

    return jsonify([sub.to_json() for sub in subs]), 200

# SUBSCRIPTION: READ ONE
@app.route('/subscriptions/<int:id>', methods=['GET'])
def get_subscription(id):
    sub = Subscription.query.get(id)
    if not sub:
        abort(404, description=f"Subscription with ID {id} not found")
    return jsonify(sub.to_json()), 200

# SUBSCRIPTION: UPDATE
@app.route('/subscriptions/<int:id>', methods=['PUT'])
def update_subscription(id):
    try:
        sub = Subscription.query.get(id)
        if not sub:
             abort(404, description=f"Subscription with ID {id} not found")

        data = request.get_json()

        if 'name' in data: sub.name = data['name']
        
        if 'price' in data:
            try:
                val = float(data['price'])
                if val < 0: raise ValueError
                sub.price = val
            except ValueError:
                return bad_request(type('obj', (object,), {'description': 'Invalid price'}))

        if 'frequency' in data:
            try:
                sub.frequency = FrequencyType(data['frequency'])
            except ValueError:
                return bad_request(type('obj', (object,), {'description': f'Invalid frequency. Allowed: {[e.value for e in FrequencyType]}'}))
        
        if 'status' in data:
            try:
                sub.status = StatusType(data['status'])
            except ValueError:
                return bad_request(type('obj', (object,), {'description': f'Invalid status. Allowed: {[e.value for e in StatusType]}'}))

        if 'category' in data: 
            cat_obj = get_or_create_category(data['category'])
            sub.category_id = cat_obj.id

        db.session.commit()
        return jsonify({'message': 'Updated', 'subscription': sub.to_json()}), 200
    except Exception as e:
        return internal_error(e)

# SUBSCRIPTION: DELETE
@app.route('/subscriptions/<int:id>', methods=['DELETE'])
def delete_subscription(id):
    sub = Subscription.query.get(id)
    if not sub:
        abort(404, description=f"Cannot delete: Subscription {id} does not exist")
        
    db.session.delete(sub)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)