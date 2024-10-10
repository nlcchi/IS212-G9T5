DROP TYPE IF EXISTS request_type CASCADE;
DROP TYPE IF EXISTS request_status CASCADE;
DROP TYPE IF EXISTS decision_status CASCADE;

DROP TABLE IF EXISTS work_from_home_request_dates CASCADE;
DROP TABLE IF EXISTS work_from_home_requests CASCADE;
DROP TABLE IF EXISTS requestdecisions CASCADE;

CREATE TYPE request_type AS ENUM ('Ad-hoc', 'Recurring');
CREATE TYPE request_status AS ENUM ('Pending', 'Approved', 'Rejected', 'Cancelled', 'Withdrawn');
CREATE TYPE decision_status AS ENUM ('Approved', 'Rejected', 'Withdrawn');

CREATE TABLE work_from_home_requests (
    request_id SERIAL PRIMARY KEY,
    staff_id INTEGER NOT NULL,
    manager_id INTEGER NOT NULL,
    request_type request_type NOT NULL,  
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    recurrence_days VARCHAR(20),  
    is_am BOOLEAN NOT NULL,  
    is_pm BOOLEAN NOT NULL,  
    request_status request_status NOT NULL,  
    apply_date DATE NOT NULL,
    withdrawable_until DATE NOT NULL,
    request_reason TEXT,
    FOREIGN KEY (staff_id) REFERENCES employee(staff_id),
    FOREIGN KEY (manager_id) REFERENCES employee(staff_id)
);

CREATE TABLE requestdecisions (
    decision_id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL,
    manager_id INTEGER NOT NULL,
    decision_date DATE NOT NULL,
    decision_status decision_status NOT NULL, 
    decision_notes TEXT,
    FOREIGN KEY (request_id) REFERENCES work_from_home_requests(request_id),
    FOREIGN KEY (manager_id) REFERENCES employee(staff_id)
);

CREATE TABLE work_from_home_request_dates (
    date_id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL,
    specific_date DATE NOT NULL,
    staff_id INTEGER NOT NULL,
    decision_status decision_status NOT NULL, 
    is_am BOOLEAN NOT NULL,  
    is_pm BOOLEAN NOT NULL,  
    FOREIGN KEY (request_id) REFERENCES work_from_home_requests(request_id),
    FOREIGN KEY (staff_id) REFERENCES employee(staff_id),
    FOREIGN KEY (decision_status) REFERENCES requestdecisions(decision_status)
);