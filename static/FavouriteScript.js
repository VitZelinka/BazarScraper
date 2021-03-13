function addToFavourites(itemID, buttonID) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/addfav');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("itemId="+itemID);
    var thisButton = document.getElementById(buttonID);
    var secondButton = document.getElementById(buttonID.replace("favAddButton", "favRemButton"))
    console.log(thisButton)
    console.log(secondButton)
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