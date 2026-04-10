pip install -r requirements.txt

alembic init alembic

alembic revision --autogenerate -m "init"

alembic upgrade head

python seed.py

uvicorn app.main:app --reload


yarn install

yarn dev

**запуск через python run.py**
