# start.sh

export FLASK_APP=run.py
export FLASK_DEBUG=1
export APP_CONFIG_FILE=config.py
python3 -m flask run
