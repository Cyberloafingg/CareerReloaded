from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"Hello": "World"}

if __name__ == '__main__':
    uvicorn.run('FastAPI_QuickStart:app',
                host='127.0.0.1',
                reload=True,
                port=8080)