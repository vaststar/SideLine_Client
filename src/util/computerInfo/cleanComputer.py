import os,time,win32gui, win32api, win32con

class CleanComputer(object):
    @staticmethod
    def RunCleanBat():
        os.system(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),'tool/CCleaner','clean.bat'))