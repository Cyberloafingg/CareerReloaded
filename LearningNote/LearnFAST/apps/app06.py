from typing import Optional, Union, List

from fastapi import APIRouter
from pydantic import BaseModel

app06 = APIRouter()


##################
# response_model #
##################

class UserIn(BaseModel):
    username: str
    password: int
    email: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None


# 需求为 响应的信息中不包含 password 字段
# 使用 response_model 参数
# 在文档中显示一些注释信息
@app06.post('/user', response_model=UserOut,
            description='创建用户,但是使用 response_model 参数,隐藏响应的信息中不包含 password 字段')
def create_user(user: UserIn):
    # 存到数据库
    return user


################################
# response_model_exclude_unset #
################################
class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: float = 10.5
    tags: List[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app06.get("/items/{item_id}",
           response_model=Item,
           response_model_exclude_unset=True,
           response_model_exclude_defaults=True,
           description='原有的数据模型中的默认值不会被返回比如上面foo的 tax 和 tags 字段,'
                       '我们在返回的时候不想返回这些字段')
async def read_item(item_id: str):
    return items[item_id]
