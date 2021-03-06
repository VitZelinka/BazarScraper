function addToFavourites(itemID) {
    var xhr = new XMLHttpRequest()
    xhr.open('POST', '/addfav')
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send("itemId="+itemID)
}