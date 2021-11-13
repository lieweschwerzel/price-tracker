import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import smtplib, time
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

product_id = "ALPECIN"
query = "https://www.ah.nl/zoeken?query="
HOURS = 1
SLEEPTIME = HOURS * 3600  # 3600 seconds in 1 hour

def main():
    price = check_price()
    print(product_id + " " + price)
    # =============================================================================
    # KEEP SEARCHING EVERY X HOURS until "1+1 gratis" offer is found, send email, detain heroku ps:scale worker=1
    # =============================================================================
    while True:    
        if has_one_plus_one():
            print("1 + 1 gratis")
            send_gmail(price)
            break
        else:
            print("{!s} has no 1+1 offer, trying again in {:d} hours".format(product_id, HOURS))
            time.sleep(SLEEPTIME)

def check_price():    
    htmldata = get_data(query + product_id)
    soup = BeautifulSoup(htmldata, 'html.parser')
    regex = re.compile('price_highlight')
    price = ""
    for data in soup.find("div", {"class" : regex}):
        price += data.get_text()
    return price


    # link for extract html data
def get_data(url):
    r = requests.get(url)
    return r.text

def has_one_plus_one():
    htmldata = get_data(query + product_id)
    soup = BeautifulSoup(htmldata, 'html.parser')
    regex = re.compile('shield_root')    
    for data in soup.findAll("div", {"class" : regex}):
        if data.get_text() == "1 + 1 gratis":
            return True
        else: 
            return False

def send_gmail(price):
    gmail_user = 'lieweschwerzel@gmail.com'
    recipient = 'lieweschwerzel@gmail.com'
    gmail_app_password = os.environ.get("PASSWORD")    
    # =============================================================================
    # SET THE INFO ABOUT THE EMAIL
    # =============================================================================
    FROM = gmail_user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = product_id + " " + price + ": 1 + 1 GRATIS!!"
    TEXT = query + product_id
    # =============================================================================
    # Prepare actual message
    # =============================================================================
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_app_password)
    server.sendmail(FROM, TO, message)
    server.close()
    print('Email sent!')


if __name__ == '__main__':
    main()