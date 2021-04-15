function changeToLogin() {
    var loginForm = document.getElementById("login-form")
    var registerForm = document.getElementById("register-form")
    registerForm.style.display = "none";
    loginForm.style.display = "flex";
}

function changeToRegister() {
    var loginForm = document.getElementById("login-form")
    var registerForm = document.getElementById("register-form")
    registerForm.style.display = "flex";
    loginForm.style.display = "none";
}

function removeFromFavouritesProfile(itemID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/remfav');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("itemId="+itemID);
    var thisListItem = document.getElementById(itemID);
    thisListItem.style.display = "none";
}
