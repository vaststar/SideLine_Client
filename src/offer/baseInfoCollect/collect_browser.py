import pandas,os,threadpool
import sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')
from src.offer import serverhost
from src.util.httpRequest import HTTPRequest

class BrowserCollecter(object):
    @staticmethod
    def removeCSVDuplicates():
        file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))),
                          'resource','ua.csv')
        df = pandas.read_csv(file)
        datalist = df.drop_duplicates()
        datalist.to_csv(file)
    @staticmethod
    def getCSVUserAgent():
        file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            'resource', 'ua.csv')
        df = pandas.read_csv(file)
        return df['User Agent']
    @staticmethod
    def writeOneUAToDB(ua):
        try:
            if len(ua)>15 and 'obile' not in ua and 'Linux' not in ua and 'linux' not in ua:
                HTTPRequest.post(serverhost + "/browsers/",{'ua':ua.replace("\"","")})
        except Exception as e:
            print(e)


if __name__=='__main__':
    # BrowserCollecter.removeCSVDuplicates()
    pool = threadpool.ThreadPool(20)
    requests=threadpool.makeRequests(BrowserCollecter.writeOneUAToDB,BrowserCollecter.getCSVUserAgent())
    [pool.putRequest(req) for req in requests]
    pool.wait()
