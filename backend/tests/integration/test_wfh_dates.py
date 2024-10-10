import unittest
import flask_testing
import json
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
        
        wfh_date1 = WFHRequestDates(
                date_id=1,
                request_id=1,
                specific_date=datetime.date(2024, 9, 15),
                staff_id=140008,
                decision_status="Approved",
                is_am=True,
                is_pm=True
            )
        
        wfh_date2 = WFHRequestDates(
                date_id=2,
                request_id=2,
                specific_date=datetime.date(2024, 10, 1),
                staff_id=140008,
                decision_status="Approved",
                is_am=True,
                is_pm=True
            )

        db.session.add(employee)
        db.session.add(manager)
        db.session.add(wfh_request1)
        db.session.add(wfh_request2)
        db.session.add(wfh_date1)
        db.session.add(wfh_date2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestWFHDates(TestApp):
    #get all wfh dates for a certain staff id
    def test_wfh_dates_by_staffId(self):
        
        response = self.client.get("/api/staff/140008/all_wfh_dates", content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [
            {
                'date_id': 1, 
                'decision_status': 'Approved', 
                'is_am': True, 
                'is_pm': True, 
                'request_id': 1, 
                'specific_date': '2024-09-15', 
                'staff_id': 140008
            }, 
            {
                'date_id': 2, 
                'decision_status': 'Approved', 
                'is_am': True, 
                'is_pm': True, 
                'request_id': 2, 
                'specific_date': '2024-10-01', 
                'staff_id': 140008
            }])
    
    def test_wfh_dates_by_staffId_empty(self):
        
        response = self.client.get("/api/staff/140001/all_wfh_dates", content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {'message': 'No WFH dates found for this staff member'})
        
    # Get all approved wfh dates for a certain staff id in a certain date range
    #GET /api/staff/1/wfh_dates?start_date=2024-09-01&end_date=2024-09-30

    def test_wfh_dates_by_staffId_range(self):
        
        response = self.client.get("/api/staff/140008/wfh_dates?start_date=2024-09-01&end_date=2024-09-30", content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [
            {
                'date_id': 1, 
                'decision_status': 'Approved', 
                'is_am': True, 
                'is_pm': True, 
                'request_id': 1, 
                'specific_date': '2024-09-15', 
                'staff_id': 140008
            }])

    def test_wfh_dates_by_staffId_range_withdrawn(self):
        wfh_request3 = WFHRequests(
                staff_id=140008,
                manager_id=140001,
                request_type='Ad-hoc',
                start_date=datetime.date(2024, 9, 16),
                end_date=datetime.date(2024, 9, 16),
                recurrence_days= None,
                is_am=True,
                is_pm=True,
                request_status='Pending',
                apply_date=datetime.date(2024, 9, 30),
                withdrawable_until=datetime.date(2024, 9, 30),
                request_reason="Sick"
            )
        
        wfh_date3 = WFHRequestDates(
                date_id=3,
                request_id=3,
                specific_date=datetime.date(2024, 9, 16),
                staff_id=140008,
                decision_status="Withdrawn",
                is_am=True,
                is_pm=True
            )
        
        db.session.add(wfh_request3)
        db.session.add(wfh_date3)
        db.session.commit()

        response = self.client.get("/api/staff/140008/wfh_dates?start_date=2024-09-01&end_date=2024-09-30", content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [
            {
                'date_id': 1, 
                'decision_status': 'Approved', 
                'is_am': True, 
                'is_pm': True, 
                'request_id': 1, 
                'specific_date': '2024-09-15', 
                'staff_id': 140008
            }])
        
    # Get all wfh dates and in office dates for a certain staff id in a certain date range
    #GET /api/staff/1/wfh_office_dates?start_date=2024-09-01&end_date=2024-09-30 
    
    def test_wfh_dates_by_staffId_wfh_office(self):
        wfh_request3 = WFHRequests(
                staff_id=140008,
                manager_id=140001,
                request_type='Ad-hoc',
                start_date=datetime.date(2024, 9, 16),
                end_date=datetime.date(2024, 9, 16),
                recurrence_days= None,
                is_am=True,
                is_pm=True,
                request_status='Pending',
                apply_date=datetime.date(2024, 9, 30),
                withdrawable_until=datetime.date(2024, 9, 30),
                request_reason="Sick"
            )
        
        wfh_date3 = WFHRequestDates(
                date_id=3,
                request_id=3,
                specific_date=datetime.date(2024, 9, 16),
                staff_id=140008,
                decision_status="Withdrawn",
                is_am=True,
                is_pm=True
            )
        
        db.session.add(wfh_request3)
        db.session.add(wfh_date3)
        db.session.commit()

        response = self.client.get("/api/staff/140008/wfh_office_dates?start_date=2024-09-15&end_date=2024-09-17", content_type='application/json')

        self.assertEqual(response.status_code, 200)        
        self.assertEqual(response.get_json(), {
        'in_office_dates': [
             {'date': '2024-09-15', 'is_am': False, 'is_pm': False}, 
             {'date': '2024-09-16', 'is_am': True, 'is_pm': True}, 
             {'date': '2024-09-17', 'is_am': True, 'is_pm': True}, 
             ], 
         'wfh_dates': [
             {'date_id': 1, 'decision_status': 'Approved', 'is_am': True, 'is_pm': True, 'request_id': 1, 'specific_date': '2024-09-15', 'staff_id': 140008}
             ]})
          