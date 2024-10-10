import unittest
import flask_testing
from server import app, db
from models import Employee

class TestApp(flask_testing.TestCase):
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    app.config['TESTING'] = True

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        new_employee = Employee(
            staff_id=140008,
            staff_fname="Jaclyn",
            staff_lname="Lee",
            dept="Sales",
            position="Sales Manager",
            country="Singapore",
            email="Jaclyn.Lee@allinone.com.sg",
            reporting_manager=140001,
            role=3
        )
        db.session.add(new_employee)
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestEmployee(TestApp):
    def test_get_employee(self):
        staff_id = 140008

        response = self.client.get(f"/api/staff/{staff_id}",
                                    content_type='application/json')
        
        self.assertEqual(response.json, {
        "country": "Singapore",
        "dept": "Sales",
        "email": "Jaclyn.Lee@allinone.com.sg",
        "position": "Sales Manager",
        "reporting_manager": 140001,
        "role": 3,
        "staff_fname": "Jaclyn",
        "staff_id": 140008,
        "staff_lname": "Lee"
        })

if __name__ == '__main__':
    unittest.main()
