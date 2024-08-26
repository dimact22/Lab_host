from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
import shutil
import os
import gridfs
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from db.models import users_serializer
from schemas.user import User, UserLogin, DeleteUser, ChangeUser
from schemas.info_save import Info
from schemas.contact import ContactForm
from config.db import collection, db, infos
from db.hash import Hash
from jose import jwt
from utilities.helper import remove_field_document
from middelware.auth import auth_middleware, verify_admin_token, auth_middleware_username_return
import os
import json
from db.uploaded_files import save_file, retrieve_file, delete_file, userFiles, getFile

user = APIRouter(prefix="/user", tags=['user'])
templating = Jinja2Templates(directory="templates")
templating2 = Jinja2Templates(directory=".")


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
        'Receiver_email', "rediscoolstatefree@gmail.com")
    subject = f"Message from user {contact.email}"
    message_body = contact.message
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = os.getenv('Smtp_username', "rediscoolstatefree@gmail.com")
    smtp_password = os.getenv('Smtp_password', "rkfw kogp tbut bkfo")

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
async def create_upload_file(file: UploadFile, name=Depends(auth_middleware_username_return)):
    """
    Upload a file

    Uploads a file to the server and processes it. The file is temporarily saved on the server, processed, saved in database, and then removed.

    - **file**: The file to be uploaded.
    """
    upload_folder = "uploaded_files"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    with open(f"uploaded_files/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_id = save_file(f"uploaded_files/{file.filename}", file.filename, name)
    os.remove(f"uploaded_files/{file.filename}")
    return {"filename": file.filename}


@user.delete("/delete_file/{file_id}")
async def delete_file_api(file_id: str):
    if delete_file(file_id):
        return {"message": f"File with ID {file_id} has been deleted successfully."}
    else:
        raise HTTPException(
            status_code=404, detail=f"No file found with ID {file_id}.")


@user.get("/user_files/{user_name}")
async def get_user_files(user_name: str):
    try:
        return userFiles(user_name)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving files: {e}")


@user.get("/file/{file_id}")
def get_file(file_id: str):
    try:
        return getFile(file_id)
    except gridfs.errors.NoFile:
        raise HTTPException(status_code=404, detail="File not found")


@user.get("/save_file/{email}", response_class=HTMLResponse, summary="Displays a form to fill it")
async def read_form(request: Request, email: str,):
    found_user = infos.find_one({"email": email})
    if found_user:
        print(found_user)
        return templating.TemplateResponse("i.html", {"request": request, "data": dict(found_user)})
    else:
        print(3)
        html_file_path = "i.html"
        return templating2.TemplateResponse("i.html", {"request": request, "data": email})


@user.get("/submit_info/{email}", summary="Create pdf_file")
async def submit_info(email: str):
    found_user = infos.find_one({"email": email})
    if found_user:
        found_user = json.dumps(
            str(found_user), ensure_ascii=False, indent=4)
        return found_user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@user.post("/save_info/{email}", summary="Saves all the completed information in the form")
async def save_info(email, firstname: str = Form("0"),
                    lastname: str = Form("0"),
                    age: int = Form("0"),
                    gender: str = Form("0")):
    info = Info(firstname=firstname, lastname=lastname, age=age, gender=gender)
    collection = db.get_collection("infos")
    if collection.find_one({"email": email}):
        collection.delete_one({"email": email})
    collection.insert_one({"email": email, } | dict(info))
    return {"message": "User info received successfully", "user_info": info.dict()}


@user.post("/register")
async def create_user(user: User):
    """
    Register a new user

    Creates a new user account with a hashed password. If a user with the provided email already exists, an HTTP 400 error is returned.
    - **name**: The name of the user.
    - **email**: The email address of the user.
    - **phone**: The phone number of the user.
    - **password**: The password of the user.
    """

    existing_user = collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    existing_user = collection.find_one({"name": user.name})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="A user with this name already exists")
    hashed_password = Hash.bcrypt(user.password)
    user.password = hashed_password
    _id = collection.insert_one(dict(user))
    user = users_serializer(collection.find({"_id": _id.inserted_id}))
    return {"status": "Ok", "data": user}


@user.post("/login")
async def login_user(user: UserLogin):
    """
    Login user

    Authenticates a user and returns a JWT token. If the user is not found or the credentials are invalid, an HTTP 400 error is returned.

    - **name**: The username of the user.
    - **password**: The password of the user.
    """

    found_user = collection.find_one({"name": user.name})

    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    if Hash.verify(user.password, found_user["password"]):
        token = jwt.encode(
            {'sub': found_user["name"]}, "test", algorithm='HS256')
        return {"token": token}
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")


@user.get("/admin", dependencies=[Depends(verify_admin_token)])
async def admin_panel(request: Request):
    users = collection.find({"name": {"$ne": 'admin_statefree'}}, {"_id": 0})
    users = list(users)
    return users


@user.post("/admin/edit/{name}", dependencies=[Depends(verify_admin_token)])
async def user_change(name: str, request: Request, user: ChangeUser):
    try:
        result = collection.update_one(
            {'name': name}, {'$set': {'email': user.email, 'phone': user.phone}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@user.post("/admin/delete", dependencies=[Depends(verify_admin_token)])
async def admin_delete(request: Request, user: DeleteUser):
    if not user.name:
        raise HTTPException(
            status_code=400, detail="User name must be provided")

    result = collection.delete_one({"name": user.name})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"detail": f"User '{user.name}' deleted successfully"}


@user.get("/{user_id}", dependencies=[Depends(auth_middleware)])
async def detail(user_id: str):
    """
    Get user details

    Retrieves detailed information about a user, excluding sensitive fields.

    - **user_id**: The user ID in the database.
    """

    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    user_detail = collection.find_one({"_id": user_obj_id})
    if not user_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Could not find user with given ID")

    user_remove = remove_field_document(user_detail, ["password"])
    user_remove["id"] = str(user_remove["_id"])
    user_remove.pop("_id", None)

    return user_remove


@user.get("")
async def get_user():
    userdata = collection.find({}, {"_id": 0})
    result_dicts = [doc for doc in userdata]
    return result_dicts
