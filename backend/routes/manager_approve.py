from flask import Blueprint, jsonify, request
from models import *
from util.wfh_requests import *
from util.request_decisions import *
from util.wfh_dates import *
from sqlalchemy import and_

approve = Blueprint('approve', __name__)

@approve.route("/api/approve", methods=['POST'])
def manager_approve_adhoc():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON or no data provided"}), 400

    try:
        request_id = data["request_id"]
        req = get_request(request_id)
        if not req:
            return jsonify({"error": "Request not found"}), 404

        # if data["request_type"] != 'Ad-hoc':
        #     return jsonify({"error": "Invalid request type"}), 400
        
        staff_id = req["staff_id"]
        employee = Employee.query.filter_by(staff_id=staff_id).first()
        if not employee: 
            return jsonify({"error": f"Employee with staff_id {staff_id} not found"}), 404
        
        reporting_manager_id = employee.reporting_manager
        if not reporting_manager_id:
            return jsonify({"error": f"Reporting manager for employee {staff_id} not found"}), 404
        
        employees_under_same_manager = Employee.query.filter_by(reporting_manager=reporting_manager_id).all()
        total_employees = len(employees_under_same_manager)
        
        start_date = req["start_date"]

        approved_adhoc_requests = WFHRequests.query.filter(
            and_(
                WFHRequests.staff_id.in_([emp.staff_id for emp in employees_under_same_manager]),
                WFHRequests.request_type == 'Ad-hoc',
                WFHRequests.start_date == start_date,
                WFHRequests.request_status == 'Approved'
            )
        ).count()

        if total_employees > 0:
            ratio = (approved_adhoc_requests+1) / total_employees
        else:
            ratio = 0

        # print(ratio)

        if ratio > 0.5:
            return jsonify({"error": "Exceed 0.5 rule limit"}), 422
        

        # print(f"Calling update_request with request_id: {request_id}")
        new_req = update_request(request_id, {"request_status": data.get("decision_status")})
        # print(f"update_request returned: {new_req}")
        if new_req is None:
            return jsonify({"error": "Request not found"}), 404

        # print(f"Calling create_request_decision with data: {data}")
        decision = create_request_decision(data)
        # print(f"create_request_decision returned: {decision}")
        if "error" in decision:
            return jsonify(decision), 500
        
        wfh_date = add_approved_date(new_req['new_request'], decision["decision"]["decision_status"])
        if "error" in wfh_date:
            return jsonify(wfh_date), 500 
        
        return jsonify({
            "message": "Request updated and manager's decision stored successfully",
            "request": new_req["new_request"],
            "decision": decision["decision"],
            "wfh_date": wfh_date["wfh_date"]
        }), 201

    except Exception as e:
        db.session.rollback() 
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
