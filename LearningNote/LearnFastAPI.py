from typing import Union,List,Optional
from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


app = FastAPI()


class Item(BaseModel):
    name: str # 必须
    description: str | None = None # 可选
    price: float
    tax: float | None = None



# 定义一个枚举类，继承 str 类型和 Enum 类型
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# 通过 路径 / 和 /items/{item_id} 接受 HTTP 请求。
# 路径为 / ，操作为 GET，函数为 read_root。
@app.get("/")
async def read_root():
    return {"Hello": "World"}


# 声明不属于路径参数的参数，即查询参数
# 这里给定了默认值，即 skip=0, limit=10
# @app.get("/items/")
# async def read_item(skip: int = 0, limit: int =1):
#     return fake_items_db[skip : skip + limit]

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    # print(model_name)
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


# 当你需要将数据从客户端（例如浏览器）发送给 API 时，你将其作为「请求体」发送。
# 请求体是客户端发送给 API 的数据。响应体是 API 发送给客户端的数据。
# 你的 API 几乎总是要发送响应体。但是客户端并不总是需要发送请求体。
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


if __name__ == '__main__':
    uvicorn.run('LearnFastAPI:app', host="127.0.0.1", port=8000,reload=True,reload_delay=0.1)
