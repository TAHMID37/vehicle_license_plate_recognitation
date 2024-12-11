# from datetime import datetime
# from sqlalchemy.orm import Session
# from app.models import VehicleLog
# from app.utils import detect_and_extract_lp_text
# from sqlalchemy.sql import text

# # Function to process entry or exit
# def process_vehicle(image_path: str, state: str, db: Session):
#     # Extract license plate text using your OCR function
#     area,number = detect_and_extract_lp_text(image_path)
#     license_plate = area + " "+ number 

#     if not license_plate:
#         return {"error": "License plate could not be recognized"}

#     if state == "enter":
#         # Check if vehicle is already inside
#         existing_vehicle = db.execute(
#             text("SELECT * FROM vehicle_logs WHERE license_plate=:plate AND is_active=True"),
#             {"plate": license_plate}
#         ).fetchone()  # Fetch a single row

#         if existing_vehicle:  # Check if any record exists
#             return {"error": "Vehicle is already inside"}

#         # Add entry log
#         new_log = VehicleLog(license_plate=license_plate)
#         db.add(new_log)
#         db.commit()  # Synchronous commit
#         return {"message": f"Vehicle {license_plate} entered at {new_log.entry_time}"}

#     elif state == "exit":
#         # Find the vehicle in active logs
#         log = db.execute(
#             text("SELECT * FROM vehicle_logs WHERE license_plate=:plate AND is_active=True"),
#             {"plate": license_plate}
#         ).fetchone()  # Fetch a single row

#         if not log:  # If no active log is found
#             return {"error": "Vehicle is not found in the parking lot"}

#         # Calculate duration and charge
#         exit_time = datetime.utcnow()
#         entry_time = log.entry_time  # Adjust this based on how you retrieve `entry_time`
#         duration_hours = (exit_time - entry_time).total_seconds() / 3600
#         charged_amount = duration_hours * 10  # Example: $10 per hour

#         # Update the log record (you need to find the ORM instance and update it)
#         db.execute(
#             text("""
#                 UPDATE vehicle_logs
#                 SET exit_time = :exit_time, charged_amount = :charged_amount, is_active = False
#                 WHERE id = :log_id
#             """),
#             {
#                 "exit_time": exit_time,
#                 "charged_amount": charged_amount,
#                 "log_id": log.id,
#             }
#         )
#         db.commit()  # Synchronous commit

#         return {
#             "message": f"Vehicle {license_plate} exited.",
#             "duration_hours": round(duration_hours, 2),
#             "charged_amount": round(charged_amount, 2),
#         }

#     return {"error": "Invalid state. Use 'enter' or 'exit'."}
# from datetime import datetime
# from sqlalchemy.orm import Session
# from sqlalchemy.sql import text
# from app.models import VehicleLog
# from app.utils import detect_and_extract_lp_text

# def process_vehicle(image_path: str, state: str, db: Session):
#     # Extract license plate text using your OCR function
#     area, number = detect_and_extract_lp_text(image_path)
#     license_plate = area + " " + number 

#     if not license_plate:
#         return {"error": "License plate could not be recognized"}

#     if state == "enter":
#         # Check if vehicle is already inside
#         result = db.execute(
#             text("SELECT * FROM vehicle_logs WHERE license_plate=:plate AND is_active=True"),
#             {"plate": license_plate}
#         )
#         existing_vehicle = result.fetchone()  # Fetch a single row (no await required)

#         if existing_vehicle:  # Check if any record exists
#             return {"error": "Vehicle is already inside"}

#         # Add entry log
#         new_log = VehicleLog(license_plate=license_plate)
#         db.add(new_log)
#         db.commit()  # Synchronous commit
#         return {"message": f"Vehicle {license_plate} entered at {new_log.entry_time}"}

#     elif state == "exit":
#         # Find the vehicle in active logs
#         result = db.execute(
#             text("SELECT * FROM vehicle_logs WHERE license_plate=:plate AND is_active=True"),
#             {"plate": license_plate}
#         )
#         log = result.fetchone()  # Fetch a single row (no await required)

#         if not log:  # If no active log is found
#             return {"error": "Vehicle is not found in the parking lot"}

#         # Calculate duration and charge
#         exit_time = datetime.utcnow()
#         entry_time = log.entry_time  # Adjust this based on how you retrieve `entry_time`
#         duration_hours = (exit_time - entry_time).total_seconds() / 3600
#         charged_amount = duration_hours * 10  # Example: $10 per hour

#         # Update the log record
#         db.execute(
#             text("""
#                 UPDATE vehicle_logs
#                 SET exit_time = :exit_time, charged_amount = :charged_amount, is_active = False
#                 WHERE id = :log_id
#             """),
#             {
#                 "exit_time": exit_time,
#                 "charged_amount": charged_amount,
#                 "log_id": log.id,
#             }
#         )
#         db.commit()  # Synchronous commit

#         return {
#             "message": f"Vehicle {license_plate} exited.",
#             "duration_hours": round(duration_hours, 2),
#             "charged_amount": round(charged_amount, 2),
#         }

#     return {"error": "Invalid state. Use 'enter' or 'exit'."}

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.models import VehicleLog, VehicleRegistration
from app.utils import detect_and_extract_lp_text

def process_vehicle(image_path: str, state: str, db: Session):
    # Extract license plate text using your OCR function
    area, number = detect_and_extract_lp_text(image_path)
    license_plate = area + " " + number 

    if not license_plate:
        return {"error": "License plate could not be recognized"}

    # Check if the vehicle is registered
    registered_vehicle = db.query(VehicleRegistration).filter_by(license_plate=license_plate).first()
    if not registered_vehicle:
        return {"message": "This vehicle is not registered for the parking. Please complete registration first."}

    if state == "enter":
        # Check if vehicle is already inside
        result = db.execute(
            text("SELECT * FROM vehicle_logs WHERE license_plate=:plate AND is_active=True"),
            {"plate": license_plate}
        )
        existing_vehicle = result.fetchone()  # Fetch a single row (no await required)

        if existing_vehicle:  # Check if any record exists
            return {"message": "Vehicle is already inside"}

        # Add entry log
        new_log = VehicleLog(license_plate=license_plate)
        db.add(new_log)
        db.commit()  # Synchronous commit
        return {"message": f"Vehicle {license_plate} entered at {new_log.entry_time}"}

    elif state == "exit":
        # Find the vehicle in active logs
        result = db.execute(
            text("SELECT * FROM vehicle_logs WHERE license_plate=:plate AND is_active=True"),
            {"plate": license_plate}
        )
        log = result.fetchone()  # Fetch a single row (no await required)

        if not log:  # If no active log is found
            return {"message": "Vehicle is not found in the parking lot"}

        # Calculate duration and charge
        exit_time = datetime.utcnow()
        entry_time = log.entry_time  # Adjust this based on how you retrieve `entry_time`
        duration_hours = (exit_time - entry_time).total_seconds() / 3600
        charged_amount = duration_hours * 1000  # Example: 1000 Taka per hour

        # Update the log record
        db.execute(
            text("""
                UPDATE vehicle_logs
                SET exit_time = :exit_time, charged_amount = :charged_amount, is_active = False
                WHERE id = :log_id
            """),
            {
                "exit_time": exit_time,
                "charged_amount": charged_amount,
                "log_id": log.id,
            }
        )
        db.commit()  # Synchronous commit

        return {
            "message": f"Vehicle {license_plate} exited.",
            "duration_hours": round(duration_hours, 2),
            "charged_amount": round(charged_amount, 2),
        }

    return {"error": "Invalid state. Use 'enter' or 'exit'."}


