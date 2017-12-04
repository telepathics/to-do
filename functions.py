import sys, os, base64
sys.dont_write_bytecode = True

import psycopg2
import psycopg2.extras
import urllib.parse
import random
import string


def dict_factory(cursor, row):
	d = {}
	for i, col in enumerate(cursor.description):
		d[col[0]] = row[i]
	return d



# >>>>>>>>>>>>>>>> SESSIONS <<<<<<<<<<<<<<<<

class SessionStore:
	def __init__(self):
		self.sessionStore = {}
		
		return

	def createSession(self):
		rnum = os.urandom(32)
		ID = base64.b64encode(rnum).decode("utf-8")
		self.sessionStore[ID] = {}
		
		return ID

	def getSession(self, ID):
		if ID in self.sessionStore:
			return self.sessionStore[ID]
			
		return None

	def delSession(self,ID):
		if ID in self.sessionStore:
			del self.sessionStore[ID]

		return self.getSession[ID]

	def contains(self, key):
		return key in self.sessionStore





# >>>>>>>>>>>>>>>> DATABASE <<<<<<<<<<<<<<<<

class DB:
	def __init__(self):
		# self.connection = sqlite3.connect("auth.db")

		urllib.parse.uses_netloc.append("postgres")
		url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

		self.connection = psycopg2.connect(
			cursor_factory=psycopg2.extras.RealDictCursor,
			database=url.path[1:],
			user=url.username,
			password=url.password,
			host=url.hostname,
			port=url.port
		)

		# self.connection.row_factory = dict_factory

		self.cursor = self.connection.cursor()

	def __del__(self):
		self.connection.close()

	def createTables(self):
		 self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, email VARCHAR(255) UNIQUE, encrypted_password VARCHAR(255), first_name VARCHAR(255), last_name VARCHAR(255))")
		 self.cursor.execute("CREATE TABLE IF NOT EXISTS tasks (TID SERIAL PRIMARY KEY, task_name VARCHAR(255), description VARCHAR(255), UID INTEGER, completed INTEGER)")

		 self.connection.commit()


	# ---------------- INSERT ----------------

	def insertUser(self, **args):
		if "email" not in args or "first_name" not in args or "last_name" not in args or "encrypted_password" not in args:
			return (400, "Missing arguments.")

		email = args["email"].lower()
		first_name = args["first_name"].lower()
		last_name = args["last_name"].lower()

		if self.retrieveUserByEmail(email):
			return (409, "Email already in use.")

		self.cursor.execute("INSERT INTO users (email, first_name, last_name, encrypted_password) VALUES (%s, %s, %s, %s)", (email, first_name, last_name, args["encrypted_password"]))
		self.connection.commit()

		return (201, "User created.")

	def insertTask(self, **args):
		if "task_name" not in args:
			return (400, "Missing arguments.")

		if "description" not in args:
			args["description"] = ""

		task_name = args["task_name"].lower()
		UID = args["UID"]

		self.cursor.execute("INSERT INTO tasks (task_name, description, UID, completed) VALUES (%s, %s, %s, %s)", (task_name, args["description"], UID, 0))
		self.connection.commit()

		return (201, "Task created.")


	# ---------------- RETRIEVE ----------------

	def retrieveUserByEmail(self, email):
		for row in self.cursor.execute("SELECT * FROM users WHERE email = %s", (email, )):

			return {"UID": row['UID'], "email": row['email'], "first_name": row['first_name'], "last_name": row['last_name'], "encrypted_password": row['encrypted_password'], "image": row['image']}

		return None

	def retrieveTasks(self, UID):
		tasks = []
		for row in self.cursor.execute("SELECT * FROM tasks WHERE UID = %s", (UID, )):
			tasks.append({"TID": row['TID'], "task_name": row['task_name'], "description": row['description'], "UID": int(row['UID']), "completed": bool(row['completed'])})

		return tasks

	def retrieveTaskByID(self, TID):
		for row in self.cursor.execute("SELECT * FROM tasks WHERE TID = %s", (TID, )):
			return ({"TID": int(row['TID']), "task_name": row['task_name'], "description": row['description'], "UID": int(row['UID']), "completed": bool(int(row['completed']))})

		return None


	# ---------------- UPDATE ----------------

	def completeTask(self, TID):
		if not self.retrieveTaskByID(TID):
			return (404, "Task not found.")

		self.cursor.execute("UPDATE tasks SET completed=? WHERE TID = %s", (True, TID))
		self.connection.commit()

	def updateProfile(self, UID, changes):
		self.cursor.execute("UPDATE users SET image = %s, first_name = %s, last_name = %s WHERE UID = %s", (changes['image'], changes['first_name'], changes['last_name'], UID))
		self.connection.commit()
