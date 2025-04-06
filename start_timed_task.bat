@echo off
setlocal

:: 设置默认值
set INTERVAL=60
set LOG_LEVEL=INFO
set SERVER=
set USERNAME=
set PASSWORD=

:: 解析命令行参数
:parse_args
if "%~1" == "" goto :done_args
if /i "%~1" == "-i" (
    set INTERVAL=%~2
    shift /1
    shift /1
    goto :parse_args
)
if /i "%~1" == "--interval" (
    set INTERVAL=%~2
    shift /1
    shift /1
    goto :parse_args
)
if /i "%~1" == "-l" (
    set LOG_LEVEL=%~2
    shift /1
    shift /1
    goto :parse_args
)
if /i "%~1" == "--log-level" (
    set LOG_LEVEL=%~2
    shift /1
    shift /1
    goto :parse_args
)
if /i "%~1" == "-s" (
    set SERVER=%~2
    shift /1
    shift /1
    goto :parse_args
)
if /i "%~1" == "--server" (
    set SERVER=%~2
    shift /1
    shift /1
    goto :parse_args
)
if /i "%~1" == "-u" (
    set USERNAME=%~2
    shift /1
    shift /1
    goto :parse_args
)
if /i "%~1" == "--username" (
    set USERNAME=%~2
    shift /1
    shift /1
    goto :parse_args
)
if /i "%~1" == "-p" (
    set PASSWORD=%~2
    shift /1
    shift /1
    goto :parse_args
)
if /i "%~1" == "--password" (
    set PASSWORD=%~2
    shift /1
    shift /1
    goto :parse_args
)
if /i "%~1" == "-h" (
    goto :display_help
)
if /i "%~1" == "--help" (
    goto :display_help
)

echo 未知参数: %~1
exit /b 1

:display_help
echo 使用方法: %0 [选项]
echo 选项:
echo   -i, --interval 秒数     设置定时任务的执行间隔，默认60秒
echo   -l, --log-level 级别     设置日志级别 (DEBUG, INFO, WARNING, ERROR)，默认INFO
echo   -s, --server 地址        设置服务器地址
echo   -u, --username 用户名    设置用户名
echo   -p, --password 密码      设置密码
echo   -h, --help               显示此帮助信息
exit /b 0

:done_args

:: 检查虚拟环境
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo 虚拟环境不存在，使用系统Python
)

:: 检查服务器地址、用户名和密码
set SERVER_ARGS=
if not "%SERVER%"=="" (
    if not "%USERNAME%"=="" (
        if not "%PASSWORD%"=="" (
            set SERVER_ARGS=--server "%SERVER%" --username "%USERNAME%" --password "%PASSWORD%"
        )
    )
)

echo ===== 启动 Train-Ticket 定时任务 =====
echo 间隔时间: %INTERVAL%秒
echo 日志级别: %LOG_LEVEL%
echo 开始时间: %date% %time%
echo =======================================

:: 启动定时任务
start /b python -m src.timed_task --interval "%INTERVAL%" --log-level "%LOG_LEVEL%" %SERVER_ARGS% > timed_task.log 2>&1

echo 定时任务已在后台启动
echo 日志保存在 timed_task.log

endlocal 