
from twocaptcha import TwoCaptcha
import json
import time
import requests
from bs4 import BeautifulSoup
import coloredlogs
import verboselogs
import sys
import string
import random
import threading

# 503049
with open("settings.json", "r", encoding="utf-8") as file:
    settings = json.load(file)

api_key = settings["api"]
referal = settings["ref"]

level_styles = {'debug': {'color': 8},
                'info': {},
                'warning': {'color': 11},
                'error': {'color': 'red'},
                'critical': {'bold': True, 'color': 'red'},

                'spam': {'color': 'green', 'faint': True},
                'verbose': {'color': 'blue'},
                'notice': {'color': 'magenta'},
                'success': {'bold': True, 'color': 'green'},
                }

logfmtstr = "%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s"
logfmt = coloredlogs.ColoredFormatter(logfmtstr, level_styles=level_styles)

logger = verboselogs.VerboseLogger("Benefix")

coloredlogs.install(fmt=logfmtstr, stream=sys.stdout, level_styles=level_styles,
                    milliseconds=True, level='DEBUG', logger=logger)


def main():
    ses = requests.session()

    headers = {
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": f"https://web-coin.cc/?i={referal}",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
    }
    r = ses.get(f"https://web-coin.cc/?i={referal}", headers=headers)
    time.sleep(1)

    r = ses.get("https://web-coin.cc/register", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    reg_control = soup.find("input", {"name": "reg_control"}).get("value")
    img = "https://web-coin.cc" + soup.find_all("img")[1].get("src")

    email = ''.join(random.choice(string.ascii_lowercase + string.digits)
                    for _ in range(9)) + "@mail.ru"
    filename = ''.join(random.choice(string.ascii_lowercase +
                                     string.digits) for _ in range(9))
    r = ses.get(img, headers=headers)
    with open(f"{filename}.png", "wb") as file:
        file.write(r.content)

    solver = TwoCaptcha(api_key)
    result = solver.normal(f"{filename}.png")
    code = result["code"]

    logger.success("Успешно создал аккаунт!")
    logger.notice(
        f'code: {result["code"]} | email: {email} | password: 123321asSs')

    data = {
        "reg_control": reg_control,
        "email":  email,
        "first_name": "bot_rakhim",
        "last_name": "bot_rakhim",
        "pass": "123321asSs",
        "repass": "123321asSs",
        "captcha": result["code"]
    }

    response = ses.post("https://web-coin.cc/register",
                        headers=headers, data=data)

    time.sleep(1)
    start_mining = time.time() * 1000

    test = ses.get(
        f"https://web-coin.cc/AJAX/mining_control.php?action=start_mining&_={start_mining}", headers=headers)

    logger.debug(test.text)

    with open("accounts.txt", "a+", encoding="utf-8") as file:
        file.write(f"\n{email}:123321asSs")

    logger.verbose("УСПЕХ")


for i in range(1, 120):
    time.sleep(3)
    threading.Thread(target=main).start()
