import asyncio
import json
from typing import Dict, List
from chatgpt.chat import ChatSession
import datetime
import shutil

def write_dataset(path: str, dataset: List[Dict]):
    with open(path, "w", encoding="utf-8") as f:
        for data in dataset:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

def read_dataset(path: str):
    dataset = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            dataset.append(json.loads(line))
    return dataset

async def main():
    with open("account.json", "r", encoding="utf-8") as f:
        account_info = json.loads(f.read())
    session = ChatSession(account_info["account"], account_info["password"], headless=False)

    dataset = read_dataset("questions.jsonl")

    await session.start_session()
    info = await session.get_conversations()
    print(info)

    for data in dataset:
        start_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        await asyncio.sleep(3)
        await session.new_chat()

        await session.submit_question(data["question_p"])
        await session.wait_until_response()

        await session.submit_question(data["question_n"])
        await session.wait_until_response()
        history = await session.get_conversation(1)
        print(history)

        end_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        data["conversation"] = history
        data["start_time"] = start_time
        data["end_time"] = end_time

        write_dataset("answers.bak.jsonl", dataset)
        shutil.copy("answers.bak.jsonl", "answers.jsonl")

        await session.delete_conversation(1)

    await session.end_session()

if __name__ == "__main__":
    asyncio.run(main())