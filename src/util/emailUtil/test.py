import sys
sys.path.append('.')
sys.path.append('..')
from src.util.emailUtil import EmailUtil

if __name__=='__main__':
    '''提供邮件收取、发送功能'''
    # print(EmailUtil.getLink('thomas_land@163.com', 'shouquanma1',('请验证您的会员资格',),r'.*?(https://lifepointspanel.com/doi-by-email/account\?domain.*?)\".*?'))
    # EmailUtil.sendEmail("测试发送 <BerthaThomasFZ@aol.com>", 'SUw9UgLh',
    #                       ["测试接收1 <47029316@qq.com>", "测试接收2 <285765981@qq.com>"],
    #                       "标题", "内容")
    # EmailUtil.sendEmail("测试发送 <lid0lv72@21cn.com>", 'Dhu4368969',
    #                                           ["测试接收1 <lid0lv72@21cn.com>"],
    #                                           "标题", "内容")
    print(EmailUtil.getLink('yuquql4523@21cn.com', '2d30654a', ('请验证您的会员资格',),
                            r'.*?(https://lifepointspanel.com/doi-by-email/account\?domain.*?)\".*?'))
    # EmailUtil.getEmail('lid0lv72@21cn.com','Dhu4368969',('标题',),)