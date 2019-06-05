import sys,getopt,threadpool,re,os,shutil,time,mysql.connector
from urllib import request
sys.path.append('.')
sys.path.append('..')
from src.offer.offer_lifePoints.mainPage import MainPage
from src.offer.offer_lifePoints.register import RegisterPage
from src.offer.offer_lifePoints.lifeRequest import LifeReq
from src.offer.offer_lifePoints.dealCard import DealCard

from src.LogMoule import logger
from src.util.computerInfo import ComputerUtil
from src.util.proxyAgent import AgentUtil

class LifePointsRun(object):
    @staticmethod
    def writeAllToken():
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firef'}
        req = request.Request(url="http://track.rehealthylife.com/survey/config.txt", headers=header, method="GET")
        res = request.urlopen(req).read()
        pattern = re.compile('^(\d+).*?----([a-zA-Z0-9-]+)')
        for item in res.decode(encoding='utf-8').split('\r\n'):
            res = pattern.match(item)
            if res:
                LifeReq().addResearch(res.group(1), res.group(2))
    @staticmethod
    def writeAllToken_from_db():
        try:
            coon = mysql.connector.connect(host='66.98.122.107', port=3306, user='public', passwd='H8jB3p73Yhy6beyb',
                                           database='lpdata', autocommit=True)
            # 标准操作，查看player表的定义
            cursor = coon.cursor()
            cursor.execute('select * from tokentable;')
            res = cursor.fetchall()
            print('read tokentable ok')
            for item in res:
                if res:
                    LifeReq().addResearch(item[1],item[2])
        except Exception as e:
            print(e)

    @staticmethod
    def runOneJob(information,runTime,stayIP=False):
        if not stayIP and not AgentUtil.changeIP(city=information.get('city'), state=information.get('state'), country=information.get('country')):
            return None
        print('do job')
        MainPage(information).doJob(runTime)
        print('finish job')

    @staticmethod
    def runJob(jobCountry=("US",),jobNum=1,runTime=None,threadNum=1,stayInfo=False,stayIP=False,timeoutSec=24000,updateToken=False):
        if updateToken:
            print('update project token db')
            LifePointsRun.writeAllToken_from_db()
            print('update project token db finish')
        pool = threadpool.ThreadPool(threadNum)
        while True:
            #清空cache
            if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)),'cache')):
                shutil.rmtree(os.path.join(os.path.dirname(os.path.realpath(__file__)),'cache'))
            #清空超时任务
            LifeReq().freeTimeOutJob(timeoutSecs=timeoutSec)
            #清空本机器控制的任务
            LifeReq().freeMachine()
            try:
                accounts = LifeReq().getAvailableJob(country=jobCountry, number=jobNum)
                if not accounts:
                    continue
                for item in accounts:
                    LifeReq().busyDoJob(item['life_id'])
                # 创建多线程运行
                data = [((index, runTime, stayIP), None) for index in accounts]
                requests = threadpool.makeRequests(LifePointsRun.runOneJob, data)
                print(accounts)
                [pool.putRequest(req) for req in requests]
                pool.wait()
                print('thread finish')
                for item in accounts:
                    LifeReq().freeDoJob(item['life_id'])
            except Exception as e:
                print(e)
            finally:
                #清空本机器控制的任务
                LifeReq().freeMachine()
                if not stayInfo:
                    ComputerUtil.CleanAndChangeInfo()
                    return None

    @staticmethod
    def registerOne(information):
        registInformation=information
        if registInformation.get('country') != 'CHN':
            print('change ip to information:',information)
            #外国号注册时需换ip
            while not AgentUtil.changeIP(city=registInformation.get('city'), state=registInformation.get('state'), country=registInformation.get('country')):
                print('ip change failure,change another identity')
                time.sleep(1)
                LifeReq().addIdentityError(registInformation.get('identity_id'),'cannot change ip to city:'+registInformation.get('city'),'0')
                res = LifeReq().getUnRegisterInformation((registInformation.get('country'),),1)
                if not res:
                    print('there is no unregistered information')
                registInformation=res[0]
                print('change to :',registInformation)
                if not registInformation:
                    print('information none')
                    break
        if registInformation:
            RegisterPage().doJob(registInformation)
    @staticmethod
    def registerJob(regCountry=('US',),regNumber=None,threadNum=1):
        allInfo = LifeReq().getUnRegisterInformation(regCountry, regNumber)
        pool = threadpool.ThreadPool(threadNum)
        data = [((index,), None) for index in allInfo]
        requests = threadpool.makeRequests(LifePointsRun.registerOne, data)
        [pool.putRequest(req) for req in requests]
        pool.wait()

    @staticmethod
    def recheckOneAccount(account):
        if account['activate_state'] == '0':
            # 检查邮箱
            email = LifeReq().getEmailByID(account['life_id'])
            if email:
                print('重新检查激活邮箱：', email)
                RegisterPage().confirmRegister(email['email_id'], email['email_address'], email['email_auth_code'],
                                               ('请验证您的会员资格','please verify your membership'),
                                               r'.*?(https://lifepointspanel.com/doi-by-email/account\?domain.*?)\".*?')
        elif account['activate_state'] == '-1':
            # 再做一次任务，进行封号判断
            print('重新检查封号:', account['life_id'])
            info = LifeReq().getJobByID(account['life_id'])
            MainPage(info).reactivateAccount()

    @staticmethod
    def recheckAccounts(threadNum=1):
        #针对状态有问题的账号，重查一遍，防止遗漏，或者因为某次加载问题导致丢失账号
        allaccounts=LifeReq().getAllAccount()
        pool = threadpool.ThreadPool(threadNum)
        data = [((index,), None) for index in allaccounts]
        requests = threadpool.makeRequests(LifePointsRun.recheckOneAccount, data)
        [pool.putRequest(req) for req in requests]
        pool.wait()

    @staticmethod
    def checkOneEmailOrder(emailInfo):
        DealCard(emailInfo).getAllOrder()
    @staticmethod
    def recheckEmailOrder(threadNum=1,allEmail=False):
        #过滤无效邮箱
        fallEmail=[]
        if allEmail:
            allEmail = LifeReq().getAllEmail()
            for item in LifeReq().getAllAccount():
                for em in allEmail:
                    if em['email_id'] == item['life_id']:
                        fallEmail.append(em)
                        break
        else:
            allError = list(filter(lambda x:x['error_type']=='0',LifeReq().getAllError()))
            for item in allError:
                em = LifeReq().getEmailByID(item['email_id'])
                if em:
                    fallEmail.append(em)
        print('检测邮箱数量：',len(fallEmail))
        pool = threadpool.ThreadPool(threadNum)
        data = [((index,), None) for index in fallEmail]
        requests = threadpool.makeRequests(LifePointsRun.checkOneEmailOrder, data)
        [pool.putRequest(req) for req in requests]
        pool.wait()

    @staticmethod
    def checkOneEmailCard(card):
        emailInfo = LifeReq().getEmailByID(card['email_id'])
        if emailInfo:
            DealCard(emailInfo).startCheckEmail(card['order_id'])
    @staticmethod
    def checkJDCard(threadNum=1):
        allCards = LifeReq().getAllCards()
        pool = threadpool.ThreadPool(threadNum)
        data = [((index,), None) for index in allCards]
        requests = threadpool.makeRequests(LifePointsRun.checkOneEmailCard, data)
        [pool.putRequest(req) for req in requests]
        pool.wait()

if __name__=='__main__':
    try:
        options, arg = getopt.getopt(sys.argv[1:], "",['threadNum=','country=','register=','runjob=','runTime=','timeoutSec=','stayInfo','stayIP','recheckAccount','recheckOrder','checkAll','checkCard','updateDB'])
    except getopt.GetoptError:
        sys.exit()
    runType=-1
    runThread=1
    country=('CHN',)
    #注册参数（个数+线程数），个数为-1，表示全部做
    registerNum=None
    #做任务参数
    offerNumber=None
    offerDoTime=2
    sectimeout=24000
    keepIP=False
    keepInfo=False
    updateDB =False#是否更新token表
    #检查订单号参数
    checkAllEmail=False
    for name,value in options:
        if name in ('--register',):
            runType=0
            if int(value)==-1:
                registerNum=None
            else:
                registerNum =int(value)
        elif name in ('--runjob',):
            runType=1
            if int(value)==-1:
                offerNumber=None
            else:
                offerNumber =int(value)
        elif name in ('--recheckAccount',):
            runType=2
        elif name in ('--recheckOrder',):
            runType=3
        elif name in ('--checkCard',):
            runType=4
        elif name in ('--threadNum',):
            runThread=int(value)
        elif name in ('--country',):
            country = tuple(str(value).split(','))
        elif name in ('--runTime',):
            offerDoTime=int(value)
        elif name in ('--timeoutSec',):
            sectimeout=int(value)
        elif name in ('--stayIP',):
            keepIP=True
        elif name in ('--stayInfo',):
            keepInfo=True
        elif name in ('--checkAll',):
            checkAllEmail=True
        elif name in ('--updateDB',):
            updateDB=True

    if runType==0:
        print('cc',country)
        LifePointsRun.registerJob(regCountry=country,regNumber=registerNum,threadNum=runThread)
    elif runType==1:
        LifePointsRun.runJob(jobCountry=country,jobNum=offerNumber, runTime=offerDoTime, threadNum=runThread,
                             stayInfo=keepInfo,stayIP=keepIP,timeoutSec=sectimeout,updateToken=updateDB)
    elif runType==2:
        LifePointsRun.recheckAccounts(threadNum=runThread)
    elif runType==3:
        LifePointsRun.recheckEmailOrder(threadNum=runThread,allEmail=checkAllEmail)
    elif runType==4:
        LifePointsRun.checkJDCard(threadNum=runThread)



