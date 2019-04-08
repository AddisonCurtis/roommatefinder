function logout() {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "/apit/logout", true);
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.send(JSON.stringify({}));
}
