export PYTHONPATH="$HOME/ttu-chatbot"

pip install -r requirements.txt

uvicorn app:app --reload --port 8081
