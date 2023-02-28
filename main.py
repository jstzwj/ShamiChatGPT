import asyncio
import json
from chatgpt.chat import ChatSession

async def main():
    with open("account.json", "r", encoding="utf-8") as f:
        account_info = json.loads(f.read())
    session = ChatSession(account_info["account"], account_info["password"], headless=False)
    await session.start_session()
    info = await session.get_conversations()
    print(info)
    await asyncio.sleep(3)
    history = await session.get_conversation(2)
    print(history)

    await session.submit_question(2, "你好")
    await asyncio.sleep(10)

    await session.end_session()

if __name__ == "__main__":
    asyncio.run(main())