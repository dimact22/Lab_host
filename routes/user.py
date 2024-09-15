from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
import shutil
import os
import gridfs
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi.responses import FileResponse
from functions.pdf_creations import pdf_creations
from fastapi.templating import Jinja2Templates
from db.models import users_serializer
from schemas.user import User, UserLogin, DeleteUser, ChangeUser, PdfFile
from schemas.info_save import Info
from schemas.contact import ContactForm
from config.db import collection, db, infos, files
from db.hash import Hash
from jose import jwt
from utilities.helper import remove_field_document
from middelware.auth import auth_middleware, verify_admin_token, auth_middleware_email_return
import os
import json
from db.uploaded_files import save_file, retrieve_file, delete_file, userFiles, getFile, delete_all_file
from dotenv import load_dotenv
load_dotenv()

user = APIRouter(prefix="/user", tags=['user'])



@user.post("/message")
async def message_user(contact: ContactForm):
    """
        Sending messages from the user

        Accepts data from the contact form and sends it to a corporative email. If errors arise when sending
        Email, Returns HTTP 400 Error.

        - ** email **: email user sending a message.
        - ** message **: Message from the user.
    """

    sender_email = contact.email
    receiver_email = os.getenv(
        'Receiver_email')
    subject = f"Message from user {contact.email}"
    message_body = contact.message
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = os.getenv('Smtp_username')
    smtp_password = os.getenv('Smtp_password')

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message_body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        return {"status": "Ok", "detail": 'Email sent successfully!'}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    finally:
        server.quit()


@user.post("/uploadfile/")
async def create_upload_file(file: UploadFile, email=Depends(auth_middleware_email_return)):
    """
    Upload a file

    Uploads a file to the server and processes it. The file is temporarily saved on the server, processed, saved in database with user email from jwt token, and then removed.

    - **file**: The file to be uploaded.
    """
    upload_folder = "uploaded_files"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    with open(f"uploaded_files/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_id = save_file(f"uploaded_files/{file.filename}", file.filename, email)
    os.remove(f"uploaded_files/{file.filename}")
    return {"filename": file.filename}


@user.delete("/delete_file/{file_id}")
async def delete_file_api(file_id: str, email=Depends(auth_middleware_email_return)):
    """
    Delete a file

    Deletes a file from the server by its ID. If no file is found with the provided ID, returns HTTP 404 error. The file can delete only user with email that file belongs to.

    - **file_id**: The ID of the file to be deleted.
    """
    if delete_file(file_id, email):
        return {"message": f"File with ID {file_id} has been deleted successfully."}
    else:
        raise HTTPException(
            status_code=404, detail=f"No file found with ID {file_id}.")


@user.get("/user_files")
async def get_user_files(email=Depends(auth_middleware_email_return)):
    """
    Get user files

    Retrieves a list of files uploaded by the authenticated user(email from jwt token). If an error occurs during retrieval, returns HTTP 500 error.
    """
    try:
        return userFiles(email)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving files: {e}")


@user.get("/file/{file_id}")
def get_file(file_id: str, email=Depends(auth_middleware_email_return)):
    """
    Retrieve a file

    Retrieves a file by its ID for the authenticated user. If the file is not found, returns HTTP 404 error. Get the file can only user with email that file belong to.

    - **file_id**: The ID of the file to be retrieved.
    """
    try:
        return getFile(file_id, email)
    except gridfs.errors.NoFile:
        raise HTTPException(status_code=404, detail="File not found")

@user.post("/register")
async def create_user(user: User):
    """
    Register a new user

    Creates a new user account with a hashed password. If a user with the provided email already exists, an HTTP 400 error is returned.
    - **name**: The name of the user.
    - **email**: The email address of the user.
    - **phone**: The phone number of the user.
    - **password**: The password of the user.
    - **ort**: The locations of the user.
    """

    existing_user = collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    hashed_password = Hash.bcrypt(user.password)
    user.password = hashed_password
    
    _id = collection.insert_one(dict(user))
    user = users_serializer(collection.find({"_id": _id.inserted_id}))
    return {"status": "Ok", "data": user}

@user.post("/pdf")
async def login_user(info: PdfFile):
    """
    Create a PDF file

    Generates a PDF file with user-provided information in the form and returns a success message. 
    If an error occurs during PDF creation, returns HTTP 400 error. This pdf-file save in database with user's email from jwt token.
    """
    try:
        pdf_creations(f"testPdf {random.randint(0, 10000)}", info.name, info.date, info.nat)
        return {"status": "Ok", "data": "Pdf-file was created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user.post("/login")
async def login_user(user: UserLogin):
    """
    Login user

    Authenticates a user and returns a JWT token. If the user is not found or the credentials are invalid, an HTTP 400 error is returned.

    - **email**: The username of the user.
    - **password**: The password of the user.
    """

    found_user = collection.find_one({"email": user.email})
    
    if not found_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    if Hash.verify(user.password, found_user["password"]):
        token = jwt.encode({'sub': found_user["email"]}, os.getenv(
    "SecretJwt"), algorithm='HS256')
        return {"token": token}
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")


@user.get("/admin", dependencies=[Depends(verify_admin_token)])
async def admin_panel(request: Request):
    """
    Admin panel

    Returns a list of users for the admin. This route is protected and can only be accessed by authenticated users with admin privileges.
    """ 
    users = collection.find({"email": {"$ne": 'admin_statefree'}}, {"_id": 0})
    users = list(users)
    return users

@user.get("/get_email")
async def get_email(email=Depends(auth_middleware_email_return)):
    """
    Retrieves the email of the currently authenticated user.

    This route is protected and requires a valid JWT token to access. The token should be included in the
    Authorization header of the request as a Bearer token.

    """ 
    return {"email": email}


@user.post("/admin/editUser/{email}", dependencies=[Depends(verify_admin_token)])
async def user_change(email: str, request: Request, user: ChangeUser):
    """
    Edit a user's details (admin access required).

    This route allows an admin to update a user's name and phone number based on the provided email.
    """

    try:
        result = collection.update_one(
            {'email': email}, {'$set': {'name': user.name, 'phone': user.phone}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}")



@user.post("/admin/delete", dependencies=[Depends(verify_admin_token)])
async def admin_delete(request: Request, user: DeleteUser):
    """
    Delete a user (admin access required).

    This route allows an admin to delete a user from the database based on their email. It also deletes all associated files.
    """
    if not user.email:
        raise HTTPException(
            status_code=400, detail="User email must be provided")

    result = collection.delete_one({"email": user.email})
    delete_all_file(user.email)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"detail": f"User '{user.email}' deleted successfully"}
