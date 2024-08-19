copy .\src\logging.conf logging.conf
coverage run -m pytest
del logging.conf
del *.log