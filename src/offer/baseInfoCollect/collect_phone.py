import random
class GeneratePhone(object):
    @staticmethod
    def generatePhone_CHN():
        prelist = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139", "147", "150", "151", "152",
                   "153", "155", "156", "157", "158", "159", "186", "187", "188", "189"]
        return random.choice(prelist)+''.join(random.sample('0123456789',8))
if __name__=='__main__':
    [print(GeneratePhone.generatePhone_CHN()) for _ in range(20)]