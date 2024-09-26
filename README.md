

# Setting up Virtual Environment
To set up a virtual environment for this application, follow these steps:

1. Open a command prompt at the root of the application's folder (REDLAB).
2. Create a directory named venv:

    `mkdir venv`

3. Navigate into 'venv

    `cd venv`

4. create a virtual enviroment named 'redilab' using Python's 'venv' module: 

    ` python -m venv redilab`

5. activate the virtual enviroment 

on Windows:

`venv/Scripts/activate`

on macOS/Linux

`venv/bin/activate`

# Managing the Stack(Backend)
## Install Dependencies

1. Install the backend dependencies

    `pip install -r requirements.txt`


## Stack management

1. Open a command prompt at the root of the application's folder.

2. add a new .env file and then the codes in the env.simple in . env
3. Run: `docker-compose up -d --build`
3. View Container: `docker ps`

4. Go inside a Container: `docker exec -it <nodeContainerID> sh` (replace <nodeContainerID>)
5. Stop containers : `docker-compose down`
6. Stop all running Containers: `docker stop $(docker ps -aq)`
7. remove all Containers: `docker rm $(docker ps -aq)`

## Run the Application

1. Start the FastAPI server:

  `docker-compose up --build`

2. Access Swagger UI:

Open your browser and navigate to http://localhost:8000/docs to access the Swagger UI documentation.
## Tools and Technologies
### MongoDB

This application uses MongoDB as the database. Follow these steps to set up MongoDB:

Install MongoDB:

Visit the MongoDB Download Center and follow the instructions to install MongoDB on your system.

Install MongoDB Compass:

Download and install MongoDB Compass, a GUI for MongoDB, to visualize and manage your MongoDB data.

### Docker Desktop

Download and install Docker Desktop for your operating system.

### Postman

Download and install Postman to test and interact with your API endpoints.

Managing MongoDB with Docker
This application uses Docker to manage MongoDB. The docker-compose.yml file includes the configuration for the MongoDB service.

### Using Postman
Postman can be used to test the endpoints of the application. Here's how:

Open Postman.
Create a new request and set the appropriate method (GET, POST, etc.) and URL.
Add headers and body as needed.
Send the request and view the response.
