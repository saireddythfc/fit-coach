from ai_engine_sdk import AiEngine
import os
from os.path import join, dirname
from dotenv import load_dotenv
import asyncio
from fastapi import APIRouter, Depends, HTTPException
import requests

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

api_key = os.environ.get("FETCHAI_API_KEY")


async def get_function_groups():
    # ... some asynchronous operations ...
    ai_engine = AiEngine(api_key)
    function_groups = await ai_engine.get_function_groups()
    return function_groups


async def main():
    function_groups = await get_function_groups()
    for group in function_groups:
        print(group)


async def test_session():
    ai_engine = AiEngine(api_key)
    groups = await ai_engine.get_function_groups()
    public = next(g for g in groups if g.name == "Public")
    session = await ai_engine.create_session(function_group=public.uuid)
    # print("Session created:", session.session_id)

    print(f"Session created: {session.session_id}")  # Add logging
    await session.start(
        objective="Favorite holiday destination?",
        context="where can I go for christmas?",
    )
    print("Session started, waiting for response...")  # Add logging

    # *** ADD A DELAY ***
    await asyncio.sleep(5)  # Wait for 5 seconds (adjust as needed)

    # Retrieve response
    print("Attempting to get messages...")  # Add logging
    messages = await session.get_messages()
    print(f"Messages received: {messages}")  # Add logging

    if messages:
        # It's often the *second* message (index 1) that's the AI response
        # The first might be the user input. Check the structure.
        # Let's assume the last one is correct for now as per your original code.
        print(f"AI Response content: {messages[-1].content}")
        return {"response": messages[-1].content}
    else:
        print("No messages found after delay.")  # Add logging
        raise HTTPException(
            status_code=500, detail="No response from AI Engine after delay"
        )


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(test_session())
