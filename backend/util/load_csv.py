import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Employee(Base):
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

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine) 
Session = sessionmaker(bind=engine)

def import_employee_data(csv_file_path):
    """Import employee data from a CSV file into the PostgreSQL database."""
    csv_file_path = os.path.abspath(csv_file_path)
    df = pd.read_csv(csv_file_path)
    print(df.head())

    session = Session()

    for index, row in df.iterrows():
        employee = Employee(
            staff_id=row['Staff_ID'],
            staff_fname=row['Staff_FName'],
            staff_lname=row['Staff_LName'],
            dept=row['Dept'],
            position=row['Position'],
            country=row['Country'],
            email=row['Email'],
            reporting_manager=row['Reporting_Manager'],
            role=row['Role']
        )  
        
        session.add(employee)

    session.commit()
    session.close()  

if __name__ == "__main__":
    import_employee_data('../employeenew.csv')
