import uvicorn
from fastapi import FastAPI


def get_app():
    app = FastAPI()
    return app


app = get_app()

if __name__ == "__main__":
    uvicorn.run(app)
