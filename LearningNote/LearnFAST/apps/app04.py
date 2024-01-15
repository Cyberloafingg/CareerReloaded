from fastapi import APIRouter, File, UploadFile
from typing import List



app04 = APIRouter()

# 适合小文件
@app04.post('/file')
async def get_file(file: bytes = File(...)):
    print(file)
    return {"file_size": len(file)}

@app04.post('/file_list')
async def get_list_file(file: List[bytes] = File(...)):
    for i in file:
        print(len(i))
    return {"file_size": len(file)}

# 更为通用的方法，uploadfile是一个类，可以通过file.filename获取文件名
# 这里也可以用List[UploadFile]
@app04.post('/uploadfile')
async def get_upload_file(file: UploadFile = File(...)):
    print(file.filename)
    return {"filename": file.filename}

