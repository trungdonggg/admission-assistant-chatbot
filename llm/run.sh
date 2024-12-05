export PYTHONPATH=$(dirname "$(pwd -P)")

apt install uvicorn

pip install -r requirements.txt

uvicorn app:app --reload --port 5001
