import sys, os
sys.dont_write_bytecode = True

import json
import http.cookies as cookies

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from passlib.hash import bcrypt
import bcrypt as cryptb

from functions import *


gSessionStore = SessionStore()





class Handler(BaseHTTPRequestHandler):

	# >>>>>>>>>>>>>>>> CORS & CHECKING <<<<<<<<<<<<<<<<

	def end_headers(self):
		self.sendCookie()
		self.send_header("Access-Control-Allow-Origin", self.headers['Origin'])
		self.send_header("Access-Control-Allow-Headers", "Content-Type, Content-Length")
		self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		self.send_header("Access-Control-Allow-Credentials", "true")
		BaseHTTPRequestHandler.end_headers(self)

	def handle404(self):
		self.send_response(404)
		self.send_header("Content-Type", "text/plain")
		self.end_headers()

		self.wfile.write("Not found.".encode("utf-8"))

	def sendError(self, status_code, error):
		self.send_response(status_code)
		self.send_header("Content-Type", "text/plain")
		self.end_headers()
		self.wfile.write(error.encode("utf-8"))

	def checkPath(self, mask):
		mask_parts = mask[1:].split("/")
		path_parts = self.path[1:].rstrip("/").split("/")
		if len(mask_parts) != len(path_parts):
			self.url_vars = {}
			return False

		vars = {}
		for i in range(len(mask_parts)):
			if mask_parts[i][0] == "{":
				vars[mask_parts[i][1:-1]] = path_parts[i]
			else:
				if mask_parts[i] != path_parts[i]:
					self.url_vars = {}
					return False

		self.url_vars = vars
		return True





	# >>>>>>>>>>>>>>>> JSON <<<<<<<<<<<<<<<<

	def getJSON(self):
		if "Content-Length" not in self.headers:
			return (422, {})
		if self.headers["Content-Length"] == "0":
			return (422, {})

		raw_body = self.rfile.read(int(self.headers["Content-Length"]))

		try:
			body = json.loads(raw_body.decode("utf-8"))
		except json.decoder.JSONDecodeError:
			body = {}
			return (422, {})
		return (200, body)





	# >>>>>>>>>>>>>>>> COOKIES <<<<<<<<<<<<<<<<

	def loadCookie(self):
		if "Cookie" in self.headers:
			self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
		else:
			self.cookie = cookies.SimpleCookie()

	def sendCookie(self):
		if not hasattr(self, "cookie"): return

		for morsel in self.cookie.values():
			self.send_header("Set-Cookie", morsel.OutputString())





	# >>>>>>>>>>>>>>>> SESSIONS <<<<<<<<<<<<<<<<

	def loadSession(self):
		self.loadCookie()

		if not "sessionID" in self.cookie or not gSessionStore.contains(self.cookie["sessionID"].value):
			self.cookie["sessionID"] = gSessionStore.createSession()

		self.session = gSessionStore.getSession(self.cookie["sessionID"].value)





	# >>>>>>>>>>>>>>>> METHODS <<<<<<<<<<<<<<<<

	def do_OPTIONS(self):
		self.send_response(200)
		self.end_headers()


	def do_GET(self):
		self.loadSession()

		# RETURN USER INFORMATION
		if self.checkPath("/users/{email}"):
			user = db.retrieveUserByEmail(self.url_vars["email"])
			if not user:
				self.sendError(404, "Email not found")
				return
			self.send_response(200)
			self.send_header("Content-Type", "application/json")
			self.end_headers()

			self.wfile.write(json.dumps({
				"email": user["email"],
				"first_name": user["first_name"],
				"last_name": user["last_name"],
				"image": user["image"]
				}).encode("utf-8"))

		# RETURN AUTHENTICATED USER INFORMATION
		elif self.checkPath("/user"):
			if "email" not in self.session:
				self.sendError(401, "Unauthorised Access.")
				return

			user = db.retrieveUserByEmail(self.session["email"])

			self.send_response(200)
			self.send_header("Content-Type", "application/json")
			self.end_headers()

			self.wfile.write(json.dumps({
				"email": user["email"],
				"first_name": user["first_name"],
				"last_name": user["last_name"],
				"image": user["image"],
				"UID": self.session["UID"]
			}).encode("utf-8"))

		# RETURN JSON LIST OF TASKS UNDER AUTHENTICATED USER
		elif self.checkPath("/tasks"):
			if "email" not in self.session:
				self.sendError(401, "Unauthorised Access.")
				return

			tasks = db.retrieveTasks(self.session["UID"])

			self.send_response(200)
			self.send_header("Content-Type", "application/json")
			self.end_headers()

			self.wfile.write(json.dumps({
				"tasks": tasks
			}).encode("utf-8"))

		else:
			self.handle404()


	def do_POST(self):
		self.loadSession()

		# LOGIN
		if self.checkPath("/authenticate"):
			status_code, body = self.getJSON()
			if status_code < 200 or status_code > 299:
				self.sendError(status_code, "Could not parse JSON from body")
				return

			if "email" not in body or "encrypted_password" not in body:
				self.sendError(422, "Not all values in body")
				return

			user = db.retrieveUserByEmail(body['email'])
			if not user:
				self.sendError(404, "User not found")
				return

			if not bcrypt.verify(body["encrypted_password"], user['encrypted_password']):
				self.sendError(401, "Incorrect password.")
				return

			self.session["email"] = body["email"]
			self.session["UID"] = user["UID"]

			self.send_response(200)
			self.send_header("Content-Type", "application/json")
			self.end_headers()

		# REGISTRATION
		elif self.checkPath("/users"):
			status_code, body = self.getJSON()
			if status_code < 200 or status_code > 299:
				self.sendError(status_code, "Could not parse JSON from body.")
				return

			if "email" not in body or "first_name" not in body or "last_name" not in body or "encrypted_password" not in body:
				self.sendError(422, "Missing required values")
				return

			body["encrypted_password"] = bcrypt.encrypt(body["encrypted_password"])

			status_code, rtn = db.insertUser(**body)
			if status_code < 200 or status_code > 299:

				self.sendError(status_code, rtn)
				return


			user = db.retrieveUserByEmail(body['email'])

			self.session["email"] = body['email']
			self.session["UID"] = user['UID']

			self.send_response(201)
			self.send_header("Content-Type", "application/json")
			self.end_headers()

		# ADD NEW TASK
		elif self.checkPath("/tasks"):

			if "email" not in self.session:
				self.sendError(401, "Unauthorised Access.")
				return

			status_code, body = self.getJSON()


			if "task_name" not in body:
				self.sendError(422, "Missing required fields")
				return

			body['UID'] = self.session['UID']

			status_code, rtn = db.insertTask(**body)
			if status_code < 200 or status_code > 299:

				self.sendError(status_code, rtn)
				return

			self.send_response(201)
			self.send_header("Content-Type", "application/json")
			self.end_headers()

		else:
			self.handle404()

	def do_PUT(self):
		self.loadSession()

		# COMPLETE TASK
		if self.checkPath("/tasks/{TID}"):
			if "email" not in self.session:
				self.sendError(401, "Unauthorised Access")
				return

			task = db.retrieveTaskByID(self.url_vars["TID"])
			if not task or task["UID"] != self.session["UID"]:
				self.sendError(404, "Task not found under given ID.")
				return

			db.completeTask(task["TID"])

			self.send_response(200)
			self.send_header("Content-Type", "application/json")
			self.end_headers()

		# UPDATE PROFILE
		if self.checkPath("/user/profile"):
			if "email" not in self.session:
				self.sendError(401, "Unauthorised Access")
				return

			status_code, body = self.getJSON()

			db.updateProfile(self.session["UID"], body)
			self.send_response(200)
			self.send_header("Content-Type", "application/json")
			self.end_headers()

		else:
			self.handle404()


	def do_DELETE(self):
		self.loadSession()

		# LOGOUT
		if self.checkPath("/authenticate"):
			if "email" not in self.session:
				self.sendError(401, "Unauthorised Access.")
				return

			self.send_response(200)
			self.send_header("Content-Type", "application/json")
			self.end_headers()

			self.session = {}
		else:
			self.handle404()





# >>>>>>>>>>>>>>>> START RUNNING SERVER <<<<<<<<<<<<<<<<

def main():
	db = DB()
	db.createTables()
	db = None # disconnect

	port = 8080
	if len(sys.argv) > 1:
		port = int(sys.argv[1])

	listen = ("0.0.0.0", port)
	server = HTTPServer(listen, Handler)
	print("Server listening on", "{}:{}".format(*listen))
	server.serve_forever()

main()
