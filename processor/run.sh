export PYTHONPATH=$(dirname "$(pwd -P)")

pip install -r requirements.txt

uvicorn app:app --reload --port 7000
