@echo off
REM 定时任务启动脚本 - Windows版本

REM 设置默认参数
set INTERVAL=%1
if "%INTERVAL%"=="" set INTERVAL=60

set LOG_LEVEL=%2
if "%LOG_LEVEL%"=="" set LOG_LEVEL=INFO

REM 检查虚拟环境
if exist .venv\Scripts\activate.bat (
    echo 激活虚拟环境...
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 输出启动信息
echo ===== 启动 Train-Ticket 定时任务 =====
echo 间隔时间: %INTERVAL%秒
echo 日志级别: %LOG_LEVEL%
echo 开始时间: %date% %time%
echo =======================================

REM 启动定时任务
python -m src.timed_task --interval %INTERVAL% --log-level %LOG_LEVEL%

REM 如果命令异常退出，输出错误信息
if %ERRORLEVEL% NEQ 0 (
    echo 定时任务异常退出，请检查日志获取详细信息
    exit /b 1
)

REM 退出虚拟环境
if defined VIRTUAL_ENV (
    deactivate
) 