cd /d %~dp0
call .\venv\Scripts\activate
cd ..\src
python .\offer\baseInfoCollect\run.py --threadNum=10 --identity_en=1000 --country=us,au