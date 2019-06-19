import os,time,re,json,random
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

from src.offer import chromeName
from src.offer.offer_lifePoints.lifeRequest import LifeReq
from src.offer.offer_lifePoints.dealCard import DealCard
from src.LogMoule import logger
from src.offer.baseInfoCollect.collect_phone import GeneratePhone

class Exchange(object):
    def __init__(self,information):
        self.chrome_driver = None
        self.mainHandle = None
        self.information=information
        self.lifePoints=0

    def doJob(self,minPoints=2850):
        try:
            print('打开浏览器')
            self.initDriver(self.information.get('ua'))  # 初始化浏览器
            self.login(self.information.get('email_address'), self.information.get('password'))  # 登陆
            print('登陆成功')
            self.getLifePoints()#获取分数
            if self.lifePoints != self.information.get('points'):
                LifeReq().ChangeAccountPoints(self.information.get('life_id'), str(self.lifePoints))
            if self.lifePoints >= minPoints:
                logger.info('开始兑换：'+self.information['life_id'])
                self.startGetMoney()
        except Exception as e:
            print(e)
        finally:
            print('关闭浏览器')
            self.chrome_driver.quit()
            time.sleep(20)

    def initDriver(self,ua):
        '''初始化浏览器'''
        driverpath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
                           ,'tool/webdriver',chromeName)
        desire = DesiredCapabilities.CHROME
        desire['loggingPrefs'] = {'performance': 'ALL'}
        userAgent = ua
        if userAgent is None:
            userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'

        chrome_options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_setting_values': {
                    "User-Agent": userAgent,  # 更换UA
                    "images": 2}
                }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('disable-infobars')
        chrome_options.add_argument('--incognito')
        os.makedirs(os.path.join(os.path.dirname(os.path.realpath(__file__)),'cache'), exist_ok=True)
        chrome_options.add_argument('--disk-cache-dir='+os.path.join(os.path.dirname(os.path.realpath(__file__)),'cache'))
        # chrome_options.add_argument('--headless')
        self.chrome_driver = webdriver.Chrome(driverpath,desired_capabilities=desire,options=chrome_options)

    def login(self,email,password):
        '''登陆账号'''
        logNumber=0
        while True:
            if logNumber>=3:
                return
            logNumber+=1
            try:
                self.chrome_driver.get("https://www.lifepointspanel.com/login")
                self.mainHandle = self.chrome_driver.current_window_handle
                try:
                    WebDriverWait(self.chrome_driver, 5, 0.5).until(
                        EC.visibility_of_element_located((By.XPATH, '//*[@id="accept_all_cookies"]')))
                    self.chrome_driver.find_element_by_xpath('//*[@id="accept_all_cookies"]').click()
                except Exception as e:
                    print('未找到同意cookie按钮',e)
                finally:
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-contact-email"]').send_keys(email)
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-password"]').send_keys(password)
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-submit-button"]').click()
                    break
            except Exception as e:
                print('登陆失败，次数：',logNumber,e)
                self.chrome_driver.refresh()

    def getLifePoints(self):
        try:
            self.lifePoints = self.information.get('points')
            points=self.chrome_driver.find_element_by_xpath('/html/body/header/div/div[2]/div/section/ul/li[3]/a/strong').text
            self.lifePoints=int(points)
            print('lifepoints',points)
        except Exception as e:
            logger.info('未找到分数值，诡异的情况，尽量人工查一下,账号：' + self.information['life_id'])
            print('未找到分数值',e)

    def startGetMoney(self):
        handles = self.chrome_driver.window_handles
        self.chrome_driver.execute_script("window.open('about:blank');")
        while True:
            temp = set(self.chrome_driver.window_handles) - set(handles)
            if len(temp) > 0:
                self.chrome_driver.switch_to.window(temp.pop())
                self.chrome_driver.get('https://www.lifepointspanel.com/member/redeempoints')
                break
        if self.information.get("country")=="CHN":
            self.chrome_driver.get('https://www.perksplus.com/PerksPlusV2/Secure/RewardZone/ProductDetail.aspx?ProductID=b009c8e7-944f-40b8-94a9-153285e75346')
        else:
            self.chrome_driver.get("https://www.perksplus.com/PerksPlusV2/Secure/RewardZone/ProductDetail.aspx?ProductID=1e06d4d3-7be4-440f-b049-c8c5cf1dc0f5")
        time.sleep(5)

        addToXPath='//*[@id="ctl00_ContentPlaceHolder1_AddToCartButton"]'
        WebDriverWait(self.chrome_driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, addToXPath)))
        self.chrome_driver.find_element_by_xpath(addToXPath).click()
        withXPath='//*[@id="ctl00_ContentPlaceHolder1_proceedToCheckOutButton"]'
        WebDriverWait(self.chrome_driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, withXPath)))
        self.chrome_driver.find_element_by_xpath(withXPath).click()
        time.sleep(5)
        try:
            useAddr='//*[@id="ctl00_ContentPlaceHolder1_ViewShippingAddress1_shippingAddressRepeater_ctl00_useThisShippingAddressButton"]'
            self.chrome_driver.find_element_by_xpath(useAddr).click()
            time.sleep(2)
        except Exception as e:
            try:
                self.chrome_driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ViewShippingAddress1_createNewAddressLink"]').click()
                time.sleep(3)
                identity=LifeReq().getIdentityByID(self.information['identity_id'])
                try:
                    name='//*[@id="ctl00_ContentPlaceHolder1_EditShippingAddress1_fullNameTextBox"]'
                    self.chrome_driver.find_element_by_xpath(name).send_keys(identity['firstname'])
                except Exception as e:
                    pass
                addr1='//*[@id="ctl00_ContentPlaceHolder1_EditShippingAddress1_addressLine1TextBox"]'
                self.chrome_driver.find_element_by_xpath(addr1).send_keys(identity['address'])
                city='//*[@id="ctl00_ContentPlaceHolder1_EditShippingAddress1_cityNameTextBox"]'
                self.chrome_driver.find_element_by_xpath(city).send_keys(identity['city'])
                state='//*[@id="ctl00_ContentPlaceHolder1_EditShippingAddress1_stateNameTextBox"]'
                self.chrome_driver.find_element_by_xpath(state).send_keys(identity['state'])
                zipcode='//*[@id="ctl00_ContentPlaceHolder1_EditShippingAddress1_zipCodeTextBox"]'
                self.chrome_driver.find_element_by_xpath(zipcode).send_keys(identity['zipcode'])
                phone='//*[@id="ctl00_ContentPlaceHolder1_EditShippingAddress1_phoneNumberTextBox"]'
                self.chrome_driver.find_element_by_xpath(phone).send_keys(GeneratePhone.generatePhone_CHN())
                self.chrome_driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_EditShippingAddress1_useThisShippingAddressButton"]').click()
                time.sleep(3)
            except Exception as e:
                print(e)
        try:
            self.chrome_driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_placeOrderButton"]').click()
            logger.info('兑换成功：'+self.information['life_id'])
            #去邮箱获取订单号
            time.sleep(20)
            if not DealCard(self.information).getFirstOrder():
                #说明未取到当前的兑换订单，记录一下，
                logger.error('去邮箱查找订单号失败:'+self.information['email_id'])
                LifeReq().addError(self.information['email_id'],'已经兑换，但是并未查找到邮件，可能邮箱有问题，建议手动查看','0')
        except Exception as e:
            logger.error('兑换失败：'+self.information['life_id']+' 请自行查看，或者等待下一轮任务兑换')
            print(e)


if __name__=='__main__':
    data={'activate_state': '1', 'browser_id': 'f05b40bc633b11e98ebb0242ac160003', 'identity_id': 'dca4e2e6618b11e98c0b0242ac190003', 'life_id': 'ebd3ae1a63f611e98be60242ac120003', 'password': 'Z@z123456', 'points': '5650', 'email_address': '863640218@qq.com', 'email_auth_code': 'qqimbapmaqbdbefj', 'email_id': 'ebd3ae1a63f611e98be60242ac120003', 'email_password': 'ZZT06118115', 'ua': {'browser_id': 'f05b40bc633b11e98ebb0242ac160003', 'ua': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.19.2883.75 Safari/537.36'}}
    Exchange(data).doJob()

