import os,win32gui
from time import  sleep
from .windowOperate import windowOperate
class ChangeInfo(object):
    @staticmethod
    def RunChange():
        os.system('start '+os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                                        'tool/WindowsChanger','changer.exe'))
        num=0
        while True:
            if num >= 10:
                return
            #根据进程名称获取进程id
            sleep(0.5)
            handle=windowOperate.get_handle_by_process_name("changer.exe")
            title = win32gui.GetWindowText(handle)
            num+=1
            if title:
                break
        # # 一键修改
        handle_modify = win32gui.FindWindowEx(handle, 0, 'Button', '一键修改')
        if not handle_modify:
            return
        windowOperate.click_position(handle_modify, 10, 10)
        sleep(15)
        # 重启电脑
        handle_modify = win32gui.FindWindowEx(handle, 0, 'Button', '重启电脑')
        if not handle_modify:
            return
        windowOperate.click_position(handle_modify, 10, 10)