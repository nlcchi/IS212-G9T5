import unittest
import flask_testing
import json
from datetime import datetime
from server import app, db
from models import *

class TestApp(flask_testing.TestCase):
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    app.config['TESTING'] = True

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()

        self.manager = Employee(
            staff_id=140001,
            staff_fname="Derek",
            staff_lname="Tan",
            dept="Sales",
            position="Director",
            country="Singapore",
            email="Derek.Tan@allinone.com.sg",
            reporting_manager=None,  
            role=1
        )
        self.employee_1 = Employee(
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
        self.employee_2 = Employee(
            staff_id=140009,
            staff_fname="John",
            staff_lname="Doe",
            dept="Sales",
            position="Sales Associate",
            country="Singapore",
            email="John.Doe@allinone.com.sg",
            reporting_manager=140001,
            role=3
        )
        self.employee_3=Employee(
            staff_id=140010, 
            staff_fname='Sophia', 
            staff_lname='Toh', 
            dept='Sales', 
            position="Sales Manager", 
            country="Singapore",
            email="Sophia.Toh@allinone.com.sg",
            reporting_manager=140001,
            role=3
        )
        self.employee_4=Employee(
            staff_id=140011,
            staff_fname='Joseph',
            staff_lname='Tan',
            dept='Sales',
            position="Sales Manager", 
            country="Singapore",
            email="josephtan@allinone.come.sg",
            reporting_manager=140001,
            role=3
        )

        db.session.add(self.manager)
        db.session.add(self.employee_1)
        db.session.add(self.employee_2)
        db.session.add(self.employee_3)
        db.session.add(self.employee_4)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestManagerApproveAdhoc(TestApp):

    def test_approve_adhoc_invalid_json(self):
        request_body = {}
        response = self.client.post("/api/approve",
                                     data=json.dumps(request_body),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Invalid JSON or no data provided"})

    def test_approve_adhoc_request_not_found(self):
        request_body = {
            'request_id': 999, 
            'manager_id': 140001,
            'start_date': datetime.strptime("2024-09-15", '%Y-%m-%d').isoformat(),
            'end_date': datetime.strptime("2024-09-20", '%Y-%m-%d').isoformat(),
            'decision': 'Approved'
        }
        response = self.client.post("/api/approve",
                                     data=json.dumps(request_body),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Request not found"})

    def test_headcount_check_below_50_percent(self):
        wfh_request_1 = WFHRequests(
            request_id=1,
            staff_id=140008,
            manager_id=140001,
            request_type='Ad-hoc',
            start_date=datetime.strptime("2024-09-15", '%Y-%m-%d'),
            end_date=datetime.strptime("2024-09-20", '%Y-%m-%d'),
            request_status='Pending',
            apply_date=datetime.now(),
            withdrawable_until=datetime.strptime("2024-09-10", '%Y-%m-%d'),
            request_reason='Personal matters',
            is_am=False,
            is_pm=True
        )
        db.session.add(wfh_request_1)
        db.session.commit()

        request_body = {
            'request_id': 1,
            'decision_status': 'Approved',
            'start_date': '2024-09-15',  
            'decision_notes': 'Nil',
            'manager_id': 140001
        }

        response = self.client.post("/api/approve",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertIn("manager's decision stored successfully", response.get_json()["message"])

    def test_headcount_check_above_50_percent(self):
        approved_request_1 = WFHRequests(
            request_id=1,
            staff_id=140008,
            manager_id=140001,
            request_type='Ad-hoc',
            start_date=datetime.strptime("2024-09-15", '%Y-%m-%d'),
            end_date=datetime.strptime("2024-09-20", '%Y-%m-%d'),
            request_status='Approved',
            apply_date=datetime.now(),
            withdrawable_until=datetime.strptime("2024-09-10", '%Y-%m-%d'),
            request_reason='Personal matters',
            is_am=False,
            is_pm=True
        )
        approved_request_2 = WFHRequests(
            request_id=2,
            staff_id=140009,  
            manager_id=140001,
            request_type='Ad-hoc',
            start_date=datetime.strptime("2024-09-15", '%Y-%m-%d'),  
            end_date=datetime.strptime("2024-09-22", '%Y-%m-%d'),    
            request_status='Approved',
            apply_date=datetime.now(),
            withdrawable_until=datetime.strptime("2024-09-10", '%Y-%m-%d'),  
            request_reason='Medical appointment',
            is_am=True,
            is_pm=False
        )

        approved_request_3 = WFHRequests(
            request_id=3,
            staff_id=140010,  
            manager_id=140001,
            request_type='Ad-hoc',
            start_date=datetime.strptime("2024-09-15", '%Y-%m-%d'),  
            end_date=datetime.strptime("2024-09-25", '%Y-%m-%d'),    
            request_status='Approved',
            apply_date=datetime.now(),
            withdrawable_until=datetime.strptime("2024-09-10", '%Y-%m-%d'),  
            request_reason='Family matters',
            is_am=False,
            is_pm=True
        )
        db.session.add(approved_request_1)
        db.session.add(approved_request_2)
        db.session.add(approved_request_3)

        pending_request = WFHRequests(
            request_id=4,
            staff_id=140011,
            manager_id=140001,
            request_type='Ad-hoc',
            start_date=datetime.strptime("2024-09-15", '%Y-%m-%d'),
            end_date=datetime.strptime("2024-09-20", '%Y-%m-%d'),
            request_status='Pending',
            apply_date=datetime.now(),
            withdrawable_until=datetime.strptime("2024-09-10", '%Y-%m-%d'),
            request_reason='Urgent family matter',
            is_am=True,
            is_pm=False
        )
        db.session.add(pending_request)
        db.session.commit()

        request_body = {
            'request_id': 4,
            'decision': 'Approved',
            'start_date': '2024-09-15',  
        }

        response = self.client.post("/api/approve",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.get_json(), {"error": "Exceed 0.5 rule limit"})

    def test_headcount_check_exactly_50_percent(self):
        approved_request_1 = WFHRequests(
            request_id=1,
            staff_id=140008,
            manager_id=140001,
            request_type='Ad-hoc',
            start_date=datetime.strptime("2024-09-15", '%Y-%m-%d'),
            end_date=datetime.strptime("2024-09-20", '%Y-%m-%d'),
            request_status='Approved',
            apply_date=datetime.now(),
            withdrawable_until=datetime.strptime("2024-09-10", '%Y-%m-%d'),
            request_reason='Personal matters',
            is_am=False,
            is_pm=True
        )

        approved_request_2 = WFHRequests(
            request_id=2,
            staff_id=140009,  
            manager_id=140001,
            request_type='Ad-hoc',
            start_date=datetime.strptime("2024-09-15", '%Y-%m-%d'),  
            end_date=datetime.strptime("2024-09-22", '%Y-%m-%d'),    
            request_status='Pending',
            apply_date=datetime.now(),
            withdrawable_until=datetime.strptime("2024-09-10", '%Y-%m-%d'), 
            request_reason='Medical appointment',
            is_am=True,
            is_pm=False
        )

        approved_request_3 = WFHRequests(
            request_id=3,
            staff_id=140010,  
            manager_id=140001,
            request_type='Ad-hoc',
            start_date=datetime.strptime("2024-09-15", '%Y-%m-%d'),  
            end_date=datetime.strptime("2024-09-25", '%Y-%m-%d'),    
            request_status='Pending',
            apply_date=datetime.now(),
            withdrawable_until=datetime.strptime("2024-09-10", '%Y-%m-%d'),  
            request_reason='Family matters',
            is_am=False,
            is_pm=True
        )

        db.session.add(approved_request_1)
        db.session.add(approved_request_2)
        db.session.add(approved_request_3)


        pending_request = WFHRequests(
            request_id=4,
            staff_id=140009,
            manager_id=140001,
            request_type='Ad-hoc',
            start_date=datetime.strptime("2024-09-15", '%Y-%m-%d'),
            end_date=datetime.strptime("2024-09-20", '%Y-%m-%d'),
            request_status='Approved',
            apply_date=datetime.now(),
            withdrawable_until=datetime.strptime("2024-09-10", '%Y-%m-%d'),
            request_reason='Urgent family matter',
            is_am=True,
            is_pm=False
        )
        db.session.add(pending_request)
        db.session.commit()

        request_body = {
            'request_id': 4,
            'decision_status': 'Approved',
            'start_date': '2024-09-15',  
            'decision_notes': 'Nil',
            'manager_id': 140001
        }


        response = self.client.post("/api/approve",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    unittest.main()
