from bs4 import BeautifulSoup
import requests

#get list of urls
#check if urls already in DB
#go through remaining urls
#get item header
#get item picture url
#save all to DB
def scrapeSbazar():
    url = "https://www.sbazar.cz/30-elektro-pocitace/cela-cr/zdarma?cena-dohodou=bez"
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("li", class_="c-item c-item--uw")
        urls = []
        for item in items:
            anchor = item.find("a", class_="c-item__link")
            urls.append(anchor["href"])

scrapeSbazar()