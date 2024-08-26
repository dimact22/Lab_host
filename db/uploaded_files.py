from pymongo import MongoClient, errors
import gridfs
import os
from fastapi.responses import StreamingResponse
import base64
from bson import ObjectId

# Connect to MongoDB
try:
    client = MongoClient(
        "mongodb+srv://ReDiUser:1234rtyu@cluster0.tnsqcvc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    client = MongoClient(
        "mongodb+srv://ReDiUser:1234rtyu@cluster0.tnsqcvc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["filedb"]
    fs = gridfs.GridFS(db)
except errors.ConnectionError:
    print("Error connecting to MongoDB. Check your connection settings and ensure the MongoDB server is running.")
    exit(1)  # Terminate the program if there is a connection error


def save_file(file_path, file_name, name):
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found.")

        # Open and save the file to GridFS
        with open(file_path, "rb") as file:
            file_id = fs.put(file, filename=file_name, user_name=name)
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


def delete_file(file_id):
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


def userFiles(name: str):

    files = fs.find({"user_name": name})

    # Если файлов не найдено, возвращаем пустой список
    if files.count() == 0:
        return {"files": []}

    # Создаем список для хранения информации о файлах
    user_files = []
    for file in files:
        file_info = {
            "file_id": str(file._id),
            "filename": file.filename,
            "length": file.length,
            "upload_date": file.uploadDate,
            "md5": file.md5,
            "chunkSize": file.chunkSize
        }
        user_files.append(file_info)

    return {"files": user_files}


def getFile(file_id: str):
    # Получаем файл из GridFS
    file_data = fs.get(ObjectId(file_id))

    # Создаем потоковый ответ
    response = StreamingResponse(
        file_data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_data.filename}"}
    )
    return response
