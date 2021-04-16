function showItems() {
    var ItemsList = document.getElementById("AdminItemsList");
    var UsersList = document.getElementById("AdminUsersList");
    var ReportsList = document.getElementById("AdminReportsList");
    var LogsList = document.getElementById("AdminLogsList");
    ItemsList.style.display = "flex";
    UsersList.style.display = "none";
    ReportsList.style.display = "none";
    LogsList.style.display = "none";
}

function showUsers() {
    var ItemsList = document.getElementById("AdminItemsList");
    var UsersList = document.getElementById("AdminUsersList");
    var ReportsList = document.getElementById("AdminReportsList");
    var LogsList = document.getElementById("AdminLogsList");
    ItemsList.style.display = "none";
    UsersList.style.display = "flex";
    ReportsList.style.display = "none";
    LogsList.style.display = "none";
}

function showReports() {
    var ItemsList = document.getElementById("AdminItemsList");
    var UsersList = document.getElementById("AdminUsersList");
    var ReportsList = document.getElementById("AdminReportsList");
    var LogsList = document.getElementById("AdminLogsList");
    ItemsList.style.display = "none";
    UsersList.style.display = "none";
    ReportsList.style.display = "flex";
    LogsList.style.display = "none";
}

function showLogs() {
    var ItemsList = document.getElementById("AdminItemsList");
    var UsersList = document.getElementById("AdminUsersList");
    var ReportsList = document.getElementById("AdminReportsList");
    var LogsList = document.getElementById("AdminLogsList");
    ItemsList.style.display = "none";
    UsersList.style.display = "none";
    ReportsList.style.display = "none";
    LogsList.style.display = "flex";
}

function unpublishItem(itemID, buttonID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/unpublish');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("itemId="+itemID);
    var thisButton = document.getElementById(buttonID);
    var secondButton = document.getElementById(buttonID.replace("unpublishButton", "publishButton"))
    thisButton.style.display = "none";
    secondButton.style.display = "inline";
}

function publishItem(itemID, buttonID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/publish');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("itemId="+itemID);
    var thisButton = document.getElementById(buttonID);
    var secondButton = document.getElementById(buttonID.replace("publishButton", "unpublishButton"))
    thisButton.style.display = "none";
    secondButton.style.display = "inline";
}

function unpublishItemRep(itemID, buttonID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/unpublish');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("itemId="+itemID);
    var thisButton = document.getElementById(buttonID);
    var secondButton = document.getElementById(buttonID.replace("unpublishButton", "publishButton"))
    thisButton.style.display = "none";
    secondButton.style.display = "inline";
}

function publishItemRep(itemID, buttonID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/publish');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("itemId="+itemID);
    var thisButton = document.getElementById(buttonID);
    var secondButton = document.getElementById(buttonID.replace("publishButton", "unpublishButton"))
    thisButton.style.display = "none";
    secondButton.style.display = "inline";
}

function removeItem(itemID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/deleteitem');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("itemId="+itemID);
    var thisListItem = document.getElementById(itemID);
    thisListItem.style.display = "none";
}

function removeItemRep(itemID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/deleteitem');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("itemId="+itemID);
    var thisListItem = document.getElementById("rep"+itemID);
    thisListItem.style.display = "none";
}

function removeUser(userID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/deleteuser');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("userId="+userID);
    var thisListItem = document.getElementById("us"+userID);
    thisListItem.style.display = "none";
}

function revoke(userID, buttonID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/revoke');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("userId="+userID);
    var thisButton = document.getElementById(buttonID);
    var secondButton = document.getElementById(buttonID.replace("Revoke", "Grant"))
    thisButton.style.display = "none";
    secondButton.style.display = "inline";
}

function grant(userID, buttonID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/grant');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("userId="+userID);
    var thisButton = document.getElementById(buttonID);
    var secondButton = document.getElementById(buttonID.replace("Grant", "Revoke"))
    thisButton.style.display = "none";
    secondButton.style.display = "inline";
}
