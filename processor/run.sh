export PYTHONPATH=$(dirname "$(pwd -P)")

apt install uvicorn

pip install --upgrade -r requirements.txt

uvicorn app:app --reload --host 0.0.0.0 --port 7000
