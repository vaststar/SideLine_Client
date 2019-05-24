cd /d %~dp0
call .\venv\Scripts\activate
cd ..\src
python .\offer\offer_lifePoints\run.py --threadNum=5 --country=US --runjob=40 --runTime=2 --timeoutSec=18000