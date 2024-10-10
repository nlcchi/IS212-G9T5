import unittest
import flask_testing
from server import app, db
from models import Employee
from util.employee import get_all_department_teams

class TestApp(flask_testing.TestCase):
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    app.config['TESTING'] = True

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        # Add test employees to the database
        self.add_test_employees()

    def add_test_employees(self):
        # Adding employees to test the function
        employee_1 = Employee(
            staff_id=140001,
            staff_fname="Alice",
            staff_lname="Smith",
            dept="Sales",
            position="Sales Manager",
            country="Singapore",
            email="alice.smith@example.com",
            reporting_manager=None,
            role=1
        )
        employee_2 = Employee(
            staff_id=140002,
            staff_fname="Bob",
            staff_lname="Johnson",
            dept="Sales",
            position="Sales Associate",
            country="Singapore",
            email="bob.johnson@example.com",
            reporting_manager=140001,
            role=2
        )
        employee_3 = Employee(
            staff_id=140003,
            staff_fname="Charlie",
            staff_lname="Brown",
            dept="HR",
            position="HR Manager",
            country="Singapore",
            email="charlie.brown@example.com",
            reporting_manager=None,
            role=1
        )
        db.session.add_all([employee_1, employee_2, employee_3])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestGetAllDepartmentTeams(TestApp):
    def test_get_all_department_teams(self):
        expected_result = {
    "Sales": {
        140001: [  # Reporting manager ID for Bob Johnson
            {
                "staff_id": 140002,
                "staff_fname": "Bob",
                "staff_lname": "Johnson",
                "dept": "Sales",
                "position": "Sales Associate",
                "country": "Singapore",
                "email": "bob.johnson@example.com",
                "reporting_manager": 140001,
                "role": 2,
            }
        ]
    },
    "HR": {
        # Charlie Brown will not be included because his reporting_manager is None
    }
}

        result = get_all_department_teams()
        print("Actual result:", result)
        print("Expected result:", expected_result)
        self.assertEqual(result, expected_result)




if __name__ == '__main__':
    unittest.main()
