@echo off
echo Starting APEX Trading System...
echo.
echo [1/3] Starting Python backend...
start "APEX Python" cmd /k "cd /d C:\Users\USER\Desktop\APEX && python apex/apex_core.py"
timeout /t 3
echo [2/3] Starting API server...
start "APEX API" cmd /k "cd /d C:\Users\USER\Desktop\APEX && node apex/api/server.js"
timeout /t 2
echo [3/3] Starting dashboard...
start "APEX Dashboard" cmd /k "cd /d C:\Users\USER\Desktop\APEX\apex\dashboard\dashboard-wireframe && npm run dev"
echo.
echo APEX is starting up...
echo Dashboard will be at: http://localhost:5173
echo API server at: http://localhost:3001
echo.
pause
