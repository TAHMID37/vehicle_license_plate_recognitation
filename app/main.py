from fastapi import FastAPI, UploadFile, Form, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import process_vehicle
import os
from fastapi.concurrency import run_in_threadpool
from app.utils import detect_and_extract_lp_text
from app.models import VehicleRegistration,VehicleLog
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/process/")
async def process_vehicle_endpoint(
    file: UploadFile, state: str = Form(...), db: Session = Depends(get_db)
):
    # Create the uploads folder if it does not exist
    uploads_dir = "./uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    # Save the uploaded file to the uploads folder
    save_path = os.path.join(uploads_dir, file.filename)
    try:
        # Read the file content once and save it
        file_content = await file.read()
        with open(save_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        return {"error": f"Failed to save uploaded file: {e}"}

    # Process the vehicle (entry/exit)
    try:
        # Since process_vehicle is synchronous, run it in a thread pool
        result = await run_in_threadpool(process_vehicle, save_path, state, db)
        return result
    except Exception as e:
        return {"error": f"Failed to process vehicle: {str(e)}"}
    
    
    
#Registration Vechicle


# Function to register a vehicle
def register_vehicle_in_db(db: Session, license_plate: str):
    existing_vehicle = db.query(VehicleRegistration).filter_by(license_plate=license_plate).first()
    if existing_vehicle:
        return {"message": f"Vehicle {license_plate} is already registered"}
    new_vehicle = VehicleRegistration(license_plate=license_plate)
    db.add(new_vehicle)
    db.commit()
    return {"message": f"Vehicle {license_plate} registered successfully"}

# 1. Endpoint for registering vehicles from a folder

folder_path = "./image"

@app.post("/register-from-folder/")
def register_vehicles_from_folder(db: Session = Depends(get_db)):
    if not os.path.exists(folder_path):
        return {"error": "Folder path does not exist"}

    registered_vehicles = []
    errors = []

    # Process all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                area, number = detect_and_extract_lp_text(file_path)
                license_plate = area + " " + number
                if not license_plate.strip():
                    errors.append({"file": filename, "error": "License plate not detected"})
                    continue
                # Register the vehicle in the database
                result = register_vehicle_in_db(db, license_plate)
                registered_vehicles.append(result)
            except Exception as e:
                errors.append({"file": filename, "error": str(e)})

    return {
       "message": "Vehicle registration completed",
    }

# 2. Endpoint for registering vehicles from uploaded images
@app.post("/register-from-images/")
async def register_vehicles_from_images(files: List[UploadFile], db: Session = Depends(get_db)):
    uploads_dir = "./image"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    registered_vehicles = []
    errors = []

    # Process each uploaded file
    for file in files:
        save_path = os.path.join(uploads_dir, file.filename)
        try:
            # Save the uploaded file
            file_content = await file.read()
            with open(save_path, "wb") as f:
                f.write(file_content)
            
            # Detect and register license plate
            area, number = detect_and_extract_lp_text(save_path)
            license_plate = area + " " + number
            if not license_plate.strip():
                errors.append({"file": file.filename, "error": "License plate not detected"})
                continue
            
            # Check if the license plate is already registered
            existing_vehicle = db.query(VehicleRegistration).filter_by(license_plate=license_plate).first()
            if existing_vehicle:
                errors.append({"file": file.filename, "error": f"Vehicle {license_plate} is already registered"})
                continue

            result = register_vehicle_in_db(db, license_plate)
            registered_vehicles.append(result)
        except Exception as e:
            errors.append({"file": file.filename, "error": str(e)})

    return {
        "registered_vehicles": registered_vehicles,
        "errors": errors,
    }
    
    
@app.get("/registered-vehicles/")
async def get_registered_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(VehicleRegistration).all()
    return vehicles

@app.get("/registered-vehicles/{license_plate}")
async def get_registered_vehicle(license_plate: str, db: Session = Depends(get_db)):
    vehicle = db.query(VehicleRegistration).filter_by(license_plate=license_plate).first()
    if not vehicle:
        return {"error": f"Vehicle {license_plate} not found"}
    return vehicle

@app.delete("/registered-vehicles/{id}")
async def delete_registered_vehicle(id: int, db: Session = Depends(get_db)):
    vehicle = db.query(VehicleRegistration).filter_by(id=id).first()
    license_plate = vehicle.license_plate
    if not vehicle:
        return {"error": f"Vehicle with License Plate {license_plate} not found"}
    db.delete(vehicle)
    db.commit()
    return {"message": f"Vehicle with License Plate {license_plate} deleted successfully"}

@app.get("/vehicles_log/")
async def get_vehicles_log(db: Session = Depends(get_db)):
    vehicles = db.query(VehicleLog).all()
    return vehicles
    