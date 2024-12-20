import unittest
from unittest.mock import patch
from datetime import date
import flask_testing
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

        db.session.add(employee)
        db.session.add(manager)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

@patch('routes.cron.date')
class TestCronJob(TestApp):
    def test_auto_reject_more_than_2mths(self, mock_date):
        mock_date.today.return_value = date(2024, 12, 12)
        wfh_request = WFHRequests(
            request_id="1",
            staff_id=140008,
            manager_id=140001,
            specific_date=date(2024, 9, 15),
            is_am=True,
            is_pm=True,
            request_status='Pending',
            apply_date=date(2024, 9, 12),
            request_reason='Personal matters'
        )

        db.session.add(wfh_request)
        db.session.commit()

        response = self.client.get("/api/auto-reject")

        pending = WFHRequests.query.filter_by(request_status="Pending").all()
        cancelled = WFHRequests.query.filter_by(request_status="Cancelled").all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(cancelled[0].json(), {
            'request_id': "1",
            'staff_id': 140008,
            'manager_id': 140001,
            'specific_date': "2024-09-15",
            'is_am': True,
            'is_pm': True,
            "request_status": "Cancelled",
            'apply_date': "2024-09-12",
            'request_reason': "Auto-rejected by system"
            })
        self.assertEqual(pending, [])

    def test_auto_reject_less_than_2mths(self, mock_date):
        mock_date.today.return_value = date(2024, 12, 12)
        wfh_request = WFHRequests(
            request_id="1",
            staff_id=140008,
            manager_id=140001,
            specific_date=date(2024, 9, 15),
            is_am=True,
            is_pm=True,
            request_status='Pending',
            apply_date=date(2024, 11, 12),
            request_reason='Personal matters'
        )

        db.session.add(wfh_request)
        db.session.commit()

        response = self.client.get("/api/auto-reject")

        pending = WFHRequests.query.filter_by(request_status="Pending").all()
        cancelled = WFHRequests.query.filter_by(request_status="Cancelled").all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(pending[0].json(), {
            'request_id': "1",
            'staff_id': 140008,
            'manager_id': 140001,
            'specific_date': "2024-09-15",
            'is_am': True,
            'is_pm': True,
            "request_status": "Pending",
            'apply_date': "2024-11-12",
            'request_reason': "Personal matters"
            })
        self.assertEqual(cancelled, [])

    def test_auto_reject_boundary(self, mock_date):
        mock_date.today.return_value = date(2024, 12, 12)
        wfh_request = WFHRequests(
            request_id="1",
            staff_id=140008,
            manager_id=140001,
            specific_date=date(2024, 9, 15),
            is_am=True,
            is_pm=True,
            request_status='Pending',
            apply_date=date(2024, 10, 12),
            request_reason='Personal matters'
        )

        db.session.add(wfh_request)
        db.session.commit()

        response = self.client.get("/api/auto-reject")

        pending = WFHRequests.query.filter_by(request_status="Pending").all()
        cancelled = WFHRequests.query.filter_by(request_status="Cancelled").all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(pending[0].json(), {
            'request_id': "1",
            'staff_id': 140008,
            'manager_id': 140001,
            'specific_date': "2024-09-15",
            'is_am': True,
            'is_pm': True,
            "request_status": "Pending",
            'apply_date': "2024-10-12",
            'request_reason': "Personal matters"
            })
        self.assertEqual(cancelled, [])

    @patch('routes.cron.WFHRequests.query.filter')
    @patch('routes.cron.db.session.rollback')
    def auto_reject_exception(self, mock_filter, mock_rollback):
        mock_filter.side_effect = Exception("Database connection error")

        with app.test_client() as client:
            response = client.get('/api/auto-reject')

        # Assert that the rollback was called
        mock_rollback.assert_called_once()

        # Assert the response
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Database connection error", response.data)


if __name__ == '__main__':
    unittest.main()
