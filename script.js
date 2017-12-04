"use strict";
let apiURL = "https://web-to-do.herokuapp.com/"

let toDoList = [];
let toDoneList = [];
let totalcount = 0;

let taskslist = document.querySelector("#tasks-list");
let newtask = document.querySelector("#new-task");
let inProgress = document.querySelector("#inprogress");
let completedTasks = document.querySelector("#completedtasks");

let authPage = document.getElementById("auth-page");
let sideBar = document.getElementById("side-bar");
let taskPage = document.getElementById("task-page");
let profilePage = document.getElementById("profile-page");

let emailInUse = document.querySelectorAll(".emailInUse");
let somethingWrong = document.querySelectorAll(".somethingWrong");
let missingFormItems = document.querySelectorAll(".missingFormItems");

function addNewUser() {
		let regFirstname = document.getElementById("regFirstName");
		let regLastName = document.getElementById("regLastName")
		let regEmail = document.getElementById("regEmail");
		let regPassword = document.getElementById("regPassword");

		if (regFirstname.value != '' && regLastName.value != '' && regEmail.value != '' && regPassword != '') {
			let regData = {
				'first_name': regFirstName.value,
				'last_name': regLastName.value,
				'email': regEmail.value,
				'encrypted_password': regPassword.value
			}

			fetch(`${apiURL}/users`, {
				method: "POST",
				credentials: "include",
				body: JSON.stringify(regData)
			}).then(function(response) {
				if (response['status'] == 201) {
					loginUser();
					showTaskPage();
				} else {
					emailInUse[0].style.display = "block";
				}
			})
		} else {
			missingFormItems[0].style.display = "block";
		}

}

function loginUser() {
	let logEmail = document.getElementById("logEmail");
	let logPassword = document.getElementById("logPassword");

	if (logEmail.value != '' && logPassword != '') {
		let logData = {
			'email': logEmail.value,
			'encrypted_password': logPassword.value
		}

		fetch(`${apiURL}/authenticate`, {
			method: "POST",
			credentials: "include",
			body: JSON.stringify(logData)
		}).then(function(response) {
			let status_code = response['status'];
			if (status_code < 200 && status_code > 299 || status_code == 404 || status_code == 401) {
				somethingWrong[0].style.display = "block";
			} else if (status_code == 422) {
				missingFormItems[1].style.display = "block";
			} else {
				showTaskPage();
			}
		})
	} else {
		missingFormItems[1].style.display = "block";
	}
}

function logoutUser() {
	fetch(`${apiURL}/authenticate`, {
		method: "DELETE",
		credentials: "include"
	}).then(function() {
		showAuthPage();
	})
}

let userID, userFName, userLName, userEmail, userImage;
function getUserData() {
	fetch(`${apiURL}/user`, {
		method: "GET",
		credentials: "include"
	}).then(function(response) {
		return response.json();
	}).then(function(data) {

		userID = data['UID'];
		userFName = data['first_name'];
		userLName = data['last_name'];
		userEmail = data['email'];
		userImage = data['image'];

		let userFNameLocs = document.querySelectorAll(".userFName");
		for (let i=0; i < userFNameLocs.length; i++) {
			userFNameLocs[i].innerText = userFName;
		}

		if (userImage != undefined) {
			let userImageLocs = document.querySelectorAll(".user-icon");
			for (let i=0; i < userImageLocs.length; i++) {
				userImageLocs[i].src = userImage;
				userImageLocs[i].alt = `${userFName} icon image`;
			}
		} else {
			let userImageLocs = document.querySelectorAll(".user-icon");
			for (let i=0; i < userImageLocs.length; i++) {
				userImageLocs[i].src = "./imgs/default-icon.jpg";
				userImageLocs[i].alt = `${userFName} icon image`;
			}
		}

		document.getElementById("updateFName").value = userFName;
		document.getElementById("updateLName").value = userLName;
	})
}

function updateProfile() {
	let updateData = {
		'image': document.getElementById("image").src,
		'first_name': document.getElementById("updateFName").value,
		'last_name': document.getElementById("updateLName").value
	}

	fetch(`${apiURL}/user/profile`, {
		method: "PUT",
		credentials: "include",
		body: JSON.stringify(updateData)
	}).then(function() {
		showTaskPage();
	})
}

function addNewTask() {
	let taskData = {
		'task_name': newtask.value,
		'description': '',
		'completed': 0
	}

	fetch(`${apiURL}/tasks`, {
		method: "POST",
		credentials: "include",
		body: JSON.stringify(taskData)
	}).then(function() {
		let taskid = "task" + totalcount;
		totalcount += 1

		toDoList.push(taskid);
		
		styleTask(taskid, newtask.value);

		newtask.value = "";

		updateTaskCounts();
	})
};

function getTasks() {
	fetch(`${apiURL}/tasks`, {
		method: "GET",
		credentials: "include"
	}).then(function(response) {
		return response.json();
	}).then(function(body) {
		body = body['tasks'];

		toDoList = [];
		toDoneList = [];

		for (let i=0; i < body.length; i++) {
			if (body[i]['completed'] == false) {
				toDoList.push(body[i]['TID']);
				styleTask(body[i]['TID'], body[i]['task_name']);
			} else {
				toDoneList.push(body[i]['TID']);
			}
		}

		updateTaskCounts()
	})
}

function styleTask(taskid, taskname) {
	let listitem = document.createElement("li");
	listitem.classList.add("task");
	listitem.setAttribute("id", "li"+taskid);

	let checkbox = document.createElement("input");
	checkbox.setAttribute("id", taskid);
	checkbox.type = "checkbox";
	checkbox.addEventListener("click", function(e) {
		checkAnimation(taskid);
		setTimeout(function() { checkItem(taskid); }, 200);
	});

	let label = document.createElement("label");
	label.setAttribute("for", taskid);
	let span = document.createElement("span");

	taskslist.appendChild(listitem);
	listitem.appendChild(checkbox);
	listitem.appendChild(label);

	label.innerHTML = "<span></span>"+taskname;

	tinyCareScript();
}

function updateTaskCounts() {
	inProgress.innerHTML = toDoList.length;
	completedTasks.innerHTML = toDoneList.length;
}

function checkSession() {
	fetch(`${apiURL}/tasks`, {
		method: "GET",
		credentials: "include"
	}).then(function(response) {
		if (response['status'] == 404 || response['status'] == 401) {
			showAuthPage();
		} else if (response['status'] == 201 || response['status'] == 200) {
			showTaskPage();
		}
		tinyCareScript();
		return response.json();
	})
}

function showAuthPage() {
	authPage.style.display = "flex";
	sideBar.style.opacity = "0";
	taskPage.style.opacity = "0";

	profilePage.style.display = "none";

	// document.getElementById('regPassword').onkeydown = function(e){
	// 	if(e.keyCode == 13){
	// 		addNewUser();
	// 	}
	// };

	getUserData();
}

function showTaskPage() {
	authPage.style.display = "none";
	sideBar.style.opacity = "1";

	taskPage.style.display = "block";
	taskPage.style.opacity = "1";

	profilePage.style.display = "none";

	// document.getElementById('#new-task').onkeydown = function(e){
	// 	if(e.keyCode == 13){
	// 		addNewTask();
	// 	}
	// }

	getUserData();
	getTasks();
}

function showProfilePage() {
	authPage.style.display = "none";
	sideBar.style.opacity = "1";
	taskPage.style.display = "none";

	profilePage.style.display = "block";
	profilePage.style.opacity = "1";
	profilePage.style.zIndex = "1";

	getUserData();
}

function readURL (input) {
	if (input.files && input.files[0]) {
		let reader = new FileReader();
			reader.onload = function (e) {
				let pic = document.getElementById('image');
				pic.src = e.target.result;
			}
		reader.readAsDataURL(input.files[0]);
	}
}

function checkAnimation(taskid) {
	let tasksList = document.getElementById(`li${taskid}`);
	let taskItem = document.querySelector(`label[for="${taskid}"]`);

	taskItem.style.textDecoration = "line-through";
	taskItem.style.opacity = 0;
}

function checkItem(taskid) {
	fetch(`${apiURL}/tasks/${taskid}`, {
		method: "PUT",
		credentials: "include"
	}).then(function(response) {
		toDoneList.push(taskid);
		toDoList = toDoList.filter(val => val !== taskid);

		document.getElementById(`li${taskid}`).remove();

		updateTaskCounts()
		
		window.setTimeout(function() { tinyCareScript(); }, 100);
	})
};

function tinyCareScript() {
	let careRepo = ["remember to drink some water!", "say hello to an old friend!", "nap time!", "smile a little :)", "listen to music that makes you feel good!", "remember to eat something, please!", "take a walk, you deserve it!", "try to find time to do something creative!"];
	if (taskslist.childNodes.length == 3) {
		document.querySelector('#inboxZero').style.display = "flex";

		document.querySelector('#allDone').innerHTML = "💗&nbsp; Looks like you're all done for now 💗 <br/>"
		document.querySelector('#tiny-care').innerHTML = careRepo[Math.floor(Math.random() * careRepo.length)];

		window.setTimeout(function() {
			document.querySelector("#inboxZero").style.opacity = 1;
		}, 0);
	} else {
		document.querySelector('#inboxZero').style.display = "none";
		document.querySelector("#inboxZero").style.opacity = 0;
	}
};

checkSession();

