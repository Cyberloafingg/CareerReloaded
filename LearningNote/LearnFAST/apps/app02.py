from datetime import date
from typing import Optional, List

from fastapi import APIRouter
from pydantic import BaseModel, Field, validator


class Addr(BaseModel):
    city: str
    street: str


class User(BaseModel):
    name: str = 'root'
    age: int = Field(default=10, gt=1, le=100)  # 使用Field可以设置默认值和验证规则
    birth: date
    friends: Optional[List[str]] = None
    addr: Optional[Addr] = None  # 嵌套模型

    # 或使用规则函数，
    @validator('name')
    def check_name(cls, v):
        assert v.isalpha(), 'name must be alpha'
        return v


app02 = APIRouter()


@app02.post('/data')
async def data(user: User):
    print(user, type(user))
    return user  # 这里的返回值会被自动转换为json格式

# curl -X 'GET' \
#   'http://127.0.0.1:8000/app02/user/?item_id=123' \
#   -H 'accept: application/json'
