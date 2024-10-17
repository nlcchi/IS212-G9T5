from models import *
from datetime import datetime

def add_approved_date(request, decision):
    try: 
        new_date = WFHRequestDates(
            request_id=request["request_id"],
            specific_date = datetime.strptime(request.get("start_date"), '%Y-%m-%d').date(),
            staff_id=request["staff_id"],
            decision_status = decision,
            is_am=request["is_am"],
            is_pm=request["is_pm"]
            )
        
        db.session.add(new_date)
        db.session.commit()

        return {"message": "WFH date successfully added!", "wfh_date": new_date.json()}

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}
    
def get_date(date_id):
    date = WFHRequestDates.query.filter_by(date_id=date_id).first()
    if not date:
        return None
    return date.json()

def update_date(date_id, data):
    date = get_date(date_id)
    if not date:
        return None
    
    if 'request_id' in data:
        date["request_id"] = data['request_id']
    if 'specific_date' in data:
        date["specific_date"] = data['specific_date']
    if 'decision_status' in data:
        date["decision_status"] = data['decision_status']
    if 'staff_id' in data:
        date["staff_id"] = data['staff_id']
    if 'is_am' in data:
        date["is_am"] = data['is_am']
    if 'is_pm' in data:
        date["is_pm"] = data['is_pm']

    db.session.commit()

    return {"message": "WFH Date updated", "new_date": date}
