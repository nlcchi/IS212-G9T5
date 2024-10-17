import unittest
from unittest.mock import patch
import flask_testing
import json
from datetime import date
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

        wfh_request = WFHRequests(
                staff_id=140008,
                manager_id=140001,
                request_type='Ad-hoc',
                start_date=date(2024, 9, 15),
                end_date=date(2024, 9, 15),
                recurrence_days= None,
                is_am=True,
                is_pm=True,
                request_status='Approved',
                apply_date=date(2024, 9, 30),
                withdraw_reason = None,
                request_reason="Sick"
            )
        
        db.session.add(employee)
        db.session.add(manager)
        db.session.add(wfh_request)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

@patch('routes.staff_withdraw.date')
class TestStaffWithdraw(TestApp):

    def test_staff_withdraw_invalid_json(self, mock_datetime):
        request_body = {}

        response = self.client.post("/api/withdraw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Invalid JSON or no data provided"})

    def test_staff_withdraw_missing_field(self, mock_datetime):
        request_body = {
            'request_id': 1,
            'specific_date': "2024-09-15",
        }

        response = self.client.post("/api/withdraw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Missing 'reason' in request"})

    def test_staff_withdraw_pending(self, mock_datetime):
        wfh_request2 = WFHRequests(
                staff_id=140008,
                manager_id=140001,
                request_type='Ad-hoc',
                start_date=date(2024, 9, 17),
                end_date=date(2024, 9, 17),
                recurrence_days= None,
                is_am=True,
                is_pm=True,
                request_status='Pending',
                apply_date=date(2024, 9, 30),
                withdraw_reason = None,
                request_reason="Sick"
            )
        
        db.session.add(wfh_request2)
        db.session.commit()

        request_body = {
            'request_id': 2,
            'specific_date': "2024-09-17",
            'reason': "Not sick"
        }

        response = self.client.post("/api/withdraw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Request has not been approved."})

    def test_staff_withdraw(self, mock_datetime):
        mock_datetime.today.return_value = date(2024, 12, 12)
        mock_datetime.fromisoformat = lambda value: date.fromisoformat(value)

        request_body = {
            'request_id': 1,
            'specific_date': "2024-09-15",
            'reason': "Not sick"
        }

        response = self.client.post("/api/withdraw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')
        
        print(response.get_json())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {
            "message": "Withdraw request successfully created.",
            "request": {
                'request_id': 2,
                'staff_id': 140008,
                'manager_id': 140001,
                'request_type': 'Ad-hoc',
                'start_date': "2024-09-15",
                'end_date': "2024-09-15",
                'recurrence_days': None,
                'is_am': True,
                'is_pm': True,
                "request_status": "Pending_Withdraw",
                'apply_date': "2024-12-12",
                'withdraw_reason': "Not sick",
                'request_reason': "Sick"
                }
            })

    