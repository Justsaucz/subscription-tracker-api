import unittest
import json
from app import app, db, Subscription, FrequencyType, StatusType

class SubscriptionTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_valid_subscription(self):
        payload = {
            "name": "Netflix",
            "price": 19.99,
            "frequency": "Monthly",  
            "category": "Entertainment",
            "status": "Active"
        }
        response = self.app.post('/subscriptions', 
                                 data=json.dumps(payload), 
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn("Netflix", str(response.data))

    def test_create_invalid_enum(self):
        # Sending "Daily" which is NOT in our FrequencyType Enum
        payload = {
            "name": "Bad Data",
            "price": 10,
            "frequency": "Daily", 
            "category": "Misc"
        }
        response = self.app.post('/subscriptions', 
                                 data=json.dumps(payload), 
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid frequency", str(response.data))

    def test_update_status(self):
        # Create first
        with app.app_context():
            sub = Subscription(name="Gym", price=50, frequency=FrequencyType.MONTHLY, category="Health")
            db.session.add(sub)
            db.session.commit()

        # Update status to Cancelled
        payload = {"status": "Cancelled"}
        response = self.app.put('/subscriptions/1', 
                                data=json.dumps(payload), 
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Cancelled", str(response.data))

if __name__ == '__main__':
    unittest.main()