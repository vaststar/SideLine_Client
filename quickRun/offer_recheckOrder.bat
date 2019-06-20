cd /d %~dp0
call .\venv\Scripts\activate
cd ..\src
python .\offer\offer_lifePoints\run.py --threadNum=10 --recheckOrder --checkAll