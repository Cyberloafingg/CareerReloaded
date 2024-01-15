from datetime import date
from typing import Optional, List
from fastapi import Form
from fastapi import APIRouter
from pydantic import BaseModel, Field, validator

app03 = APIRouter()

# 以Form形式接收数据，x-www-form-urlencoded
@app03.post('/register/')
async def register(username: str = Form(...), password: str = Form(...) ):
    print(f"username: {username}, password: {password}")
    return {
        'username': username,
        'password': password
    }