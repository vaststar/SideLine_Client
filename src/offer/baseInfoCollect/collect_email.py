import os,xlrd,threadpool
import sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')
from src.offer import serverhost
from src.util.httpRequest import HTTPRequest

class EmailCollecter(object):
    @staticmethod
    def getExcelEmail():
        ExcelFile = xlrd.open_workbook(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))), 'resource',
                         'email.xlsx'))
        sheet = ExcelFile.sheet_by_index(0)
        accounts = []
        for i in range(1, sheet.nrows):
            temp = (sheet.cell_value(i, 0), sheet.cell_value(i, 1))
            accounts.append(temp)
        return accounts

    @staticmethod
    def getTXTEmail():
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))), 'resource',
                         'email.txt'),'r') as f:
            accounts = []
            for lines in f.readlines():
                lines=lines.replace("\\n","").replace("\\r","")
                accounts.append(tuple(lines.split('----')))
        return accounts

    @staticmethod
    def writeOneEmailToDB(emailaddress,emailpassword,authcode=None):
        if authcode is None:
            authcode=emailpassword
        print(emailaddress,emailpassword,authcode)
        return HTTPRequest.post(serverhost + "/emails/",
                                {"address": emailaddress, "password": emailpassword, "authcode": authcode})

if __name__=='__main__':
    pool = threadpool.ThreadPool(100)
    allEmail = EmailCollecter.getExcelEmail()
    data = [(index,None) for index in allEmail]
    requests=threadpool.makeRequests(EmailCollecter.writeOneEmailToDB,data)
    [pool.putRequest(req) for req in requests]
    pool.wait()
    pass

