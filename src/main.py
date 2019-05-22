import sys
sys.path.append('.')
sys.path.append('..')

from src.util.proxyAgent import AgentUtil
if __name__=='__main__':
    AgentUtil.changeIP()