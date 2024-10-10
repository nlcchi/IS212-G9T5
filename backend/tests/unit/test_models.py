import unittest
from unittest.mock import patch
from models import *
import datetime

class TestEmployee(unittest.TestCase):
    def test_json(self):
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
        
        self.assertEqual(new_employee.json(), {
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

class TestWFHRequests(unittest.TestCase):
    def test_json(self):
        req = WFHRequests(
            staff_id=140008,
            manager_id=140001,
            request_type="Ad-hoc",  
            start_date=datetime.date(2024, 9, 15),  
            end_date=datetime.date(2024, 9, 15),
            recurrence_days="",
            is_am=True,
            is_pm=True, 
            request_status= "Pending",  
            apply_date=datetime.date(2024, 9, 30),
            withdrawable_until=datetime.date(2024, 9, 29),
            request_reason="Sick"
            )

        self.assertEqual(req.json(), {
            'request_id': None,
            'staff_id': 140008,
            'manager_id': 140001,
            'request_type': 'Ad-hoc',
            'start_date': "2024-09-15",
            'end_date': "2024-09-15",
            'recurrence_days': '',
            'is_am': True,
            'is_pm': True,
            "request_status": "Pending",
            'apply_date': "2024-09-30",
            'withdrawable_until': "2024-09-29",
            'request_reason': "Sick"
        })

class TestWFHRequestDates(unittest.TestCase):
    def test_json(self):
        date = WFHRequestDates(
            request_id=1, 
            specific_date=datetime.date(2024, 9, 15),
            staff_id=140008, 
            decision_status="Approved",
            is_am=True,
            is_pm=True
            )
        
        self.assertEqual(date.json(), {
            "date_id": None,
            "request_id": 1,
            "specific_date": "2024-09-15",
            "staff_id": 140008,
            "decision_status": "Approved",
            "is_am": True,
            "is_pm": True
        })

@patch('util.request_decisions.datetime')
class TestRequestDecisions(unittest.TestCase):
    def test_json(self, mock_datetime):
        mock_datetime.today.return_value = datetime.date(2024, 12, 12)

        decision = RequestDecisions(
            request_id=1,
            manager_id=140001,
            decision_status="Approved",
            decision_date=mock_datetime.today(),
            decision_notes="Ok"
            )
        
        self.assertEqual(decision.decision_date, datetime.date(2024, 12, 12))
        self.assertEqual(decision.json(), {
            "decision_id": None,
            "request_id": 1,
            "manager_id": 140001,
            "decision_date": "2024-12-12",
            "decision_status": "Approved",
            "decision_notes": "Ok"
        })


if __name__ == "__main__":
    unittest.main()
