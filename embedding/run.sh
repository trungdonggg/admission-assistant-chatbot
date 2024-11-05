
export PYTHONPATH=$(dirname "$(pwd -P)")

pip install -r requirements.txt

python3 app.py

