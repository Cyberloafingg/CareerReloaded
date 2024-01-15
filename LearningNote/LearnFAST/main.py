import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps import *

app = FastAPI()

app.include_router(app01, prefix='/app01', tags=['01 Path Args and Query Args'])
app.include_router(app02, prefix='/app02', tags=['02 Pydantic Model'])
app.include_router(app03, prefix='/app03', tags=['03 Form Data'])
app.include_router(app04, prefix='/app04', tags=['04 File Upload'])
app.include_router(app05, prefix='/app05', tags=['05 Request Object'])
app.include_router(app06, prefix='/app06', tags=['06 Response Module'])

# 关于静态文件
# 在 Web 开发中，需要请求很多静态资源文件（不是由服务器生成的文件），如 css/js 和图片文件等。
# 在静态文件中，文件是不会被修改的，所以可以直接返回给客户端，直接通过文件路径访问即可。

# 而动态资源文件是由服务器生成的，如 html 文件，是在请求的时候才生成的。
# 开放静态文件夹，这样就可以通过 http://host:port/static/ 访问 static 文件夹下的文件了，也是按照路径访问的
app.mount('/static', StaticFiles(directory='static'), name='static')

if __name__ == '__main__':
    uvicorn.run('main:app',
                port=8000,
                reload=True,
                reload_delay=0.1)
