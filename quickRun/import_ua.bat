cd /d %~dp0
call .\venv\Scripts\activate
cd ..\src
python .\offer\baseInfoCollect\run.py --threadNum=10 --ua