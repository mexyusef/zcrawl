@echo off
echo Running ZCrawl application...

python -m zcrawl

if %ERRORLEVEL% NEQ 0 (
    echo Error running ZCrawl application!
) else (
    echo ZCrawl application closed successfully.
)
