from flask import Blueprint, request, jsonify
from datetime import date
from models import *

withdraw = Blueprint('withdraw', __name__)

@withdraw.route("/api/withdraw", methods=['POST'])
def staff_withdraw():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON or no data provided"}), 400
    
    required_fields = ["request_id", "reason", "specific_date"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing '{field}' in request"}), 400
    
    response = WFHRequests.query.filter(WFHRequests.request_id == data.get("request_id")).one()
    req = response.json()

    if req["request_status"] != "Approved":
        return jsonify({"error": "Request has not been approved."}), 400

    specific_date = date.fromisoformat(data.get("specific_date"))

    try: 
        new_request = WFHRequests(
                staff_id=req['staff_id'],
                manager_id=req['manager_id'],
                request_type=req['request_type'],  
                start_date=specific_date,  
                end_date=specific_date,
                recurrence_days=None,
                is_am=req['is_am'],
                is_pm=req['is_pm'], 
                request_status= "Pending_Withdraw",  
                apply_date=date.today(),
                withdraw_reason=data.get("reason"),
                request_reason=req['request_reason']
            )
        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            "message": "Withdraw request successfully created.",
            "request": new_request.json()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500