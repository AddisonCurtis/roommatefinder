function logout() {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "/api/logout", true);
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.send(JSON.stringify({}));
}
