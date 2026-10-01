
from app import create_app
from worker.updater import run_update
app=create_app()
with app.app_context():
    print(run_update())
