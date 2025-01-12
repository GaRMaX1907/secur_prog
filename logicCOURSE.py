import requests
from bs4 import BeautifulSoup
import time


class Course:
    def get_currency_rate():
        url = "https://www.google.com/search?q=курс+доллара+к+рублю"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        result = soup.find("div", class_="BNeawe iBp4i AP7Wnd").get_text()
        return float(result.replace(",", "."))
    
if __name__ == '__main__':
    current_rate = Course
    print(f"Текущий курс валюты: {current_rate}")
    while True:
        time.sleep(5)
        new_rate = Course
        if abs(new_rate - current_rate) > 2:
            print(f"Сильное изменение курса валюты! Старое значение: {current_rate}, новое значение: {new_rate}")
            current_rate = new_rate