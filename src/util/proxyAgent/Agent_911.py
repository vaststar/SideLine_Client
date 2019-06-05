import os,win32gui
from time import sleep
from .windowOperate import windowOperate

class Agent_911(object):
    @staticmethod
    def changeIP(city=None, state='All', country="US",cityNoLimit=False):
        if Agent_911.login_911():
            sleep(10)
            return Agent_911.ip_new(city, state, country,cityNoLimit)
        return False

    @staticmethod
    def login_911():
        '''
        auto login 911 after 911 client opened
        '''
        num = 0
        while True:
            #根据进程名称获取进程id
            handle=windowOperate.get_handle_by_process_name("Client.exe")
            if handle:
                break
            num+=1
            sleep(1)
            if num==1:
                os.system('start '+os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
                                                os.path.abspath(__file__))))),'tool/911S5','Client.exe'))
            if num >= 10:
                print('911 start failure')
                return False
        if Agent_911.isAlreadyLogin():
            return True
        #progress
        sleep(1)
        while True:
            progressHandle=win32gui.FindWindowEx(handle, 0, "ProgressBar20WndClass", None)
            print(progressHandle,win32gui.IsWindowVisible(progressHandle))
            if not progressHandle or not win32gui.IsWindowVisible(progressHandle):
                break
            print('wait for progress hidden')
            sleep(1)
        while True:
            subHandle = win32gui.FindWindowEx(handle, 0, "ThunderRT6CommandButton", "Login")
            if not subHandle or not win32gui.IsWindowVisible(subHandle):
                break
            print('try click login and wait login hidden')
            Agent_911.kill_OK()
            try:
                progressHandle=win32gui.FindWindowEx(handle, 0, "ProgressBar20WndClass", None)
                if not progressHandle or not win32gui.IsWindowVisible(progressHandle):
                    windowOperate.click_position(subHandle, 10, 10)
            except Exception as e:
                print(e)
            sleep(1)
        sleep(10)
        return Agent_911.isAlreadyLogin()

    @staticmethod
    def isAlreadyLogin():
        handle = windowOperate.get_handle_by_process_name("Client.exe")
        num = 0
        while True:
            if num >= 5:
                print('not login')
                return False
            num += 1
            if win32gui.FindWindowEx(handle, 0, "ThunderRT6CommandButton", "Change Server"):
                print('already login')
                return True
            sleep(1)

    @staticmethod
    def kill_OK():
        '''
        click ok button after get server failed,if there is this button
        '''
        try:
            calssname = u"#32770"
            titlename = u"Client"
            hwnd = win32gui.FindWindow(calssname, titlename)
            handle_ok = win32gui.FindWindowEx(hwnd, 0, "Button", None)
            if hwnd != 0:
                windowOperate.click_position(handle_ok, 10, 10)
        except Exception as e:
            print(e)


    @staticmethod
    def ip_new(city=None, state='All', country="US",cityNoLimit=False):
        print('Changing Ip')
        if city is None or len(city)<1:
            arg = ' -changeproxy/' + country
        else:
            if cityNoLimit:
                arg = ' -changeproxy/' + country + '/' + state + '/' + city+'/ -citynolimit'
            else:
                arg = ' -changeproxy/' + country + '/' + state + '/' + city
        print('changing ip ....')
        try:
            if not os.system(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
                                                os.path.abspath(__file__))))),'tool/911S5/ProxyTool','AutoProxyTool.exe')
                      + arg):
                sleep(6)
                print('change ip  success')
                return True
            else:
                print('change ip failed')
                return False
        except Exception as e:
            print(e)
            return False

