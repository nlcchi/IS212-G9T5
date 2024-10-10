import unittest
import flask_testing
from server import app, db
from models import *
import datetime

class TestApp(flask_testing.TestCase):
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    app.config['TESTING'] = True

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        employee = Employee(
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

        manager = Employee(
            staff_id=140001,
            staff_fname="Derek",
            staff_lname="Tan",
            dept="Sales",
            position="Director",
            country="Singapore",
            email="Derek.Tan@allinone.com.sg",
            reporting_manager=130002,
            role=1
        )

        wfh_request1 = WFHRequests(
                staff_id=140008,
                manager_id=140001,
                request_type='Ad-hoc',
                start_date=datetime.date(2024, 9, 15),
                end_date=datetime.date(2024, 9, 15),
                recurrence_days= None,
                is_am=True,
                is_pm=True,
                request_status='Approved',
                apply_date=datetime.date(2024, 9, 30),
                withdrawable_until=datetime.date(2024, 9, 29),
                request_reason="Sick"
            )
        
        wfh_request2 = WFHRequests(
                staff_id=140008,
                manager_id=140001,
                request_type='Ad-hoc',
                start_date=datetime.date(2024, 10, 1),
                end_date=datetime.date(2024, 10, 1),
                recurrence_days= None,
                is_am=True,
                is_pm=True,
                request_status='Pending',
                apply_date=datetime.date(2024, 9, 30),
                withdrawable_until=datetime.date(2024, 10, 15),
                request_reason="Sick"
            )

        db.session.add(employee)
        db.session.add(manager)
        db.session.add(wfh_request1)
        db.session.add(wfh_request2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestStaffRequests(TestApp):
    def test_staff_requests(self):
        response = self.client.get("/api/140008", content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"], [{
                'request_id': 1,
                'staff_id': 140008,
                'manager_id': 140001,
                'request_type': 'Ad-hoc',
                'start_date': "2024-09-15",
                'end_date': "2024-09-15",
                'recurrence_days': None,
                'is_am': True,
                'is_pm': True,
                "request_status": "Approved",
                'apply_date': "2024-09-30",
                'withdrawable_until': "2024-09-29",
                'request_reason': "Sick"
                }, {
                'request_id': 2,
                'staff_id': 140008,
                'manager_id': 140001,
                'request_type': 'Ad-hoc',
                'start_date': "2024-10-01",
                'end_date': "2024-10-01",
                'recurrence_days': None,
                'is_am': True,
                'is_pm': True,
                "request_status": "Pending",
                'apply_date': "2024-09-30",
                'withdrawable_until': "2024-10-15",
                'request_reason': "Sick"
                }]
            )
        
    def test_staff_no_requests(self):
        response = self.client.get("/api/140001", content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"], [])

    def test_invalid_staff(self):
        response = self.client.get("/api/0", content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Staff not found"})

    def test_staff_pending(self):
        response = self.client.get("/api/140008/pending", content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"], [{
                'request_id': 2,
                'staff_id': 140008,
                'manager_id': 140001,
                'request_type': 'Ad-hoc',
                'start_date': "2024-10-01",
                'end_date': "2024-10-01",
                'recurrence_days': None,
                'is_am': True,
                'is_pm': True,
                "request_status": "Pending",
                'apply_date': "2024-09-30",
                'withdrawable_until': "2024-10-15",
                'request_reason': "Sick"
                }]
            )
    
    def test_staff_no_pending(self):
        response = self.client.get("/api/140001/pending", content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"], [])

    def test_invalid_staff_pending(self):
        response = self.client.get("/api/0/pending", content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Staff not found"})


if __name__ == '__main__':
    unittest.main()
