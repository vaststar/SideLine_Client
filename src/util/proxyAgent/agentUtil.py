from selenium import webdriver
from time import sleep
import re,os
from .Agent_911 import Agent_911

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
        print('test ip address ')
        IPInfo = AgentUtil.get_IP_info()
        if not IPInfo:
            print('cannot get ipaddress from whoer')
            return False
        if IPInfo.get('city')==city:
            print('ip city match')
            return True
        elif cityNoLimit:
            stateAll=IPInfo.get('state').split(' ')
            stateSim=''
            for i in stateAll:
                stateSim+=i[0]
            return stateSim==state
        else:
            print('ip is',IPInfo)
            print('not ',city)
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
            print("开始检测ip信息")
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
            print(e)
            return None