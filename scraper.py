from bs4 import BeautifulSoup
import requests
import mysql.connector
import time

mysql = mysql.connector.connect(
  host="192.168.0.188",
  user="client",
  password="memicko",
  database = "bazarscraper"
)
cur = mysql.cursor()
cur.close()

#get list of urls - OK
#check if urls already in DB - OK
#go through remaining urls - OK
#get item heading - OK
#get item picture url - OK
#save all to DB - OK
def scrapeNewSbazarURLs():
    url = "https://www.sbazar.cz/30-elektro-pocitace/cela-cr/zdarma?cena-dohodou=bez"
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("li", class_="c-item c-item--uw")
        urls = []
        for item in items:
            anchor = item.find("a", class_="c-item__link")
            urls.append(anchor["href"])
        cur = mysql.cursor()
        newUrls = []
        for url in urls:
            cur.execute(f"SELECT EXISTS(SELECT * FROM items WHERE url = '{url}');")
            dbresponse = cur.fetchall()
            if dbresponse[0][0] == 0:
                newUrls.append(url)
        cur.close()
        return newUrls


def scrapeSbazarData(urls):
    cur = mysql.cursor()
    for url in urls:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            img = soup.find("img", class_="ob-c-gallery__img")
            try:
                imgURL = img["src"]
            except:
                imgURL = "placeholder.png"
            heading = soup.find("h1", class_="p-uw-item__header").text
            cur.execute(f"INSERT INTO items (url, imgurl, heading, bazar) VALUES ('{url}', '{imgURL}', '{heading}', 'sbazar');")
            mysql.commit()
            print(f"URL {url} used.")
    cur.close()
    

scrapeSbazarData(scrapeNewSbazarURLs())