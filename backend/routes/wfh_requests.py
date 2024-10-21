from flask import Blueprint, jsonify, request
from models import *
from datetime import datetime, timedelta

dates = Blueprint('dates', __name__)

##### WFHREQUESTDATES TABLE #####
# Get all wfh dates for a certain staff id
# GET /api/staff/1/all_wfh_dates
# [
#   {
#     "request_id": 1,
#     "staff_id": 1,
#     "manager_id": 2,
#     "specific_date": "2024-09-24",
#     "is_am": true,
#     "is_pm": true
#     "request_status": "Approved",
#     "apply_date": "2024-09-01",
#     "request_reason": "Sick"
#   }
# ]
@dates.route("/api/staff/<int:staff_id>/all_wfh_dates", methods=["GET"])
def get_staff_wfh_dates(staff_id):

    wfh_requests = WFHRequests.query.filter_by(staff_id=staff_id).all()

    if not wfh_requests:
        return jsonify({"message": "No WFH dates found for this staff member"}), 404

    return jsonify([date_request.json() for date_request in wfh_requests])

# Get all approved wfh dates for a certain staff id in a certain date range
#GET /api/staff/1/wfh_requests?start_date=2024-09-01&end_date=2024-09-30
# [
#   {
#     "request_id": 1,
#     "staff_id": 1,
#     "manager_id": 2,
#     "specific_date": "2024-09-24",
#     "is_am": true,
#     "is_pm": true
#     "request_status": "Approved",
#     "apply_date": "2024-09-01",
#     "request_reason": "Sick"
#   }
# ]


@dates.route("/api/staff/<int:staff_id>/wfh_requests", methods=["GET"])
def get_staff_wfh_requests_in_range(staff_id):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify({"error": "Please provide both start_date and end_date"}), 400

    # Query WFH requests within the date range for the given staff_id
    wfh_requests = WFHRequests.query.filter(
        WFHRequests.staff_id == staff_id,
        WFHRequests.specific_date >= start_date,
        WFHRequests.specific_date <= end_date,
        WFHRequests.request_status == "Approved"  
    ).all()

    if not wfh_requests:
        return jsonify({"message": "No WFH requests found for this staff member in the given date range"}), 404

    return jsonify([date_request.json() for date_request in wfh_requests])
