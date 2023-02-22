import asyncio
import json
from chatgpt.chat import ChatSession

async def main():
    with open("account.json", "r", encoding="utf-8") as f:
        account_info = json.loads(f.read())
    session = ChatSession(account_info["account"], account_info["password"])
    await session.start_session()
    await session.conversation_select(1)
    await asyncio.sleep(5)
    await session.conversation_select(2)
    await asyncio.sleep(5)
    await session.conversation_select(3)
    await asyncio.sleep(5)

    info = await session.conversation_info()
    print(info)

    await session.end_session()

if __name__ == "__main__":
    asyncio.run(main())