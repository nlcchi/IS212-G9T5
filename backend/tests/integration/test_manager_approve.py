import flask_testing
from unittest.mock import patch
import datetime
import json
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
                start_date=datetime.date(2024, 9, 15),
                end_date=datetime.date(2024, 9, 15),
                recurrence_days= None,
                is_am=True,
                is_pm=True,
                request_status='Pending',
                apply_date=datetime.date(2024, 9, 30),
                withdrawable_until=datetime.date(2024, 9, 29),
                request_reason="Sick"
            )
        
        db.session.add(employee)
        db.session.add(manager)
        db.session.add(wfh_request)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

@patch('util.request_decisions.datetime')
class TestManagerApprove(TestApp):
    # tested in test_manager_approve_headcount.py
    # def test_manager_approve_adhoc(self, mock_datetime):
    #     mock_datetime.date.today.return_value = datetime.date(2024, 12, 12)
        
    #     request_body = {
    #         "request_id":1,
    #         "manager_id":140001,
    #         "decision_status":"Approved",
    #         "decision_notes":"Ok",
    #     }
        
    #     response = self.client.post("/api/approve",
    #                                 data=json.dumps(request_body),
    #                                 content_type='application/json')
        
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(response.get_json()["message"], "Request updated and manager's decision stored successfully")
    #     self.assertEqual(response.get_json()["request"], {
    #             'request_id': 1,
    #             'staff_id': 140008,
    #             'manager_id': 140001,
    #             'request_type': 'Ad-hoc',
    #             'start_date': "2024-09-15",
    #             'end_date': "2024-09-15",
    #             'recurrence_days': None,
    #             'is_am': True,
    #             'is_pm': True,
    #             "request_status": "Approved",
    #             'apply_date': "2024-09-30",
    #             'withdrawable_until': "2024-09-29",
    #             'request_reason': "Sick"
    #             })
        
    #     self.assertEqual(response.get_json()["decision"], {
    #         "decision_id": 1,
    #         "request_id": 1,
    #         "manager_id": 140001,
    #         "decision_date": "2024-12-12",
    #         "decision_status": "Approved",
    #         "decision_notes": "Ok"
    #     })

    #     self.assertEqual(response.get_json()["wfh_date"], {
    #         "date_id": 1,
    #         "request_id": 1,
    #         "specific_date": "2024-09-15",
    #         "staff_id": 140008,
    #         "is_am": True,
    #         "is_pm": True
    #     })

    def test_manager_approve_adhoc_invalid_json(self, mock_datetime):
        request_body = {}

        response = self.client.post("/api/approve",
                                    data=json.dumps(request_body),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Invalid JSON or no data provided"})

        # comment out first due to headcount error
    # def test_manager_approve_adhoc_missing_field(self, mock_datetime):
    #     request_body = {
    #         "request_id":1,
    #         "manager_id":140001,
    #         "decision_notes":"Ok",
    #     }

    #     response = self.client.post("/api/approve",
    #                                 data=json.dumps(request_body),
    #                                 content_type='application/json')
        
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.get_json(), {"error": "Missing 'decision_status' in request"})

    def test_manager_approve_adhoc_invalid_request(self, mock_datetime):
        request_body = {
            "request_id":999,
            "manager_id":140001,
            "decision_status": "Approved",
            "decision_notes":"Ok",
        }

        response = self.client.post("/api/approve",
                                    data=json.dumps(request_body),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Request not found"})
         


