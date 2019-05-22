import sys,getopt,threadpool,random
sys.path.append('.')
sys.path.append('..')
from src.offer.baseInfoCollect.collect_email import EmailCollecter
from src.offer.baseInfoCollect.collect_browser import BrowserCollecter
from src.offer.baseInfoCollect.collect_identity_chinese import CollectCHAddr
from src.offer.baseInfoCollect.collect_identity_foregin import IdentityCollecter
from src.offer.baseInfoCollect.colllect_identity_foregin_xlsx import IdentityCollecter_US_XLSX

class BaseInfoRun(object):
    @staticmethod
    def collect_UA(threadNum=1):
        pool = threadpool.ThreadPool(threadNum)
        requests=threadpool.makeRequests(BrowserCollecter.writeOneUAToDB,BrowserCollecter.getCSVUserAgent())
        [pool.putRequest(req) for req in requests]
        pool.wait()
    @staticmethod
    def collect_email(threadNum=1):
        pool = threadpool.ThreadPool(threadNum)
        allEmail = EmailCollecter.getExcelEmail()
        data = [(index,None) for index in allEmail]
        requests=threadpool.makeRequests(EmailCollecter.writeOneEmailToDB,data)
        [pool.putRequest(req) for req in requests]
        pool.wait()
    @staticmethod
    def collect_Chinese_Identity(collctNum=None,threadNum=1):
        pool = threadpool.ThreadPool(threadNum)
        allPos = CollectCHAddr.getPosition()
        if collctNum and len(allPos)>collctNum:
            allPos=random.sample(allPos,collctNum)
        data = [((index,), None) for index in allPos]
        requests = threadpool.makeRequests(CollectCHAddr.getOneAddr, data)
        [pool.putRequest(req) for req in requests]
        pool.wait()
    @staticmethod
    def collect_Foregin_Identity(collctNum=1000,country=('us',),threadNum=1):
        def makeName(countries):
            coun=random.choice(countries)
            return coun,coun
        pool = threadpool.ThreadPool(threadNum)
        data = [(makeName(country), None) for _ in range(collctNum)]
        requests = threadpool.makeRequests(IdentityCollecter.getForeginIdentity, data)
        [pool.putRequest(req) for req in requests]
        pool.wait()
if __name__=="__main__":
    # BaseInfoRun.collect_Foregin_Identity(collctNum=1,country=('us',))
    try:
        options, args = getopt.getopt(sys.argv[1:], "",['threadNum=','email','ua','identity_chn=','identity_en=','country='])
    except getopt.GetoptError:
        sys.exit()
    runType=-1
    runThread=1
    #中文个人信息参数
    identityNum_CHN=-1
    #外文个人信息参数
    identityNum_EN=1000
    country_en=('us',)

    for name,value in options:
        if name in ('--threadNum',):
            runThread=int(value)
        elif name in ('--email',):
            runType=0
        elif name in ('--ua',):
            runType = 1
        elif name in ('--identity_chn',):
            runType = 2
            if int(value)==-1:
                identityNum_CHN=None
            else:
                identityNum_CHN =int(value)
        elif name in ('--identity_en',):
            runType = 3
            if int(value)!=-1:
                identityNum_EN =int(value)
        elif name in ('--country',):
            country_en=tuple(str(value).split(','))
    if runType==0:
        BaseInfoRun.collect_email(threadNum=runThread)
    elif runType==1:
        BaseInfoRun.collect_UA(threadNum=runThread)
    elif runType==2:
        BaseInfoRun.collect_Chinese_Identity(collctNum=identityNum_CHN)
    elif runType==3:
        # BaseInfoRun.collect_Foregin_Identity(collctNum=identityNum_EN,country=country_en,threadNum=runThread)
        allAddr = IdentityCollecter_US_XLSX.readXLSX_ADDR()
        for item in allAddr:
            print(item)
            address, city, state, zipcode, lastName, firstName, gender, birthday, country = IdentityCollecter_US_XLSX.getForeginIdentity(
                'us', 'us')
            IdentityCollecter_US_XLSX.writeOneIdentityToDB(lastName, firstName, gender, birthday, item[0], item[1],
                                                           item[2], country,
                                                           item[3])


