from pymongo import MongoClient, errors
import gridfs
from fastapi import Request, status, HTTPException
import os
from fastapi.responses import StreamingResponse
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
try:
    mongo_uri = os.getenv("MONGO_URL")
    client = MongoClient(mongo_uri)
    db = client["filedb"]
    fs = gridfs.GridFS(db)
except errors.ConnectionError:
    raise HTTPException(status_code=503, detail="Service unavailable. Unable to connect to MongoDB.")

def save_file(file_path, file_name, email):
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File '{file_path}' not found.")

        # Open and save the file to GridFS
        with open(file_path, "rb") as file:
            file_id = fs.put(file, filename=file_name, email=email)
            print(f"File '{file_name}' saved with ID: {file_id}")
            return file_id
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{file_path}' not found.")
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied to read the file: '{file_path}'.")
    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Error working with MongoDB.")

def retrieve_file(file_id):
    try:
        # Retrieve the file from GridFS
        file_data = fs.get(ObjectId(file_id))
        file_name = file_data.filename  # Extract the filename

        # Check if a file with the same name already exists
        if os.path.exists(file_name):
            raise HTTPException(status_code=409, detail=f"A file named '{file_name}' already exists.")

        # Save the file to disk with its original name
        with open(file_name, "wb") as output_file:
            output_file.write(file_data.read())
            print(f"File with ID: {file_id} retrieved and saved as '{file_name}'")
    except gridfs.errors.NoFile:
        raise HTTPException(status_code=404, detail=f"No file found in GridFS with ID: {file_id}.")
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied to write the file: '{file_name}'.")
    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Error working with MongoDB.")

def delete_all_file(email):
    try:
        files = fs.find({"email": email})
        for file in files:
            fs.delete(file._id)  # Delete the file using _id
            print(f"File with ID {file._id} has been deleted successfully.")
        return True
    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Error working with MongoDB.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

def delete_file(file_id, email):
    file_record = db.fs.files.find_one({"_id": ObjectId(file_id), "email": email})
    
    if not file_record:
        raise HTTPException(status_code=404, detail="The file was not found or you do not have access to this file.")
    try:
        object_id = ObjectId(file_id)

        # Check if the file exists
        file = fs.find_one({"_id": object_id})
        if file is None:
            raise HTTPException(status_code=404, detail=f"No file found in GridFS with ID: {file_id}.")

        # Delete the file from GridFS
        fs.delete(object_id)
        print(f"File with ID {file_id} has been deleted successfully.")
        return True
    except gridfs.errors.NoFile:
        raise HTTPException(status_code=404, detail=f"No file found in GridFS with ID: {file_id}.")
    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Error working with MongoDB.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid file ID: {str(e)}")

def userFiles(email: str):
    files = fs.find({"email": email})

    # Create a list to store file information
    user_files = []
    for file in files:
        file_info = {
            "file_id": str(file._id),
            "filename": file.filename,
            "length": file.length,
            "upload_date": file.uploadDate
        }
        user_files.append(file_info)

    return {"files": user_files} if user_files else {"files": []}  # Return files or empty list

def getFile(file_id: str, email):
    file_record = db.fs.files.find_one({"_id": ObjectId(file_id), "email": email})
    
    if not file_record:
        raise HTTPException(status_code=404, detail="The file was not found or you do not have access to this file.")

    # Get the file from GridFS
    file_data = fs.get(ObjectId(file_id))

    # Create a generator to read the file in chunks
    def iter_file(file_data):
        while True:
            data = file_data.read(4096)  # Read in 4KB chunks
            if not data:
                break
            yield data

    # Create a streaming response using the generator
    response = StreamingResponse(
        iter_file(file_data),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_data.filename}"}
    )
    return response
