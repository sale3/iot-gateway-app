@echo off
copy .\src\logging.conf logging.conf
xcopy /E .\src\configuration configuration\
pytest
del logging.conf
del *.log
del configuration
rmdir configuration
