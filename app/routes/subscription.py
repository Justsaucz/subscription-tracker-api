from flask import Blueprint, request, jsonify, abort
from app import db
from app.models import Subscription, Category, FrequencyType, StatusType
from sqlalchemy import func
from app.models import Budget

# Define Blueprint
bp = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')

# --- Helper Function ---
def get_or_create_category(category_name):
    # 1. Try to find the category
    category = Category.query.filter(func.lower(Category.name) == category_name.lower()).first()
    
    # 2. If it doesn't exist, create it!
    if not category:
        category = Category(name=category_name.capitalize())
        db.session.add(category)
        db.session.commit() 
        
    return category

# --- Routes ---

# GET ALL (with optional ?category= filter)
@bp.route('', methods=['GET'])
def get_subscriptions():
    category_name = request.args.get('category')
    
    if category_name:
        subs = Subscription.query.join(Category).filter(
            func.lower(Category.name) == category_name.lower()
        ).all()
        # Optional: return empty list if not found, consistent with your previous logic
        if not subs:
             return jsonify({
                'message': f'No subscriptions found in category: {category_name}', 
                'subscriptions': []
            }), 200
    else:
        subs = Subscription.query.all()
        
    return jsonify([sub.to_json() for sub in subs]), 200

# GET ONE
@bp.route('/<int:id>', methods=['GET'])
def get_subscription(id):
    # Use db.session.get to avoid Legacy warning
    sub = db.session.get(Subscription, id)
    if not sub:
        abort(404, description=f"Subscription with ID {id} not found")
    return jsonify(sub.to_json()), 200

# CREATE
@bp.route('', methods=['POST'])
def create_subscription():
    try:
        data = request.get_json()
        
        # 1. Validate required fields
        required = ['name', 'price', 'frequency', 'category']
        if not data or not all(k in data for k in required):
            abort(400, description=f'Missing required fields. Needs: {required}')
        
        # 2. Validate Price
        try:
            price = float(data['price'])
            if price < 0: raise ValueError
        except ValueError:
            abort(400, description='Price must be a positive number')

        # 3. Validate Frequency Enum
        try:
            freq_enum = FrequencyType(data['frequency'])
        except ValueError:
            allowed = [e.value for e in FrequencyType]
            abort(400, description=f'Invalid frequency. Allowed: {allowed}')

        # 4. Status (Optional)
        status_enum = StatusType.ACTIVE
        if 'status' in data:
            try:
                status_enum = StatusType(data['status'])
            except ValueError:
                allowed = [e.value for e in StatusType]
                abort(400, description=f'Invalid status. Allowed: {allowed}')

         # 5. Budget limit 

        budget = Budget.query.first()

        if budget and status_enum == StatusType.ACTIVE:

            active_subs = Subscription.query.filter_by(
                status=StatusType.ACTIVE
            ).all()

            total_month = 0

            for s in active_subs:
                if s.frequency == FrequencyType.MONTHLY:
                    total_month += s.price
                elif s.frequency == FrequencyType.YEARLY:
                    total_month += s.price / 12
                elif s.frequency == FrequencyType.WEEKLY:
                    total_month += s.price * 4

            # add new subscription estimate
            if freq_enum == FrequencyType.MONTHLY:
                total_month += price
            elif freq_enum == FrequencyType.YEARLY:
                total_month += price / 12
            elif freq_enum == FrequencyType.WEEKLY:
                total_month += price * 4

            if total_month > budget.monthly_limit:
                abort(400, description="Budget limit exceeded!")

        # 6. Handle Category
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
        # Check if it's an abort exception (HTTPException), otherwise 500
        if hasattr(e, 'code'): raise e 
        abort(500, description=str(e))

# UPDATE
@bp.route('/<int:id>', methods=['PUT'])
def update_subscription(id):
    try:
        sub = db.session.get(Subscription, id)
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
                abort(400, description='Invalid price')

        if 'frequency' in data:
            try:
                sub.frequency = FrequencyType(data['frequency'])
            except ValueError:
                abort(400, description=f'Invalid frequency. Allowed: {[e.value for e in FrequencyType]}')
        
        if 'status' in data:
            try:
                sub.status = StatusType(data['status'])
            except ValueError:
                abort(400, description=f'Invalid status. Allowed: {[e.value for e in StatusType]}')

        if 'category' in data: 
            cat_obj = get_or_create_category(data['category'])
            sub.category_id = cat_obj.id

        db.session.commit()
        return jsonify({'message': 'Updated', 'subscription': sub.to_json()}), 200
    except Exception as e:
        if hasattr(e, 'code'): raise e
        abort(500, description=str(e))

# DELETE
@bp.route('/<int:id>', methods=['DELETE'])
def delete_subscription(id):
    sub = db.session.get(Subscription, id)
    if not sub:
        abort(404, description=f"Cannot delete: Subscription {id} does not exist")
        
    db.session.delete(sub)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'}), 200
