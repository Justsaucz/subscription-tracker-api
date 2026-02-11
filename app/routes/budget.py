from flask import Blueprint, jsonify
from app import db
from app.models import Budget, Subscription, FrequencyType, StatusType

bp = Blueprint('budget', __name__, url_prefix='/budget')

@app.route("/budget/<int:limit>", methods=["PUT"])
def set_budget(limit):

    if limit <= 0:
        return jsonify({"error": "Budget must be positive"}), 400

    budget = Budget.query.first()

    if not budget:
        budget = Budget(monthly_limit=limit)
        db.session.add(budget)
    else:
        budget.monthly_limit = limit

    db.session.commit()

    return jsonify({
        "message": "Budget updated",
        "monthly_limit": budget.monthly_limit
    }), 200

@bp.route('', methods=['GET'])
def get_budget():

    budget = Budget.query.first()

    if not budget:
        return jsonify({"message": "No budget set"}), 404

    return jsonify(budget.to_json()), 200

@bp.route('/status', methods=['GET'])
def budget_status():

    subs = Subscription.query.filter_by(
        status=StatusType.ACTIVE
    ).all()

    budget = Budget.query.first()

    if not budget:
        return jsonify({"error": "No budget set"}), 404

    total_month = 0

    for s in subs:
        if s.frequency == FrequencyType.MONTHLY:
            total_month += s.price
        elif s.frequency == FrequencyType.YEARLY:
            total_month += s.price / 12
        elif s.frequency == FrequencyType.WEEKLY:
            total_month += s.price * 4

    used_percent = (total_month / budget.monthly_limit) * 100
    remaining = budget.monthly_limit - total_month

    return jsonify({
        "monthly_budget": budget.monthly_limit,
        "current_spending": round(total_month, 2),
        "remaining_budget": round(remaining, 2),
        "usage_percent": round(used_percent, 2)
    }), 200
