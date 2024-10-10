from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *

db = SQLAlchemy()

#Employee Table
class Employee(db.Model):
    __tablename__ = 'employee'

    staff_id = Column(Integer, primary_key=True)
    staff_fname = Column(String, nullable=False)
    staff_lname = Column(String, nullable=False)
    dept = Column(String, nullable=False)
    position = Column(String, nullable=False)
    country = Column(String, nullable=False)
    email = Column(String, nullable=False)
    reporting_manager = Column(Integer, ForeignKey('employee.staff_id'))
    role = Column(Integer, nullable=False)

    def json(self):
        return {
            "staff_id": self.staff_id,
            "staff_fname": self.staff_fname,
            "staff_lname": self.staff_lname,
            "dept": self.dept,
            "position": self.position,
            "country": self.country,
            "email": self.email,
            "reporting_manager": self.reporting_manager,
            "role": self.role
        }
    
# WFHRequests Table 
class WFHRequests(db.Model):
    __tablename__ = 'work_from_home_requests'

    request_id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey('employee.staff_id'), nullable=False)
    manager_id = Column(Integer, ForeignKey('employee.staff_id'), nullable=False)
    request_type = Column(Enum('Ad-hoc', 'Recurring', name='request_type'), nullable=False)  # Ad-hoc or Recurring
    start_date = Column(Date, nullable=False)  
    end_date = Column(Date, nullable=False)    
    recurrence_days = Column(String, nullable=True)  # Only for recurring, stores the day of the week (e.g. 'Monday')
    is_am = Column(Boolean, nullable=False, default=False)  # Is AM selected?
    is_pm = Column(Boolean, nullable=False, default=False)  # Is PM selected?
    request_status = Column(Enum('Pending', 'Approved', 'Rejected', 'Cancelled', 'Withdrawn', name='request_status'), nullable=False)
    apply_date = Column(Date, nullable=False)
    withdrawable_until = Column(Date, nullable=False)
    request_reason = Column(String, nullable=True)

    employee = db.relationship('Employee', foreign_keys=[staff_id])

    def json(self):
        return {
            "request_id": self.request_id,
            "staff_id": self.staff_id,
            "manager_id": self.manager_id,
            "request_type": self.request_type,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date),
            "recurrence_days": self.recurrence_days,  # Day of the week for recurring requests
            "is_am": self.is_am,
            "is_pm": self.is_pm,
            "request_status": self.request_status,
            "apply_date": str(self.apply_date),
            "withdrawable_until": str(self.withdrawable_until),
            "request_reason": self.request_reason
        }

# RequestDecisions Table (Stores the decision made by the manager for the requests)
class RequestDecisions(db.Model):
    __tablename__ = 'requestdecisions'

    decision_id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('work_from_home_requests.request_id'), nullable=False)
    manager_id = Column(Integer, ForeignKey('employee.staff_id'), nullable=False)  # Manager who made the decision
    decision_date = Column(Date, nullable=False)
    decision_status = Column(Enum('Approved', 'Rejected', 'Withdrawn', name='decision_status'), nullable=False)
    decision_notes = Column(Text, nullable=True)

    work_from_home_request = db.relationship('WFHRequests')
    manager = db.relationship('Employee', foreign_keys=[manager_id])

    def json(self):
        return {
            "decision_id": self.decision_id,
            "request_id": self.request_id,
            "manager_id": self.manager_id,
            "decision_date": str(self.decision_date),
            "decision_status": self.decision_status,
            "decision_notes": self.decision_notes
        }
    
# WFHRequestDates Table (Stores the specific dates for both Ad-hoc and Recurring requests)
class WFHRequestDates(db.Model):
    __tablename__ = 'work_from_home_request_dates'

    date_id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('work_from_home_requests.request_id'), nullable=False)
    specific_date = Column(Date, nullable=False)  # The specific work-from-home date
    staff_id = Column(Integer, ForeignKey('employee.staff_id'), nullable=False)
    decision_status = Column(Enum('Approved', 'Rejected', 'Withdrawn', name='decision_status'), ForeignKey('requestdecisions.decision_status'), nullable=False)
    is_am = Column(Boolean, nullable=False, default=False)  # Is AM selected for this date?
    is_pm = Column(Boolean, nullable=False, default=False)  # Is PM selected for this date?

    work_from_home_request = db.relationship('WFHRequests')
    employee = db.relationship('Employee')
    request_decisions = db.relationship('RequestDecisions')

    def json(self):
        return {
            "date_id": self.date_id,
            "request_id": self.request_id,
            "specific_date": str(self.specific_date),
            "staff_id": self.staff_id,
            "decision_status": self.decision_status,
            "is_am": self.is_am,
            "is_pm": self.is_pm
        }