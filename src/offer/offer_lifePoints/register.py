import os,time,random,threadpool
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

from src.util.emailUtil import EmailUtil
from src.offer.offer_lifePoints.lifeRequest import LifeReq
from src.offer import chromeName

from src.LogMoule import logger

from src.offer.offer_lifePoints.mainPage import MainPage
class RegisterPage(object):
    def __init__(self):
        self.chrome_driver = None
        self.mainHandle = None
        self.AmericanState={"AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New hampshire", "NJ": "New jersey", "NM": "New mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode island", "SC": "South carolina", "SD": "South dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}
    
    def doJob(self,information):
        try:
            self.initDriver(information['ua'])
            if self.register(information):
                print('注册成功，开始写入数据库')
                if not LifeReq().RegNewAccount(information.get('email_id'),information.get('password'),information.get('identity_id'),information.get('browser_id')):
                    print('写入数据库失败,邮箱id为：',information.get('email_id'))
                    return
                print('写入数据库成功,开始查找邮箱激活链接')
                #打开邮箱验证
                time.sleep(10)
                if self.confirmRegister(information.get('email_id'),information.get('email_address'),information.get('email_auth_code'),
                                     ('请验证您的会员资格','please verify your membership'),r'.*?(https://lifepointspanel.com/doi-by-email/account\?domain.*?)\".*?'):
                    MainPage(information).doJob(1)
        except Exception as e:
            print(e)
        finally:
            try:
                self.chrome_driver.quit()
            except Exception as e:
                print(e)

    def initDriver(self,ua=None):
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
        self.chrome_driver = webdriver.Chrome(driverpath,desired_capabilities=desire,options=chrome_options)
    
    def register(self,information):
        '''一个邮箱尝试注册5次，失败就放弃'''
        num = 0
        while True:
            if num > 5:
                return False
            num += 1
            try:
                self.chrome_driver.get('https://www.lifepointspanel.com/registration')
                refreshNumber=0
                while True:
                    refreshNumber+=1
                    if refreshNumber>3:
                        return False
                    if 'Registration | LifePoints' in self.chrome_driver.title:
                        break
                    else:
                        time.sleep(4)
                        self.chrome_driver.refresh()
                try:
                    time.sleep(5)
                    self.chrome_driver.find_element_by_xpath('//*[@id="accept_all_cookies"]').click()
                    time.sleep(1)
                except Exception as e:
                    print(e)
                finally:
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-first-name--2"]').send_keys(information['firstname'])
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-last-name--2"]').send_keys(information['lastname'])
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-email-address--4"]').send_keys(information['email_address'])
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-confirm-email-address--2"]').send_keys(information['email_address'])
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-password--4"]').send_keys(information['password'])
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-password-confirm--3"]').send_keys(information['password'])
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-nextbutton--2"]').click()
                    time.sleep(3)
                    Select(self.chrome_driver.find_element_by_xpath('//*[@id="edit-gender--2"]')).select_by_value(information['gender'][0].upper())  # 实例化Select
                    month = information['birthday'].split('-')[1]
                    day = information['birthday'].split('-')[2]
                    year = information['birthday'].split('-')[0]
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-date-of-birth--2"]').send_keys(year)
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-date-of-birth--2"]').send_keys(month)
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-date-of-birth--2"]').send_keys(day)
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-mailing-address1--2"]').send_keys(information['address'])
                    stateEle = Select(self.chrome_driver.find_element_by_xpath('//*[@id="edit-state--2"]'))
                    try:
                        if information['country'] != "CHN":
                            stateEle.select_by_visible_text(self.AmericanState.get(information['state']))
                        else:
                            stateEle.select_by_visible_text(information['state'])
                    except Exception as e:
                        print(e)
                        stateEle.select_by_index(random.randint(1,len(stateEle.options)))
                    time.sleep(3)
                    if information['country'] != "CHN":
                        self.chrome_driver.find_element_by_xpath('//*[@id="edit-city--2"]').send_keys(
                            information['city'])
                    else:
                        cityEle=Select(self.chrome_driver.find_element_by_xpath('//*[@id="edit-city--2"]'))
                        try:
                            cityEle.select_by_visible_text(information['city'])
                        except Exception as e:
                            print(e)
                            cityEle.select_by_index(random.randint(1,len(cityEle.options)))
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-postal-code--2"]').send_keys(information['zipcode'])
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-nextbutton1--2"]').click()
                    time.sleep(3)
                    # page3
                    self.chrome_driver.find_element_by_xpath(
                            '//*[@id="lp-registration-form--2"]/div[3]/div[1]/div[1]/label/span').click()
                    self.chrome_driver.find_element_by_xpath(
                        '//*[@id="lp-registration-form--2"]/div[3]/div[1]/div[3]/label/span').click()
                    self.chrome_driver.find_element_by_xpath(
                        '//*[@id="lp-registration-form--2"]/div[3]/div[1]/div[5]/label/span').click()
                    self.chrome_driver.find_element_by_xpath(
                        '//*[@id="lp-registration-form--2"]/div[3]/div[1]/div[7]/label/span').click()
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-submit--2"]').click()
                    try:
                        WebDriverWait(self.chrome_driver, 5, 0.5).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, 'alert-danger')))
                        errorMessage=self.chrome_driver.find_element_by_class_name('alert-danger').text
                        if '已经存在' in errorMessage:
                            print(errorMessage)
                            #记录该邮箱，废弃
                            LifeReq().addError(information['email_id'], '该邮箱已经被其他用户注册', '-1')
                            logger.error('注册失败，该邮箱似乎已经被其他人注册,账号：'+information['email_id'])
                        return False
                    except Exception as e:
                        logger.error('注册失败，原因未知,账号：' + information['email_id'])
                        print(e)
                    time.sleep(5)
                    if 'pending' not in self.chrome_driver.current_url:
                        logger.error('注册失败，原因未知,账号：' + information['email_id'])
                        print('注册出错了')
                        return False
                    return True
            except Exception as e:
                logger.error('注册失败，原因未知,账号：' + information['email_id'])
                print(e)
                return False

    def confirmRegister(self,emailid,address,emailpassword,title,urlPattern):
        url = EmailUtil.getLink(address, emailpassword, title, urlPattern)
        if url:
            url.replace("addressCheck=false","addressCheck=true")
            try:
                if not self.chrome_driver:
                    self.initDriver()
                self.chrome_driver.get(url)
                LifeReq().ActivateAccount(emailid)
                time.sleep(5)
                print('账号激活成功：',address)
                return True
            except Exception as e:
                print('账号激活失败：',address)
                logger.error('账号激活失败，账号：'+emailid)
                print(e)
                return False

if __name__=='__main__':
    #{'email_address': '47029316@qq.com', 'email_auth_code': 'rvueixjdbjeb', 'email_id': 'f58af82061750242ac160003', 'email_password': 'ZZ115', 'address': '酒泉市玉门市', 'birthday': '1982-08-21', 'city': '酒泉市', 'country': 'CHN', 'firstname': '似', 'gender': 'male', 'identity_id': '00b90644618c11e98c0b0242ac190003', 'lastname': '吕', 'state': '甘肃省', 'zipcode': '735000', 'browser_id': 'f1012a18633b11e98d1d0242ac160003', 'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari', 'password': '9&td$PK0jO0!'}
    allInfo=LifeReq().getUnRegisterInformation(("US",),None)
    for a in allInfo:
        RegisterPage().doJob(a)

    # information={'email_address': 'ScottMedina6Z@yahoo.com', 'email_auth_code': '7omO8iCG', 'email_id': '36a86a9a667011e997b30242ac120003'}
    # RegisterPage().confirmRegister(information.get('email_id'), information.get('email_address'),
    #                      information.get('email_auth_code'),
    #                      ('请验证您的会员资格',), r'.*?(https://lifepointspanel.com/doi-by-email/account\?domain.*?)\".*?')

    print('注册完毕')
