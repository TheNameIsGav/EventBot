reg query "hkcu\software\Python"

if ERRORLEVEL 1 goto NoPython

echo Python Installed: Installing packages
pip install discord.py
pip install -U python-dotenv
git clone https://github.com/TheNameIsGav/EventBot.git
cd "EventBot"
run.bat
goto:eof

:NoPython
echo No Python Installed 
echo or 
echo Python Path and Python Scripts Path not added to Path Variable

echo Done
pause