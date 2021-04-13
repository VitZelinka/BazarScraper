function addToFavourites(itemID, buttonID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/addfav');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("itemId="+itemID);
    var thisButton = document.getElementById(buttonID);
    var secondButton = document.getElementById(buttonID.replace("favAddButton", "favRemButton"))
    thisButton.style.display = "none";
    secondButton.style.display = "inline";
}

function removeFromFavourites(itemID, buttonID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/remfav');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("itemId="+itemID);
    var thisButton = document.getElementById(buttonID);
    var secondButton = document.getElementById(buttonID.replace("favRemButton", "favAddButton"))
    thisButton.style.display = "none";
    secondButton.style.display = "inline";
}

function removeFromFavouritesProfile(itemID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/remfav');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("itemId="+itemID);
    var thisListItem = document.getElementById(itemID);
    thisListItem.style.display = "none";
}


var globalItemID = 0
function openReportPopup(itemID) {
    var window = document.getElementById("report-popup-window")
    window.style.display = "block";
    globalItemID = itemID
}

function closeReportPopup() {
    var window = document.getElementById("report-popup-window")
    window.style.display = "none";
    globalItemID = 0
}

function reportItem() {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/report');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("itemId="+globalItemID);
    var window = document.getElementById("report-popup-window")
    window.style.display = "none";
}