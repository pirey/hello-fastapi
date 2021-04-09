from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return {"message": "Hello fastapi"}

@app.get("/users/me")
def get_me():
    return {"user": "current user"}

@app.get("/users/{user_id}")
def get_users(user_id: int):
    return {"user": f"User with the id {user_id}"}