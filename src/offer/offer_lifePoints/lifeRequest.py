import random,string,datetime
import sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')
from src.offer import serverhost
from src.offer import MachineID
from src.util.httpRequest import HTTPRequest
from src.LogMoule import logger

class LifeReq(object):
    def __init__(self):
        self.host=serverhost
    def getUnRegisterInformation(self,country=("CHN",),number=None):
        print(country)
        '''获取number个未注册信息，number=none表示全部获取'''
        allEmails=HTTPRequest.get(self.host+"/emails/")['data']
        print('all email number',len(allEmails))
        allIdentities=HTTPRequest.get(self.host+"/identities/")['data']
        print('identity number',len(allIdentities))
        allBrowser=HTTPRequest.get(self.host+"/browsers/")['data']
        print('ua number',len(allBrowser))
        allErrors = HTTPRequest.get(self.host + "/lifepoints/errors/emails/")['data']
        print('error email number', len(allErrors))
        allAccounts= HTTPRequest.get(self.host + "/lifepoints/accounts/")['data']
        print('registered account number',len(allAccounts))
        allIdentityErrors = HTTPRequest.get(self.host + "/lifepoints/errors/identities/")['data']
        print('error address number', len(allIdentityErrors))
        #获取可用email
        emails=[]
        for emailInfo in allEmails:
            if number and len(emails)>=number:
                break
            isLegal=True
            for err in allErrors:
                if err['email_id']==emailInfo['email_id'] and err['error_type']=='-1':
                    isLegal=False
                    break
            if not isLegal:
                continue
            for account in allAccounts:
                if account['life_id']==emailInfo['email_id']:
                    isLegal=False
                    break
            if isLegal:
                emails.append(emailInfo)
        identities=[]
        allIdentities=list(filter(lambda x: x['country'] in country,allIdentities))#筛选国家
        allIdentityErrorID = []
        [allIdentityErrorID.append(i.get('identity_id')) for i in allIdentityErrors]
        allIdentities=list(filter(lambda x: x['identity_id'] not in allIdentityErrorID,allIdentities))#筛选无用身份
        for iden in allIdentities:
            if len(identities)==len(emails):
                break
            isLegal=True
            if iden['country'] not in country:
                continue
            for account in allAccounts:
                if account['identity_id'] == iden['identity_id']:
                    isLegal=False
                    break
            if isLegal:
                identities.append(iden)
        minLen=len(emails)-len(identities)
        if  minLen > 0 :
            if minLen <= len(allIdentities):
                identities+=random.sample(allIdentities,len(emails)-len(identities))
            else:
                for _ in range(minLen):
                    identities.append(random.choice(allIdentities))
        fiRes=[]
        for index in range(len(emails)):
            # 生成一个随机密码
            password = LifeReq.generatePassword()
            result = {}
            result.update(emails[index])
            result.update(identities[index])
            result.update(random.choice(allBrowser))
            result.update({"password": password})
            fiRes.append(result)
        return fiRes

    def RegNewAccount(self,email_id,password,identity_id,browser_id):
        '''注册一个账户，置为未激活状态'''
        result = HTTPRequest.post(self.host+"/lifepoints/accounts/",{"email_id":email_id,"password":password,"points":"0",
                                                                     "activate_state":"0","identity_id":identity_id,"browser_id":browser_id,
                                                                     "register_date":datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                                                                     "activate_link":"0"})
        return result['status']

    def WriteActivateLink(self,email_id,activate_link):
        '''补全激活链接'''
        result = HTTPRequest.put(self.host + "/lifepoints/accounts/activate_link/" + email_id,
                                 {"activate_link": activate_link})
        print(result)
        return result['status']

    def ActivateAccount(self,email_id):
        '''激活一个账户'''
        result = HTTPRequest.put(self.host+"/lifepoints/accounts/activate_states/"+email_id,{"activate_state":"1"})
        return result['status']
    def DeactivateAccount(self,email_id):
        '''失效一个账户'''
        result = HTTPRequest.put(self.host+"/lifepoints/accounts/activate_states/"+email_id,{"activate_state":"-1"})
        return result['status']
    def DoubleDeactivateAccount(self,email_id):
        '''彻底弄死一个账户'''
        result = HTTPRequest.put(self.host+"/lifepoints/accounts/activate_states/"+email_id,{"activate_state":"-2"})
        return result['status']
    def ChangeAccountPoints(self,email_id,points):
        '''修改一个账户的分数'''
        result = HTTPRequest.put(self.host+"/lifepoints/accounts/points/"+email_id,{"points":points})
        return result['status']

    def getAccountByID(self,email_id):
        return HTTPRequest.get(self.host+"/lifepoints/accounts/?id="+email_id)['data']
    def getAllAccount(self):
        return HTTPRequest.get(self.host + "/lifepoints/accounts/")['data']
    def getIdentityByID(self,identityid):
        return HTTPRequest.get(self.host+'/identities/?id='+identityid)['data']
    def getEmailByID(self,email_id):
        return HTTPRequest.get(self.host + "/emails/?id=" + email_id)['data']
    def getAllEmail(self):
        return HTTPRequest.get(self.host + "/emails/")['data']
#research
    def getTokenByReasarchID(self,researchid):
        '''根据调查id，获取调查token'''
        res = HTTPRequest.get(self.host+"/lifepoints/researches/"+researchid)
        if res['status']:
            return res['data']['project_token']
        return None

    def addResearch(self,researchid,project_token):
        return HTTPRequest.post(self.host+"/lifepoints/researches/",{"research_id":researchid,"project_token":project_token})
#jobs
    def getAvailableJob(self,country=("CHN",),number=None):
        '''获取一个已注册已激活，并且未在做任务的账号，用于做任务'''
        allAccounts = HTTPRequest.get(self.host + "/lifepoints/accounts/")['data']
        freeRes=[]
        doneRes=[]
        doneJob=[]
        busyRes=[]
        for account in allAccounts:
            if number and len(freeRes) >= number:
                break
            if account['activate_state'] != '1':
                continue
            #获取地址，查看是否是指定国家的
            identity = HTTPRequest.get(self.host + "/identities/?id=" + account['identity_id'])['data']
            if identity is None or identity['country'] not in country:
                continue
            job = HTTPRequest.get(self.host + "/lifepoints/jobs/" + account['life_id'])['data']
            account.update(identity)
            if not job:
                freeRes.append(account)
            elif  datetime.datetime.utcnow() > datetime.datetime.strptime(job['available_time'],'%Y-%m-%d %H:%M:%S'):
                if job.get('job_state')=='1':
                    busyRes.append(account)
                elif job.get('job_state')=='0':
                    doneRes.append(account)
                    doneJob.append(job)
        if number and len(freeRes) < number:
            if len(doneRes) >= (number-len(freeRes)):
                #取n个最久远的已完成任务
                doneJob.sort(key=lambda x:datetime.datetime.strptime(x['update_time'],'%Y-%m-%d %H:%M:%S'))
                doneJob=doneJob[:(number-len(freeRes))]
                jobIDs=[]
                [jobIDs.append(it['life_id']) for it in doneJob]
                [freeRes.append(it) for it in doneRes if it['life_id'] in jobIDs]
            else:
                #把已完成任务全部取出
                freeRes+=doneRes
        #开始补全信息
        result=[]
        for account in freeRes:
            emailInfo = HTTPRequest.get(self.host + "/emails/?id=" + account['life_id'])['data']
            if not emailInfo:
                continue
            ua = HTTPRequest.get(self.host + "/browsers/?id=" + account['browser_id'])['data']
            res={}
            res.update(account)
            res.update(emailInfo)
            if ua:
                res.update(ua)
            result.append(res)
        if number and len(result) < number:
            logger.info('no job available,please check the job table ,machine id:'+MachineID)
        return result

    def getJobByEmailAddr(self,emailaddress):
        '''根据邮箱地址、获取一个任务需要的信息'''
        emailInfo = HTTPRequest.get(self.host+"/emails/?address="+emailaddress)['data']
        if not emailInfo :
            return None
        accountInfo=HTTPRequest.get(self.host+"/lifepoints/accounts/?id="+emailInfo['email_id'])['data']
        if not accountInfo:
            return None
        ua = HTTPRequest.get(self.host + "/browsers/?id=" + accountInfo['browser_id'])['data']
        result={}
        result.update(emailInfo)
        result.update(accountInfo)
        result.update(ua)
        return result
    def getJobByID(self,emailid):
        '''根据邮箱地址、获取一个任务需要的信息,无视正在执行、地域等限制信息'''
        emailInfo = HTTPRequest.get(self.host+"/emails/?id="+emailid)['data']
        if not emailInfo :
            return None
        accountInfo=HTTPRequest.get(self.host+"/lifepoints/accounts/?id="+emailInfo['email_id'])['data']
        if not accountInfo:
            return None
        ua = HTTPRequest.get(self.host + "/browsers/?id=" + accountInfo['browser_id'])['data']
        result={}
        result.update(emailInfo)
        result.update(accountInfo)
        result.update(ua)
        return result

    def busyDoJob(self,life_id):
        '''将一个账号置为忙碌状态，禁止其他程序使用该账户'''
        HTTPRequest.put(self.host+"/lifepoints/jobs/?life_id="+life_id,{'job_state':'1','machine_id':MachineID})
    def freeDoJob(self,life_id):
        '''释放一个任务状态'''
        HTTPRequest.put(self.host + "/lifepoints/jobs/?life_id=" + life_id, {'job_state': '0','machine_id':MachineID})
    def freeMachine(self):
        '''释放一个机器对应的任务状态'''
        HTTPRequest.put(self.host + "/lifepoints/jobs/?machine_id=" + MachineID, {'job_state': '0'})
    def freeTimeOutJob(self,timeoutSecs=18000):
        job = HTTPRequest.get(self.host + "/lifepoints/jobs/")['data']
        for item in job:
            if (datetime.datetime.utcnow()-datetime.datetime.strptime(item['update_time'],'%Y-%m-%d %H:%M:%S')).seconds>=timeoutSecs:
                self.freeDoJob(item['life_id'])
    def setJobAvailableTime(self,life_id,nexthours):
        HTTPRequest.put(self.host + "/lifepoints/jobs/?life_id=" + life_id, {'available_time': nexthours})

#card
    def getAllCards(self):
        return HTTPRequest.get(self.host+"/lifepoints/cards/")['data']
    def getCardByOrderID(self,order_id):
        return HTTPRequest.get(self.host+"/lifepoints/cards/?id="+order_id)['data']
    def createJDOrder(self,order_id,card_price,email_id,order_date):
        return HTTPRequest.post(self.host+"/lifepoints/cards/",{'order_id':order_id,'card_number':'0','card_pin':'0','card_type':"JD",'card_price':card_price,
                                                                'expire_date':'0','card_status':"0",'email_id':email_id,'order_date':order_date,'card_date':'0'})
    def addJDCard(self,order_id,card_number,card_pin,card_price,expire_date,card_date):
        return HTTPRequest.put(self.host+"/lifepoints/cards/number_pin/"+order_id,{'card_number':card_number,'card_pin':card_pin,'card_price':card_price,
                                                                'expire_date':expire_date,'card_status':"1",'card_date':card_date})
    def doneJDCard(self,order_id):
        return HTTPRequest.put(self.host+"/lifepoints/cards/status/"+order_id,{'card_status':"2"})#0表示建卡,1表示卡到账，2表示已经转换
#error
    def getAllError(self):
        return HTTPRequest.get(self.host + "/lifepoints/errors/emails/")['data']
    def getErrorByEmailID(self,email_id):
        return HTTPRequest.get(self.host + "/lifepoints/errors/emails/?email_id="+email_id)['data']
    def addError(self,email_id,message,error_type):#0表示执行兑换后，并未在邮箱里找到订单号， -1表示邮箱被使用
        return HTTPRequest.post(self.host + "/lifepoints/errors/emails/",{'email_id':email_id,'message':message,'error_type':error_type})['data']

    # error
    def getAllIdentityError(self):
        return HTTPRequest.get(self.host + "/lifepoints/errors/identities/")['data']
    def getErrorByIdentityID(self, email_id):
        return HTTPRequest.get(self.host + "/lifepoints/errors/identities/?identity_id=" + email_id)['data']
    def addIdentityError(self, identity_id, message, error_type):  # 0表示无法切换ip到该地址对应的城市
        return HTTPRequest.post(self.host + "/lifepoints/errors/identities/",
                                {'identity_id': identity_id, 'message': message, 'error_type': error_type})['data']
    @staticmethod
    def generatePassword():
        lower = [random.choice(string.ascii_lowercase) for _ in range(2,5)]
        upper = [random.choice(string.ascii_uppercase) for _ in range(2,5)]
        digit = [random.choice(string.digits) for _ in range(2,5)]
        punct = [random.choice("!@#$%^&*") for _ in range(2,5)]
        password= lower+upper+digit+punct
        random.shuffle(password)
        return ''.join(password)

if __name__=="__main__":

    # LifeReq().busyDoJob(LifeReq().getAvailableJob()['life_id'])
    # print(LifeReq().getAvailableJob())
    # information = LifeReq().getOneUnRegisteredInformation()
    # print('find unregister ok',information)
    # if information is not None:
    #     print(LifeReq().RegNewAccount(information.get("email_id"),LifeReq.generatePassword(),information.get("identity_id"),information.get("browser_id")))
    #     LifeReq().ActivateAccount(information.get("email_id"))
    # print(LifeReq().getOneUnRegisteredInformation(("CHN",)))
    # LifeReq().RegNewAccount('f58eb79e633b11e9bb400242ac160003','Z@z123456','00a0fa36618c11e99cf30242ac190003','f05b40bc633b11e98ebb0242ac160003')
    # LifeReq().ActivateAccount('f58eb79e633b11e9bb400242ac160003')
    # print(LifeReq().getOneUnRegisteredInformation("CHN"))
    # print(LifeReq().getJobByEmailAddr("47029316@qq.com"))
    # LifeReq().RegNewAccount('ebd3ae1a63f611e98be60242ac120003', 'Z@z123456', 'dca4e2e6618b11e98c0b0242ac190003',
    #                         'f05b40bc633b11e98ebb0242ac160003')
    pass
    # print(LifeReq().getAvailableJob(country=("CHN",),number=2))

