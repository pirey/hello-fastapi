from fastapi.testclient import TestClient

from app import main, database, models

client = TestClient(main.app)

def test_get_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {
        "title": "Hello Fastapi",
        "version": "1.0.0"
    }


# def test_run_db():
#     db = database.SessionLocal()
#     first_user = db.query(models.User).filter(models.User.username == "marco@pfsquad").first()
#     assert first_user is not None
#     assert first_user.username == "marco@pfsquad"
#     db.close()