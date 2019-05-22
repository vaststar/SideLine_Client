from .cleanComputer import CleanComputer
from .changeComputer import ChangeInfo

class ComputerUtil(object):
    @staticmethod
    def CleanAndChangeInfo():
        CleanComputer.RunCleanBat()
        ChangeInfo.RunChange()