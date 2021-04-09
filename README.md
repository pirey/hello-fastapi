## Setup

- install `python` & `pip`
- create virtual env `python -m venv .venv`
- activate virtual env `source .venv/bin/activate`
- install dependencies `pip install -r requirements.txt` and `pip install -r requirements-dev.txt`
- run app `uvicorn app.main:app --reload --port=9000`
- open app `http://localhost:9000`