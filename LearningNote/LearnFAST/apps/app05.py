from fastapi import APIRouter, Request
from typing import List

app05 = APIRouter()

@app05.post('/')
async def request(req: Request):
    print(f"url: {req.url}")
    print(f"client客户端: {req.client.host}")
    print(f"headers请求头: {req.headers.get('user-agent')}") # 有些请求头是不能直接获取的，比如cookie
    print(f"method: {req.method}")
    # cookie
    print(f"cookie: {req.cookies}")
    return {
        'url': req.url,
        'client': req.client.host,
        'headers': req.headers.get('user-agent'),
        'method': req.method,
        'cookie': req.cookies
    }

