from flask import Blueprint, jsonify
from app import db
from app.models import Subscription, FrequencyType, StatusType

bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@bp.route('', methods=['GET'])
def monthly_total():

    subs = Subscription.query.filter_by(status=StatusType.ACTIVE).all()

    total_month = 0
    breakdown = []

    for s in subs:
        if s.frequency == FrequencyType.MONTHLY:
            monthly_price = s.price
        elif s.frequency == FrequencyType.YEARLY:
            monthly_price = s.price / 12
        elif s.frequency == FrequencyType.WEEKLY:
            monthly_price = s.price * 4
        else:
            monthly_price = 0

        total_month += monthly_price

        breakdown.append({
            "name": s.name,
            "monthly_equivalent": round(monthly_price, 2)
        })

    total_year = total_month * 12

    return jsonify({
        "total_price_per_month": round(total_month, 2),
        "total_price_per_year": round(total_year, 2),
        "active_subscriptions": len(subs),
        "breakdown": breakdown
    }), 200

