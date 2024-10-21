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
                request_id='1',
                staff_id=140008,
                manager_id=140001,
                specific_date=datetime.date(2024, 9, 15),
                is_am=True,
                is_pm=True,
                request_status='Approved',
                apply_date=datetime.date(2024, 9, 30),
                request_reason="Sick"
            )
        
        wfh_request2 = WFHRequests(
                request_id='2',
                staff_id=140008,
                manager_id=140001,
                specific_date=datetime.date(2024, 10, 1),
                is_am=True,
                is_pm=True,
                request_status='Pending',
                apply_date=datetime.date(2024, 9, 30),
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


class TestWFHRequests(TestApp):
    # Get all WFH requests for a specific staff id
    def test_wfh_requests_by_staffId(self):
        response = self.client.get("/api/staff/140008/all_wfh_dates", content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [
            {
                'request_id': '1',
                'staff_id': 140008,
                'manager_id': 140001,
                'specific_date': '2024-09-15',
                'is_am': True,
                'is_pm': True,
                'request_status': 'Approved',
                'apply_date': '2024-09-30',
                'request_reason': 'Sick'
            },
            {
                'request_id': '2',
                'staff_id': 140008,
                'manager_id': 140001,
                'specific_date': '2024-10-01',
                'is_am': True,
                'is_pm': True,
                'request_status': 'Pending',
                'apply_date': '2024-09-30',
                'request_reason': 'Sick'
            }
        ])

    # Get WFH requests for a specific staff id in a certain date range
    def test_wfh_requests_by_staffId_range(self):
        response = self.client.get("/api/staff/140008/wfh_requests?start_date=2024-09-01&end_date=2024-09-30", content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [
            {
                'request_id': '1',
                'staff_id': 140008,
                'manager_id': 140001,
                'specific_date': '2024-09-15',
                'is_am': True,
                'is_pm': True,
                'request_status': 'Approved',
                'apply_date': '2024-09-30',
                'request_reason': 'Sick'
            }
        ])

    # Get WFH requests with no records found
    def test_wfh_requests_by_staffId_empty(self):
        response = self.client.get("/api/staff/140001/all_wfh_dates", content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {'message': 'No WFH dates found for this staff member'})

    # Test missing date range parameters
    def test_wfh_requests_missing_date_range(self):
        response = self.client.get("/api/staff/140008/wfh_requests", content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Please provide both start_date and end_date"})

    # Test no WFH requests found in the given date range
    def test_wfh_requests_by_staffId_range_no_data(self):
        response = self.client.get("/api/staff/140008/wfh_requests?start_date=2025-01-01&end_date=2025-01-31", content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"message": "No WFH requests found for this staff member in the given date range"})

    # Test WFH requests when start_date and end_date are the same
    def test_wfh_requests_by_staffId_same_date(self):
        response = self.client.get("/api/staff/140008/wfh_requests?start_date=2024-09-15&end_date=2024-09-15", content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [
            {
                'request_id': '1',
                'staff_id': 140008,
                'manager_id': 140001,
                'specific_date': '2024-09-15',
                'is_am': True,
                'is_pm': True,
                'request_status': 'Approved',
                'apply_date': '2024-09-30',
                'request_reason': 'Sick'
            }
        ])

    # Test WFH requests with a date range that includes no valid requests
    def test_wfh_requests_by_staffId_range_out_of_bounds(self):
        response = self.client.get("/api/staff/140008/wfh_requests?start_date=2023-09-01&end_date=2023-09-30", content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"message": "No WFH requests found for this staff member in the given date range"})


if __name__ == '__main__':
    unittest.main()
