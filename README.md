# Assignment: Deploy

## Requirements
Deploy your Python server application to the cloud using Heroku. Prepare your application as necessary for this deployment, including adding support for PostgreSQL. Refer to the steps below.
Steps

### Prepare your server application for deployment:
- [x] &nbsp; Add a `Procfile` that describes how your application should be started, using Python, and which port number your server should listen on, using a command-line argument to your Python script and the `$PORT` environment variable.
- [x] &nbsp; Add a `requirements.txt` text file which lists all Python modules, and their versions, required by your server application. Note that the format and syntax of this file must be exact.
- [x] &nbsp; Add a `runtime.txt` text file which indicates the Python version that should be used to run your server application. Again, the format of this file must be exact.
- [x] &nbsp; Enable your server application to listen on the HTTP port as specified by a command-line argument (in order to support the `Procfile` mechanism described above).
- [x] &nbsp; Add support for PostgreSQL to your server application, using the `psycopg2` Python module. You will need to make modifications to your code that connects to the database, as well as very minor modifications to your various SQL statements. It should not be necessary to install or use PostgreSQL on your local computer, as the necessary changes should be minor enough to not require testing prior to deployment, but you may test locally if you wish.
- [x] &nbsp; Because you will no longer have direct access to your database to run SQL commands manually, is important to add code to your server application (if you haven’t already) that will attempt to create any necessary database tables (if they do not exist) when your server first runs. The SQL command below may be useful.
`CREATE TABLE IF NOT EXISTS table_name (...)`

### Deploy your server application to Heroku:
- [x] &nbsp; Initialize a Git repository (if you haven’t yet) and commit all of your changes to be deployed. Important: be sure that the root of your Git repository contains your Python server script as well as all of the files described above (without any of these files contained within subdirectories), or else the deployment will fail.
- [x] &nbsp; Create a new Heroku application (Heroku account and Heroku CLI required). Run this command (and subsequent commands) from the root of your Git repository:
`$ heroku create`
- [x] &nbsp; [Optional] Rename your Heroku application:
`$ heroku rename my-awesome-app`
- [x] &nbsp; Provision a Postgres database and attach it to your Heroku application:
`$ heroku addons:create heroku-postgresql:hobby-dev`
- [x] &nbsp; Push your code to Heroku (this may be repeated as additional changes are committed to your repository):
`$ git push heroku master`
- [x] &nbsp; Launch your deployed application in a web browser:
`$ heroku open`
- [x] &nbsp; If you encounter an error, inspect the Heroku logs to determine the cause:
`$ heroku logs`

### Update your client application:
- [ ] &nbsp; Anywhere you previously opened a request to your server application via http://localhost... in your client application, modify your code to use your deployed server application. Be sure to use https. It isn’t necessary to specify a port number for your Heroku server. It is a good idea to refactor your code to use a BASE_URL constant value for the base URL (everything that precedes the path), so that it’s easy to switch between your deployed server and your local server for development purposes.
`https://squirreltown.herokuapp.com/`

## Resources

Refer to [this example](https://github.com/djholt/python-heroku-demo) as you work through the steps outlined above.

## Submission
Show your completed assignment to the instructor during class or office hours to receive credit.
Submit your project using Git and GitHub. Start by creating a repo for this assignment [here](https://classroom.github.com/a/XMWb0Sba).