from ai_engine_sdk import AiEngine
import os
from os.path import join, dirname
from dotenv import load_dotenv
import asyncio

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

api_key = os.environ.get("FETCH_API_KEY")


async def get_function_groups():
    # ... some asynchronous operations ...
    ai_engine = AiEngine(api_key)
    function_groups = await ai_engine.get_function_groups()
    return function_groups


async def main():
    function_groups = await get_function_groups()
    for group in function_groups:
        print(group)


if __name__ == "__main__":
    asyncio.run(main())
