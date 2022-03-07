import requests
from bs4 import BeautifulSoup
import time
import json
import random
import string
from twocaptcha import TwoCaptcha
from loguru import logger
import threading


def auth(login):
    info = login.split(":")
    login = info[0]
    password = info[1]

    with open("settings.json", "r", encoding="utf-8") as file:
        global settings
        settings = json.load(file)

    ses = requests.session()

    headers = {
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
    }

    r = ses.get("https://web-coin.cc/signin", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    check = soup.find("input", {"name": "check"}).get("value")

    img = "https://web-coin.cc" + soup.find_all("img")[1].get("src")

    filename = ''.join(random.choice(string.ascii_lowercase +
                                     string.digits) for _ in range(9))
    r = ses.get(img, headers=headers)
    with open(f"captcha/{filename}.png", "wb") as file:
        file.write(r.content)

    solver = TwoCaptcha(settings["api"])
    result = solver.normal(f"captcha/{filename}.png")
    code = result["code"]
    logger.debug(code)
    payload = {
        "check": check,
        "email": login,
        "pass": password,
        "captcha": code
    }
    r = ses.post("https://web-coin.cc/signin", data=payload, headers=headers)

    start_mining = time.time() * 1000

    test = ses.get(
        f"https://web-coin.cc/AJAX/mining_control.php?action=start_mining&_={start_mining}", headers=headers).text

    if "error" not in str(test):
        logger.success(test)
    else:
        logger.critical(test)
        with open("error_acc.txt", "a+", encoding="utf-8") as file:
            file.write(f"\n{login}:123321asSs:{test}")

    cz = time.time() * 1000
    balance = ses.get(
        f"https://web-coin.cc/AJAX/mining_control.php?action=getBalance&_={cz}", headers=headers).json()
    balance_value = balance["coins"]

    response = ses.get(
        f"https://web-coin.cc/AJAX/mining_control.php?action=takeBonus&_={cz}", headers=headers).json()

    logger.debug(response)

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://web-coin.cc',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://web-coin.cc/account/speed_up?from_balance=true',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    params = (
        ('from_balance', 'true'),
    )

    data = {
        'act': 'pay'
    }

    response = ses.post(
        'https://web-coin.cc/account/speed_up?from_balance=true', headers=headers, params=params, data=data)

    logger.success("Успешно отправил запрос")


with open("accounts_rakhim.txt", "r", encoding="utf-8") as file:
    data = file.read().split()


for i in data:
    x = threading.Thread(target=auth, args=(i,)).start()
    time.sleep(1.5)

# for i in range(1, 506):
#     z = random.choice(data)
#     x = threading.Thread(target=auth, args=(z,)).start()
#     data.remove(z)
#     time.sleep(1)
