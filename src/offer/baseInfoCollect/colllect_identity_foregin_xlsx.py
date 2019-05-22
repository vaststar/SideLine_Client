import re,random,time,threadpool,xlrd,os
from urllib import request
from bs4 import BeautifulSoup
import sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')
from src.offer import serverhost
from src.util.httpRequest import HTTPRequest

class IdentityCollecter_US_XLSX(object):
    @staticmethod
    def getForeginIdentity(nameSet,country):
        '''到网站上爬外国人的信息'''
        try:
            gender=random.choice(['male','female'])
            url="https://www.fakenamegenerator.com/gen-{}-{}-{}.php".format(gender,nameSet.lower(),country.lower())
            header={'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
            req = request.Request(url=url, headers=header, method="GET")
            html = request.urlopen(req).read().decode('utf-8')
            soup = BeautifulSoup(html, "html.parser")

            birthday=None
            for item in soup.find('div',class_='extra').find_all('dl',class_='dl-horizontal'):
                if 'Birthday' in item.get_text():
                    birthday=item.find('dd').get_text()
                    birthday=time.strftime('%Y-%m-%d',time.strptime(birthday,'%B %d, %Y'))
                    birthday = re.sub(r'19[0-7]\d',lambda x:"19"+random.choice(["8","9"])+x[0][3],birthday)
            if birthday is None:
                print('no birthday')
                return None

            tag = soup.find('div',class_="address")
            name = tag.find('h3').get_text()
            firstName=None
            lastName=None
            if country.lower()=='us':
                namePa = re.match(r'(\w+)\s+[a-zA-Z\.]+\s+(\w+)',name)
                if namePa:
                    firstName=namePa.group(1)
                    lastName=namePa.group(2)
            elif country.lower()=='au':
                namePa = re.match(r'(\w+)\s+(\w+)', name)
                if namePa:
                    firstName = namePa.group(1)
                    lastName = namePa.group(2)
            if lastName is None or firstName is None:
                return None

            addr = tag.find('div',class_='adr')
            address=None
            city=None
            state=None
            zipcode=None
            if country.lower()=='us':
                for item in addr.children:
                    if '<br' not in str(item):
                        if ','not in str(item):
                            address = str(item).lstrip().rstrip()
                        else:
                            city=str(item).lstrip().rstrip().split(', ')[0]
                            state = str(item).lstrip().rstrip().split(', ')[1].split(' ')[0]
                            zipcode = str(item).lstrip().rstrip().split(', ')[1].split(' ')[1]
            elif country.lower()=='au':
                for item in addr.children:
                    if '<br' in str(item):
                        continue
                    addrPattern=re.compile(r'.*?[a-zA-Z]$')
                    cityPattern=re.compile(r'(.*?)\s+(\w+)\s+(\d+)$')
                    if addrPattern.match(str(item).lstrip().rstrip()):
                        address = str(item).lstrip().rstrip()
                    else:
                        res = cityPattern.match(str(item).lstrip().rstrip())
                        if res:
                            city = res.group(1)
                            state = res.group(2)
                            zipcode = res.group(3)
            if city is None or state is None or address is None:
                return None

            country= country.upper()
            print('ok:',lastName,firstName,gender,birthday,address,city,state,country,zipcode)
            #读取excel
            return address,city,state,zipcode,lastName,firstName,gender,birthday,country
            # return IdentityCollecter.writeOneIdentityToDB(lastName,firstName,gender,birthday,address,city,state,country,zipcode)
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def writeOneIdentityToDB(lastname,firstname,gender,birthday,address,city,state,country,zipcode):
        if lastname is None or firstname is None or gender is None or birthday is None or address is None or city is None or state is None or zipcode is None:
            return None
        return HTTPRequest.post(serverhost + "/identities/", dict(
            zip(("lastname", "firstname", "gender", "birthday", "address", "city", "state", "country", "zipcode"),
                (lastname,firstname,  gender, birthday, address, city, state, country, zipcode))))

    @staticmethod
    def readXLSX_ADDR():
        ExcelFile = xlrd.open_workbook(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))),
                         'resource',
                         'addr_ju.xlsx'))
        sheet = ExcelFile.sheet_by_index(0)
        accounts = []
        for i in range(1, sheet.nrows):
            temp = (sheet.cell_value(i, 0), sheet.cell_value(i, 1), sheet.cell_value(i, 2), sheet.cell_value(i, 3))
            accounts.append(temp)
        return accounts

if __name__=='__main__':
    #读取所有地址
    allAddr=IdentityCollecter_US_XLSX.readXLSX_ADDR()
    for item in allAddr:
        print(item)
        address, city, state, zipcode, lastName, firstName, gender, birthday, country=IdentityCollecter_US_XLSX.getForeginIdentity('us','us')
        IdentityCollecter_US_XLSX.writeOneIdentityToDB(lastName, firstName, gender, birthday, item[0], item[1], item[2], country,
                                               item[3])
