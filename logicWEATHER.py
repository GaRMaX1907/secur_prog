import requests
from bs4 import BeautifulSoup
import time

class Weather:
    def get_weater():
        url = "https://www.google.com/search?q=погода"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        result = soup.find("span", class_="wob_t q8U8x").get_text()
        return float(result.replace(",", "."))