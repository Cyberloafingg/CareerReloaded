from fastapi import FastAPI
import uvicorn
from apps.app01 import app01
from apps.app02 import app02
from apps.app03 import app03
from apps.app04 import app04

app = FastAPI()

app.include_router(app01, prefix='/app01', tags=['01 Path args and query args'])
app.include_router(app02, prefix='/app02', tags=['02 Pydantic model'])
app.include_router(app03, prefix='/app03', tags=['03 Form data'])
app.include_router(app04, prefix='/app04', tags=['04 File upload'])

if __name__ == '__main__':
    uvicorn.run('main:app',
                port=8000,
                reload=True,
                reload_delay=0.1)

