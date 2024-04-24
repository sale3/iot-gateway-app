@echo off
copy .\src\logging.conf logging.conf
REM xcopy /E .\src\configuration configuration\
pytest
del logging.conf
del *.log
REM del configuration
REM rmdir configuration
