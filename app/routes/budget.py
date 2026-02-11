from flask import Blueprint, jsonify
from app import db
from app.models import Budget

bp = Blueprint('budget', __name__, url_prefix='/budget')


# Set budget using URL parameter
@bp.route('/<float:limit>', methods=['POST'])
def set_budget(limit):

    budget = Budget.query.first()

    if budget:
        budget.monthly_limit = limit
    else:
        budget = Budget(monthly_limit=limit)
        db.session.add(budget)

    db.session.commit()

    return jsonify({
        "message": "Budget updated",
        "monthly_limit": limit
    }), 200


# Get current budget
@bp.route('', methods=['GET'])
def get_budget():

    budget = Budget.query.first()

    if not budget:
        return jsonify({"message": "No budget set"}), 404

    return jsonify(budget.to_json()), 200
