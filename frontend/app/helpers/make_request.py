from shared_libraries.utils import _fetch_secret_key
from fastapi import HTTPException
import os
import aiohttp


async def parse_multipart(response):
    reader = aiohttp.MultipartReader.from_response(response)
    data = {}
    async for part in reader:
        print(part.headers)
        if part.headers.get(aiohttp.hdrs.CONTENT_DISPOSITION):

            name = part.headers[aiohttp.hdrs.CONTENT_DISPOSITION].split('name=')[-1].strip('"')
            if name == "agent_response":
                data["agent_response"] = await part.json()
            else:
                filename = part.filename
                file_data = await part.read(decode=True)
                data["file"] = (filename, file_data)
    return data


async def make_request(session, method, url, **kwargs):

    async with session.request(method, url, **kwargs) as resp:
        if resp.status != 200:
            raise HTTPException(status_code=resp.status, detail=resp.content)
        content_type = resp.headers.get('Content-Type', '')
        if 'multipart/form-data' in content_type:
            return await parse_multipart(resp)
        else:
            return await resp.json()