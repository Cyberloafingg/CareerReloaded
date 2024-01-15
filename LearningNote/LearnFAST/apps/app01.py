from fastapi import APIRouter
from typing import Optional, Union

app01 = APIRouter()


# 声明路径参数，即路径中的参数
# 路径操作
@app01.get('/user/{item_id}')
# 路径函数
def get_user(item_id: int):
    print(item_id)
    return {
        'item_id': item_id
    }


# curl -X 'GET' \
#   'http://127.0.0.1:8000/app01/user/123' \
#   -H 'accept: application/json'

# 声明不属于路径参数的参数，即查询参数
@app01.get('/user/')
def get_user(item_id: int, xl: Union[str, None] = None,
             item_name: Optional[str] = None):  # 有默认值的参数不是必须的,Optional[str]等价于Union[str, None]
    return {
        'item_id': {
            'item_id': item_id,
            'item_name': item_name
        }
    }

# curl -X 'GET' \
#   'http://127.0.0.1:8000/app01/user/?item_id=123&xl=ppp&item_name=ppp' \
#   -H 'accept: application/json'
