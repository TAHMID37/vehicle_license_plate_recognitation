from fastapi import FastAPI, UploadFile, Form, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import process_vehicle
import os
from fastapi.concurrency import run_in_threadpool

app = FastAPI()


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