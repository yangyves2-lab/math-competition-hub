
from app import create_app
def test_home():
    app=create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        assert c.get("/").status_code==200
