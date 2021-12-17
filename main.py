from fastapi import FastAPI
from routes.user import user
from routes.product import product
import uvicorn

app = FastAPI()
app.include_router(user)
app.include_router(product)


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)