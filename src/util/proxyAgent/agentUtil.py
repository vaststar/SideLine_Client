from selenium import webdriver
from time import sleep
import re,os
from .Agent_911 import Agent_911

AmericanState={"AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
               "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
               "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
               "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New hampshire", "NJ": "New jersey",
               "NM": "New mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
               "PA": "Pennsylvania", "RI": "Rhode island", "SC": "South carolina", "SD": "South dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
               "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}

class AgentUtil(object):
    @staticmethod
    def changeIP(city=None, state='All', country="US",cityNoLimit=False):
        IPInfo = AgentUtil.get_IP_info()
        if IPInfo and IPInfo.get('city')==city:
            print('ip city match')
            return True
        while not Agent_911.changeIP(city, state, country,cityNoLimit):
            print('ip change faliure,restart change')
            sleep(1)
        sleep(5)
        IPInfo = AgentUtil.get_IP_info()
        if not IPInfo:
            print('cannot get ipaddress from whoer')
            return False
        print('ip is:',IPInfo)
        if cityNoLimit:
            if IPInfo.get('state').upper() == AmericanState.get(state).upper():
                print('ip match')
                return True
            print(" state doesn't match")
            return False
        else:
            if IPInfo.get('city')==city:
                print('ip match')
                return True
            print('not match city ', city)
            return False

    @staticmethod
    def get_IP_info():
        driverpath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
                                  , 'tool/webdriver', 'chromedriver_74.exe')
        options = webdriver.ChromeOptions()
        options.add_argument('--incognito')
        options.add_argument('--headless')
        chrome_driver = webdriver.Chrome(driverpath,chrome_options=options)
        chrome_driver.get('https://whoer.net')
        sleep(5)
        #获取当前ip，国家、省、市、邮编
        num=0
        while True:
            try:
                chrome_driver.find_element_by_xpath('//*[@id="main"]/section[1]/div/div/div/h1/strong')
                sleep(3)
                break
            except Exception as e:
                num+=1
                # chrome_driver.get('https://whoer.net')
                sleep(3)
                if num>3:
                    print("cannot detect ip")
                    return None
        try:
            print("start test ip info")
            anonymityStr = chrome_driver.find_element_by_xpath(
                '//*[@id="hidden_rating_link"]/span').text
            res = re.match(r'.*?(\d+).*?',anonymityStr)
            if res:
                anonymityNumber=res.group(1)
            ip = chrome_driver.find_element_by_xpath('//*[@id="main"]/section[1]/div/div/div/h1/strong').text
            country=chrome_driver.find_element_by_xpath(
                '//*[@id="main"]/section[5]/div/div/div/div[1]/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]/span/span[2]/span').text
            state = chrome_driver.find_element_by_xpath(
                '//*[@id="main"]/section[5]/div/div/div/div[1]/div[1]/div[1]/div[1]/div/div/div[2]/div[2]/div[2]/span').text
            city = chrome_driver.find_element_by_xpath(
                '//*[@id="main"]/section[5]/div/div/div/div[1]/div[1]/div[1]/div[1]/div/div/div[2]/div[3]/div[2]/span').text
            postalCode = chrome_driver.find_element_by_xpath(
                '//*[@id="main"]/section[5]/div/div/div/div[1]/div[1]/div[1]/div[1]/div/div/div[2]/div[4]/div[2]/span').text

            return {'country':country,'state':state,'city':city,'postalCode':postalCode,'anonymity':anonymityNumber,'ip':ip}
        except Exception as e:
            print('cannot detect ip info',e)
            return None