from . import db
import enum

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

    # FK : Links to the Category Table
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            'frequency': self.frequency.value, 
            'category': self.category_obj.name if self.category_obj else None,
            'status': self.status.value
        }
        
class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monthly_limit = db.Column(db.Float, nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "monthly_limit": self.monthly_limit
        }
