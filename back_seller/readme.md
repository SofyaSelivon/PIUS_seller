pip install -r requirements.txt

alembic init alembic

alembic revision --autogenerate -m "init"

alembic upgrade head

python seed.py

uvicorn app.main:app --reload

**запуск через python run.py**


yarn install

yarn dev
