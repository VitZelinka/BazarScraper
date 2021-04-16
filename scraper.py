from bs4 import BeautifulSoup
import requests
import mysql.connector


mysql = mysql.connector.connect(
  host="192.168.0.188",
  user="client",
  password="memicko",
  database = "bazarscraper"
)

#get list of urls - OK
#check if urls already in DB - OK
#go through remaining urls - OK
#get item heading - OK
#get item picture url - OK
#save all to DB - OK
#https://pc.bazos.cz/?hlokalita=&humkreis=0&cenaod=0&cenado=0
#https://mobil.bazos.cz/?hlokalita=&humkreis=0&cenaod=0&cenado=0
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
    numberOfUrls = 0
    for url in urls:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            img = soup.find("img", class_="ob-c-gallery__img")
            try:
                imgURL = img["src"]
            except:
                imgURL = "static/placeholder.png"
            heading = soup.find("h1", class_="p-uw-item__header").text
            cur.execute(f"INSERT INTO items (url, imgurl, heading, bazar, public) VALUES ('{url}', '{imgURL}', '{heading}', 'sbazar', 1);")
            mysql.commit()
            numberOfUrls += 1
    cur.execute(f"INSERT INTO logs (author, message) VALUES ('scraperscript', 'Scraped {numberOfUrls} URLs from sbazar.');")
    mysql.commit()
    cur.close()


def scrapeBazosData():
    urls = ["https://pc.bazos.cz/?hlokalita=&humkreis=0&cenaod=0&cenado=0", "https://mobil.bazos.cz/?hlokalita=&humkreis=0&cenaod=0&cenado=0"]
    urlNumber = 0
    scrapedUrls = 0
    cur = mysql.cursor()
    for url in urls:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")    
            items = soup.find_all("span", class_="vypis")
            for item in items:
                img = item.find("img", class_="obrazek")
                segment = item.find("span", class_="nadpis")
                heading = segment.find("a").text
                if "tren" in heading or "pozor" in heading:
                    continue
                try:
                    imgURL = img["src"]
                except:
                    imgURL = "static/placeholder.png"
                if urlNumber == 0:
                    URLforDB = "https://pc.bazos.cz" + segment.find("a")["href"]
                else:
                    URLforDB = "https://mobil.bazos.cz" + segment.find("a")["href"]
                cur.execute(f"SELECT EXISTS(SELECT * FROM items WHERE url = '{URLforDB}');")
                dbresponse = cur.fetchall()
                if dbresponse[0][0] == 0:
                    cur.execute(f"INSERT INTO items (url, imgurl, heading, bazar, public) VALUES ('{URLforDB}', '{imgURL}', '{heading}', 'bazos', 1);")
                    mysql.commit()
                    scrapedUrls += 1
        urlNumber += 1
    cur.execute(f"INSERT INTO logs (author, message) VALUES ('scraperscript', 'Scraped {scrapedUrls} URLs from bazos.');")
    mysql.commit()
    cur.close()
    
def deleteOldItems():
    cur = mysql.cursor()
    cur.execute("DELETE FROM items WHERE dateadded < NOW() - INTERVAL 1 WEEK;")
    cur.execute("INSERT INTO logs (author, message) VALUES ('scraperscript', 'Removed old items.');")
    mysql.commit()
    cur.close()


scrapeSbazarData(scrapeNewSbazarURLs())
scrapeBazosData()
deleteOldItems()