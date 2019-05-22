import sys
sys.path.append('.')
sys.path.append('..')

from src.util.proxyAgent.agentUtil import AgentUtil


if __name__=='__main__':
    AgentUtil.changeIP(city='ALL', state='All', country="CN")
    AgentUtil.get_IP_info()