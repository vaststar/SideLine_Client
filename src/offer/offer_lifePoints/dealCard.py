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
from src.util.emailUtil import EmailUtil
from src.offer.offer_lifePoints.lifeRequest import LifeReq

class DealCard(object):
    def __init__(self,information):
        self.information=information

    def startCheckEmail(self,order_id):
        allRes = EmailUtil.getEmail(self.information['email_address'], self.information['email_auth_code'], ('来自 Perks 的电子证书',)
                                    ,onlyUnsee=False,findAll=True)
        if allRes is None or allRes == []:
            print('cannot find jd card:', self.information['email_address'])
            return False
        pattern=re.compile(r'.*?title>(\w+).*?(\d+)\sRMB.*?Card#:\s+(\w+)\s+PIN:\s+([a-zA-Z0-9-]+).*?(\d{4}-\d{2}-\d{2}).*?Expiration.*?')
        for head,body in allRes:
            for item in body:
                print('find jd card :',self.information['email_address'])
                res=pattern.match(item.replace('\r\n','').replace('\n',''))
                if res:
                    cardInfo=LifeReq().getCardByOrderID(res.group(1))
                    print('update jd card',res.group(1),cardInfo)
                    if cardInfo and cardInfo.get('card_status') =='0':
                        print(res.group(1),res.group(3),res.group(4),res.group(2),res.group(5),head[-1])
                        LifeReq().addJDCard(res.group(1),res.group(3),res.group(4),res.group(2),res.group(5),head[-1])
                    if order_id==res.group(1):
                        return True
                    break
        return False

    def getFirstOrder(self):
        try:
            allRes = EmailUtil.getEmail(self.information['email_address'], self.information['email_auth_code'], ('来自LifePoints的订购确认',)
                                        ,onlyUnsee=True,findAll=False)
            if allRes is None or allRes == []:
                print('cannot find order:', self.information['email_address'])
                return False
            pattern=re.compile(r'.*?您的订单号.*?">(\w+)<.*?')
            for head,body in allRes:
                for item in body:
                    res=pattern.match(item.replace('\r\n','').replace('\n',''))
                    print(head)
                    if res:
                        cardInfo = LifeReq().getCardByOrderID(res.group(1))
                        if not cardInfo:
                            result=LifeReq().createJDOrder(res.group(1),'25',self.information['email_id'],head[-1])
                            return result['status']
                        else:
                            print('already in database')
            return False
        except Exception as e:
            print('get first order',self.information['email_address'],e)
            return False
    def getAllOrder(self):
        try:
            print(self.information)
            allRes = EmailUtil.getEmail(self.information['email_address'], self.information['email_auth_code'], ('来自LifePoints的订购确认',)
                                        ,onlyUnsee=False,findAll=True)
            if allRes is None or allRes == []:
                print('cannot find order:', self.information['email_address'])
                return False
            pattern=re.compile(r'.*?您的订单号.*?">(\w+)<.*?')
            for head,body in allRes:
                for item in body:
                    res=pattern.match(item.replace('\r\n','').replace('\n',''))
                    if res:
                        cardInfo = LifeReq().getCardByOrderID(res.group(1))
                        if not cardInfo:
                            LifeReq().createJDOrder(res.group(1), '25', self.information['email_id'], head[-1])
                        else:
                                print('already in database')
        except Exception as e:
            print('get first order',self.information['email_address'],e)

if __name__=='__main__':
    #扫描邮箱
    # data={'email_address': '285765981@qq.com', 'email_auth_code': 'kkakwrbkqkjfcaac', 'email_id': 'f58eb79e633b11e9bb400242ac160003', 'email_password': 'ZZT06118115'}
    # print(DealCard(data).getFirstOrder())
    allCards=LifeReq().getAllCards()

    for card in allCards:
        email=LifeReq().getEmailByID(card['email_id'])
        if email:
            DealCard(email).startCheckEmail(card['order_id'])
            # DealCard(email).getFirstOrder()
