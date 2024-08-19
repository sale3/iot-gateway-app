cp ./src/logging.conf logging.conf
coverage run -m pytest
rm -rf logging.conf
rm -rf *.log