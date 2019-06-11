import os,time,re,json,random
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import threading
import sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

from src.offer import chromeName
from src.offer.offer_lifePoints.lifeRequest import LifeReq
from src.offer.offer_lifePoints.exchange import Exchange
from src.LogMoule import logger

class MainPage(object):
    def __init__(self,information):
        self.chrome_driver = None
        self.mainHandle = None
        self.allSearchLink=[]
        self.information=information

    def doJob(self,doNumber=1):
        #自动循环做任务，先初始化浏览器、登陆、获取所有任务链接、打开所有链接、查询日志、获取tableid、构造并打开秒杀链接
        # LifeReq().busyDoJob(self.information.get('life_id'))
        currentNumber = 0
        while True:
            if doNumber is not None:
                if int(doNumber) <= currentNumber:
                    print('job number finish')
                    break
            exchangeThread=None
            currentNumber+=1
            try:
                print('open chrome')
                self.initDriver(self.information.get('ua'))#初始化浏览器
                self.login(self.information.get('email_address'),self.information.get('password'))#登陆
                if self.checkActivate():#做封号判断
                    self.doFirstLogin()#进行初次完整化信息
                    print('login success')
                    points=self.getLifePoints(self.information.get('life_id'))#获取分数
                    if points is not None:
                        if points != self.information.get('points'):
                            # 写入数据库
                            LifeReq().ChangeAccountPoints(self.information.get('life_id'), points)
                        if int(points) > 2850:
                            exchangeThread = threading.Thread(target=Exchange(self.information).doJob,args=(2850,))
                            logger.info('get into duihuan:'+self.information['life_id'])
                            exchangeThread.start()
                    self.dealAllSearch()#处理所有调查链接

                else:
                    self.reactivateAccount()

            except Exception as e:
                print('do job error',self.information,e)
            finally:
                print('close chrome')
                self.chrome_driver.quit()
                if exchangeThread:
                    exchangeThread.join()
                time.sleep(20)

    def reactivateAccount(self):
        try:
            print('open chrome')
            self.initDriver(self.information.get('ua'))  # 初始化浏览器
            activateNum=0
            while activateNum<2:
                activateNum += 1
                self.chrome_driver.get(self.information.get('activate_link'))
                if self.checkActivate(firstCheck=False):
                    return True
            return False
        except Exception as e:
            print('reactivate error:',e)
            return False

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
        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)),'cache')):
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
                    print('no cookie button',e)
                finally:
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-contact-email"]').send_keys(email)
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-password"]').send_keys(password)
                    self.chrome_driver.find_element_by_xpath('//*[@id="edit-submit-button"]').click()
                    break
            except Exception as e:
                print('login error ,try number:',logNumber,e)
                self.chrome_driver.refresh()
    def checkActivate(self,firstCheck=True):
        '''检测是否封号'''
        try:
            WebDriverWait(self.chrome_driver, 5, 0.5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'alert-danger')))
            errorMessage = self.chrome_driver.find_element_by_class_name('alert-danger').text
            if '失效' in errorMessage or 'sorry' in errorMessage or 'Sorry' in errorMessage:
                print(errorMessage)
                logger.info('accout login error,please check life_points_account status==-1'+self.information['life_id'])
                #将状态置为-1
                if firstCheck:
                    LifeReq().DeactivateAccount(self.information['life_id'])
                else:
                    LifeReq().DoubleDeactivateAccount(self.information['life_id'])
                return False
            else:
                if self.information['activate_state'] != '1':
                    LifeReq().ActivateAccount(self.information['life_id'])
                print('account detect normal.')
                return True
        except Exception as e:
            if self.information['activate_state']!='1':
                LifeReq().ActivateAccount(self.information['life_id'])
            print('account detect normal.')
            return True

    def doFirstLogin(self):
        try:
            time.sleep(3)
            self.chrome_driver.switch_to.frame('survey-iframe')

            try:
                peopleNumberXPath='//*[@id="sq-testsw-container-HH_SIZE_qartstool"]/div/div/div/div/div/div[2]/div/div/div/div/div/div[2]/div/div/div[2]/div[1]/div[7]/span'
                WebDriverWait(self.chrome_driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, peopleNumberXPath)))
                self.chrome_driver.find_element_by_xpath(peopleNumberXPath).click()
            except Exception as e:
                print('no family memeber number',e)
            try:
                self.chrome_driver.find_element_by_xpath('//*[@id="btn_continue"]').click()
                self.chrome_driver.find_element_by_xpath('//*[@id="sq-testsw-container-HH_SIZE"]/div[3]').click()
            except Exception as e:
                print('no continue',e)
            try:
                self.chrome_driver.find_element_by_xpath('//*[@id="sq-testsw-container-HH_MEMBERS_qartstool"]/div/div/div[1]/div[1]/div/div[2]').click()
                self.chrome_driver.find_element_by_xpath('//*[@id="sq-testsw-container-HH_MEMBERS_qartstool"]/div/div/div[1]/div[3]/div/div[2]').click()
                self.chrome_driver.find_element_by_xpath('//*[@id="sq-testsw-container-HH_MEMBERS"]/div[3]').click()
            except Exception as e:
                print('no live with who',e)
            try:
                childNumberXPath='//*[@id="sq-testsw-container-NUMBER_OF_CHILDREN_qartstool"]/div/div/div/div[4]/div/div[2]'
                WebDriverWait(self.chrome_driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, childNumberXPath)))
                self.chrome_driver.find_element_by_xpath(childNumberXPath).click()
            except Exception as e:
                print('no child number',e)
            try:
                self.chrome_driver.find_element_by_xpath('//*[@id="sq-testsw-container-HISPANIC_DESCENT_qartstool"]/div/div/div/div[2]/div/div[2]').click()
            except Exception as e:
                print('no country ques',e)

            try:
                self.chrome_driver.find_element_by_xpath('//*[@id="sq-testsw-container-RACE_qartstool"]/div/div/div/div[1]/div/div[2]').click()
            except Exception as e:
                print('no color ques',e)
            try:
                incomeXPath=None
                if self.information['country']=='US':
                    incomeXPath='//*[@id="sq-testsw-container-HH_INCOME_US_qartstool"]/div/div/div[1]/div[14]/div/div[2]'
                elif self.information['country']=="CHN":
                    incomeXPath='//*[@id="sq-testsw-container-HH_Income_CN_qartstool"]/div/div/div[2]/div[4]/div/div[2]'
                WebDriverWait(self.chrome_driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, incomeXPath)))
                self.chrome_driver.find_element_by_xpath(incomeXPath).click()
            except Exception as e:
                print('no income',e)
            try:
                okXPath='/html/body/div[2]/div/section/article/div/div/div[2]/div/div[2]/p/button'
                WebDriverWait(self.chrome_driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, okXPath)))
                self.chrome_driver.find_element_by_xpath(okXPath).click()
                time.sleep(10)
            except Exception as e:
                print('no confirm',e)
        except Exception as e:
            print('not firt login',e)
        finally:
            self.chrome_driver.switch_to.default_content()

    def getLifePoints(self,life_id):
        try:
            points=self.chrome_driver.find_element_by_xpath('/html/body/header/div/div[2]/div/section/ul/li[3]/a/strong').text
            print('points:',points)
            return points
        except Exception as e:
            print('cannot find lifepoints,check manually',e)
            logger.info('cannot find points:'+self.information['life_id'])
            return None

    def getAllSearchLink(self):
        '''获取所有链接'''
        self.allSearchLink.clear()
        try:
            self.chrome_driver.switch_to.window(self.chrome_driver.window_handles[0])
            lineList = self.chrome_driver.find_elements_by_class_name('survey-id')
            if lineList:
                lineIter = iter(lineList)
                while True:
                    try:
                        link1 = next(lineIter).get_attribute('survey-link')
                        while not link1:
                            link1 = next(lineIter).get_attribute('survey-link')
                        sur1 = next(lineIter).text
                        if sur1 and link1:
                            self.allSearchLink.append((link1, sur1))
                    except Exception as e:
                        break
        except Exception as e:
            print('no new research',e)

        try:
            eles=self.chrome_driver.find_element_by_xpath('//*[@id="panel"]/div/section/div/div/div[1]/div/div/div/table/tbody')
            for item in eles.find_elements_by_tag_name('tr'):
                pa=item.find_elements_by_tag_name('td')[1]
                self.allSearchLink.append((pa.find_element_by_class_name('start-new-survey').get_attribute('survey-link'), pa.find_elements_by_tag_name('small')[0].text))

            eles=self.chrome_driver.find_element_by_xpath('//*[@id="panel"]/div/section/div/div/div[1]/div/div[1]/div/table/tbody')
            for item in eles.find_elements_by_tag_name('tr'):
                pa = item.find_elements_by_tag_name('td')[1]
                self.allSearchLink.append((pa.find_element_by_class_name('start-new-survey').get_attribute('survey-link'),
                                           pa.find_elements_by_tag_name('small')[0].text))

            eles=self.chrome_driver.find_element_by_xpath('//*[@id="panel"]/div/section/div/div/div[1]/div/div[2]/div/table/tbody')
            for item in eles.find_elements_by_tag_name('tr'):
                pa = item.find_elements_by_tag_name('td')[1]
                self.allSearchLink.append((pa.find_element_by_class_name('start-new-survey').get_attribute('survey-link'),
                                           pa.find_elements_by_tag_name('small')[0].text))
        except Exception as e:
            print('no doing research',e)

        if self.allSearchLink:
            random.shuffle(self.allSearchLink)
            print('find research:')
            [print(i) for i in self.allSearchLink]


    def dealAllSearch(self):
        '''打开所有链接，如果崩溃，则默认全部重新开始'''
        # self.chrome_driver.refresh()

        self.getAllSearchLink()  # 获取所有任务链接
        if len(self.allSearchLink) > 0:
            for item in self.allSearchLink:
                try:
                    self.openOneLink(item)
                except Exception as e:
                    print('open research link error:',item,e)

            self.getAllSearchLink()  # 获取所有任务链接
            if len(self.allSearchLink) < 3:
                LifeReq.setJobAvailableTime(self.information.get('life_id'), 72)
        else:
            print('no research')
            LifeReq.setJobAvailableTime(self.information.get('life_id'), 72)
            return


    def openOneLink(self,link):
        '''打开一个任务'''
        print('start research:',link)
        handles = self.chrome_driver.window_handles
        self.chrome_driver.switch_to.window(handles[-1])
        self.chrome_driver.execute_script("window.open('about:blank');")

        while True:
            temp = set(self.chrome_driver.window_handles) - set(handles)
            if len(temp) > 0:
                self.chrome_driver.switch_to.window(temp.pop())
                self.chrome_driver.get(link[0])
                break
        #通过查找链接，找到秒杀链接，暂时弃用，改成通过查找token表中对应的surveyid匹配秒杀链接
        #self.doCurrentOne()
        tokenID = LifeReq().getTokenByReasarchID(link[1])
        if not tokenID:
            print('can not find matched token,survey id is:',link[1])
            return
        print('find token:',tokenID,'survey id is:',link[1])
        ProjectPatternURL = 'https://s.cint.com/Survey/Complete?ProjectToken={}'
        miaoLink=ProjectPatternURL.format(tokenID)
        self.finishOpen((miaoLink,))

    def doCurrentOne(self):
        allLink = self.getBrowserLinks()
        FingerPrint=None
        for item in allLink:
            res = re.match(r'.*?Fingerprint/([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})$',item,re.M|re.I)
            if res:
                FingerPrint=res.group(1)
                break
        # if FingerPrint is not None:
        print('finger print id:',FingerPrint)
        urlLinks = MainPage.getFinalLink(allLink,FingerPrintID=FingerPrint)
        if len(urlLinks) > 0:
            self.finishOpen(urlLinks)

    def getBrowserLinks(self):
        '''获取浏览器所有日志'''
        time.sleep(10)
        num=0
        urlLinks=[]
        try:
            while True:
                time.sleep(2)
                currentLog = self.chrome_driver.get_log('performance')
                if num >8:
                    break
                if len(currentLog) < 1:
                    num+=1
                else:
                    num=0
                    for item in currentLog:
                        if json.loads(item['message'])['message']['method']=='Network.responseReceived':
                            url = json.loads(item['message'])['message']['params']['response']['url']
                            # logger.info(url)
                            if url is None or url ==[] or url =='' or '.css' in url or '.js' in url or '.ico' in url:
                                continue
                            urlLinks.append(url)
        except Exception as e:
            print('log read error:',e)
        finally:
            return urlLinks

    @staticmethod
    def getFinalLink(urls,FingerPrintID=None):
        resultUrlLink=[]
        ProjectPattern = re.compile(
            r'.*?([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})&.*?([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}(-[a-z0-9]{4})?-[a-z0-9]{12})'
        )
        ProjectPatternURL = 'https://s.cint.com/Survey/Complete?ProjectToken={}&ids={}'
        YougovPattern = re.compile(
            r'.*?yougov.com/(.*?)'
        )
        YougovPatternURL = 'http://stop.yougov.com/thanks/{}'
        CHMPattern = re.compile(
            r'.*?CHM_(\d{6})_([a-zA-Z0-9]{16}).*?([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})'
        )
        CHMPatternURL = 'http://www.globaltestmarket.com/20/survey/finished.phtml?ac={}&sn={}&lang=E&gh={}'
        EPattern = re.compile(
            r'.*?E_(\d{6})_([a-zA-Z0-9]{16}).*?([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})'
        )
        EPatternURL = 'http://www.globaltestmarket.com/20/survey/finished.phtml?ac={}&sn={}&lang=E&gh={}'
        Patterns=[(YougovPattern,YougovPatternURL,[1]),
                  (CHMPattern,CHMPatternURL,[1,2,3]),(EPattern,EPatternURL,[1,2,3]),
                  (ProjectPattern, ProjectPatternURL, [2, 1])]
        for url in urls:
            print(url)
            for item in Patterns:
                res = item[0].match(url)
                if res:
                    print('find url:', url)
                    logger.info('research url:'+url)
                    template = item[1]
                    li = []
                    for i in item[2]:
                        li.append(res.group(i))
                    matched=template.format(*li)
                    logger.info('miaosha url:'+matched)
                    if matched not in resultUrlLink:
                        resultUrlLink.append(matched)
        return resultUrlLink

    def finishOpen(self,urls):
        '''打开秒杀链接'''
        for url in urls:
            print("open final link after 120s")
            try:
                time.sleep(120)
                print("open final link:",url)
                handles = self.chrome_driver.window_handles
                self.chrome_driver.switch_to.window(handles[-1])
                self.chrome_driver.get(url)
                # self.chrome_driver.execute_script("window.open('{}');".format(url))
                print("final link open donw, continue after 30s")
                time.sleep(30)
            except Exception as e:
                print('open final link error:',url,e)

if __name__=='__main__':
    # MainPage(oneByone=True).doJob("285765981@qq.com","Z@z123456",doNumber=10)#.doJob("TalonHart5L@aol.com", "zd6J^9h!c")#
    data = LifeReq().getJobByID("36ee0d5c667011e995620242ac120003")
    MainPage(data).doJob(1)
    time.sleep(10000)
