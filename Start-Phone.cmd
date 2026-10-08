@echo off
cd /d "%~dp0"
echo Phone mode exposes the helper to your LAN. Use a trusted private network only.
python server.py --phone
pause
