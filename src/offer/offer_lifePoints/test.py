import sys,os,time,xlrd,json
sys.path.append('.')
sys.path.append('..')
from selenium import webdriver
from src.offer import chromeName
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# driverpath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
#                            ,'tool/webdriver',chromeName)
# desire = DesiredCapabilities.CHROME
# desire['loggingPrefs'] = {'performance': 'ALL'}
# userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
# chrome_options = webdriver.ChromeOptions()
# prefs = {'profile.default_content_setting_values': {
#             "User-Agent": userAgent,  # 更换UA
#             "images": 2}
#         }
# chrome_options.add_experimental_option("prefs", prefs)
# chrome_options.add_argument('disable-infobars')
# chrome_options.add_argument('--incognito')
# if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)),'cache')):
#     os.makedirs(os.path.join(os.path.dirname(os.path.realpath(__file__)),'cache'), exist_ok=True)
# chrome_options.add_argument('--disk-cache-dir='+os.path.join(os.path.dirname(os.path.realpath(__file__)),'cache'))
# # chrome_options.add_argument('--headless')
# chrome_options.add_argument("--proxy-server=http://112.85.170.80:9999")
# chrome_driver = webdriver.Chrome(driverpath,desired_capabilities=desire,options=chrome_options)
# # 查看本机ip，查看代理是否起作用
# chrome_driver.get("http://httpbin.org/ip")
# chrome_driver.execute_script("window.open('https://www.lifepointspanel.com/login');")
# print(chrome_driver.page_source)
# # 退出，清除浏览器缓存
# time.sleep(100000)
# chrome_driver.quit()
# from src.util.proxyAgent import AgentUtil
#AgentUtil.changeIP('Anchorage','AK','US')
# print(AgentUtil.get_IP_info())
# from src.util.emailUtil import EmailUtil
# from src.offer.offer_lifePoints.lifeRequest import LifeReq
# aa=EmailUtil.getLink('suenroqovey@yahoo.com', 'sdtrblodsjcvwxbc', ('请验证您的会员资格','please verify your membership'),r'.*?(https://lifepointspanel.com/doi-by-email/account\?domain.*?)\".*?')
# aa=aa.replace("addressCheck=false","addressCheck=true")
# LifeReq().WriteActivateLink('19eafad282b111e99b0d0242ac180003',aa)
