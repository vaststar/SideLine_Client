cd /d %~dp0
call .\venv\Scripts\activate
cd ..\src
python .\offer\offer_lifePoints\test.py
pause