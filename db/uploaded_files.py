from pymongo import MongoClient, errors
import gridfs
from fastapi import Request, status, HTTPException
import os
from fastapi.responses import StreamingResponse
import base64
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
    print("Error connecting to MongoDB. Check your connection settings and ensure the MongoDB server is running.")
    exit(1)  # Terminate the program if there is a connection error


def save_file(file_path, file_name, email):
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found.")

        # Open and save the file to GridFS
        with open(file_path, "rb") as file:
            file_id = fs.put(file, filename=file_name, email=email)
            print(f"File '{file_name}' saved with ID: {file_id}")
            return file_id
    except FileNotFoundError as e:
        print(e)
    except PermissionError:
        print(f"Permission denied to read the file: '{file_path}'.")
    except errors.PyMongoError as e:
        print(f"Error working with MongoDB: {e}")


def retrieve_file(file_id):
    try:
        # Retrieve the file from GridFS
        file_data = fs.get(file_id)

        # Extract the filename from metadata
        file_name = file_data.filename

        # Check if a file with the same name already exists
        if os.path.exists(file_name):
            raise FileExistsError(
                f"A file named '{file_name}' already exists.")

        # Save the file to disk with its original name
        with open(file_name, "wb") as output_file:
            output_file.write(file_data.read())
            print(
                f"File with ID: {file_id} retrieved and saved as '{file_name}'")
    except gridfs.errors.NoFile:
        print(f"No file found in GridFS with ID: {file_id}.")
    except FileExistsError as e:
        print(e)
    except PermissionError:
        print(f"Permission denied to write the file: '{file_name}'.")
    except errors.PyMongoError as e:
        print(f"Error working with MongoDB: {e}")

def delete_all_file(email):
    try:
        files = fs.find({"email": email})
        for file in files:
            fs.delete(file._id)  # Используем _id для удаления файла
            print(f"File with ID {file._id} has been deleted successfully.")
        return True
    except errors.PyMongoError as e:
        print(f"Error working with MongoDB: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    
def delete_file(file_id, email):
    file_record = db.fs.files.find_one({"_id": ObjectId(file_id), "email": email})
    
    if not file_record:
        raise HTTPException(status_code=404, detail="The file was not found or you do not have access to this file")
    try:
        # Преобразование file_id в ObjectId
        object_id = ObjectId(file_id)

        # Проверка наличия файла
        file = fs.find_one({"_id": object_id})
        if file is None:
            print(f"No file found in GridFS with ID: {file_id}.")
            return False

        # Удаление файла из GridFS
        fs.delete(object_id)
        print(f"File with ID {file_id} has been deleted successfully.")
        return True
    except gridfs.errors.NoFile:
        print(f"No file found in GridFS with ID: {file_id}.")
        return False
    except errors.PyMongoError as e:
        print(f"Error working with MongoDB: {e}")
        return False
    except Exception as e:
        print(f"Invalid file ID: {e}")
        return False


def userFiles(email: str):
    files = fs.find({"email": email})

    # Создаем список для хранения информации о файлах
    user_files = []

    # Проходим по курсору, чтобы собрать информацию о файлах
    for file in files:
        file_info = {
            "file_id": str(file._id),
            "filename": file.filename,
            "length": file.length,
            "upload_date": file.uploadDate
        }
        user_files.append(file_info)

    # Если файлов не найдено, возвращаем пустой список
    if not user_files:
        return {"files": []}

    return {"files": user_files}


def getFile(file_id: str, email):
    file_record = db.fs.files.find_one({"_id": ObjectId(file_id), "email": email})
    
    if not file_record:
        raise HTTPException(status_code=404, detail="The file was not found or you do not have access to this file")
    # Получаем файл из GridFS
    file_data = fs.get(ObjectId(file_id))
    

    # Создаем генератор для чтения файла по частям (например, по 4KB)
    def iter_file(file_data):
        while True:
            data = file_data.read(4096)  # Чтение по 4KB
            if not data:
                break
            yield data

    # Создаем потоковый ответ с использованием генератора
    response = StreamingResponse(
        iter_file(file_data),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_data.filename}"}
    )
    return response
