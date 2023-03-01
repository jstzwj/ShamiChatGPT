
import json
import re
import string
import asyncio
from typing import Optional, Union
from playwright._impl._api_types import TimeoutError
from playwright.async_api import async_playwright
from playwright.async_api import Playwright

from chatgpt.conversation import Conversation, History
from chatgpt.exceptions import AccessDeniedError, ServerOverloadError, UndefinedError, UnsupportedCountryError
from chatgpt.consts import *

UUID_REGEX = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
CONVERSATION_REGEX = re.compile(r'https://chat\.openai\.com/backend-api/conversation/' + UUID_REGEX)
CONVERSATIONS_REGEX = re.compile(r'https://chat\.openai\.com/backend-api/conversations\?offset=[0-9]+&limit=[0-9]+')
class ChatRecorder(object):
    def __init__(self) -> None:
        pass

    async def response_recorder(self, response):
        pass

class ChatSession(object):
    def __init__(self, account: str, password: str, headless: bool=False) -> None:
        self.account = account
        self.password = password
        self.headless = headless

        self.pw_manager = None
        self.pw = None
        self.browser = None
        self.context = None
        self.page = None
        self.recorder = ChatRecorder()
    
    async def start_session(self):
        self.pw_manager = async_playwright()
        self.pw = await self.pw_manager.__aenter__()

        self.browser = await self.pw.chromium.launch(headless=self.headless, devtools=False)
        self.context = await self.browser.new_context()
        await self.context.add_init_script("Object.defineProperties(navigator, {webdriver:{get:()=>false}});")

        self.page = await self.context.new_page()
        self.page.on("response", self.recorder.response_recorder)
        
        try:
            await self.login()
        except (TimeoutError, AccessDeniedError, UnsupportedCountryError, ServerOverloadError) as e:
            await self.end_session()
            raise e

    async def end_session(self):
        await self.context.close()
        await self.browser.close()
        await self.pw_manager.__aexit__()
        self.context = None
        self.browser = None
        self.pw = None
        self.pw_manager = None

    async def login(self):
        await self.page.goto("https://chat.openai.com/auth/login")
        await self.page.wait_for_load_state("domcontentloaded")

        try:
            await self.page.wait_for_selector(selector="xpath=//button[text()='Log in']")
        except TimeoutError as e:
            if self.check_ui("xpath=//div[text()='ChatGPT is at capacity right now']"):
                raise ServerOverloadError("ChatGPT is at capacity right now")
            elif self.check_ui("xpath=//h1[text()='Access denied']"):
                raise AccessDeniedError("Access denied")
            elif self.check_ui("xpath=//h1[text()='undefined']"):
                raise UndefinedError("Undefined")
            else:
                raise e
        
        await asyncio.sleep(3)
        await self.page.locator("xpath=//button[text()='Log in']").click()
        await self.page.wait_for_url("https://auth0.openai.com/u/login/identifier?state=*")
        await asyncio.sleep(0.5)
        await self.page.locator("xpath=//input[@name='username']").fill(self.account)
        await self.page.locator("xpath=//button[text()='Continue']").click()
        await self.page.wait_for_selector(selector="xpath=//input[@name='password']")
        await self.page.locator("xpath=//input[@name='password']").fill(self.password)
        await self.page.locator("xpath=//button[text()='Continue']").click()

        try:
            await self.page.wait_for_url("https://chat.openai.com/chat")
        except TimeoutError as e:
            await self.page.wait_for_selector(selector="xpath=//div[contains(text(), 'unsupported_country')]")
            raise UnsupportedCountryError("ChatGPT is not available in your country")

        await self.skip_button("Next")
        await self.skip_button("Next")
        await self.skip_button("Done")
    
    async def skip_button(self, name):
        if await self.page.locator(f"xpath=//button[text()='{name}']").count() > 0:
            await self.page.locator(f"xpath=//button[text()='{name}']").click()

    async def click_ui(self, xpath: str):
        await self.page.wait_for_selector(selector=xpath)
        await self.page.locator(selector=xpath).click()
    
    async def check_ui(self, xpath: str):
        return await self.page.locator(selector=xpath).count() > 0

    async def new_chat(self):
        await self.click_ui("xpath=//a[text()='New chat']")
    
    async def select_conversation(self, index: Union[str, int]):
        if isinstance(index, str):
            await self.page.goto(f"https://chat.openai.com/chat/{index}")
        else:
            await self.click_ui(f'xpath=//nav/div[1]/div/a[{index}]')
    
    async def get_conversations(self):
        async with self.page.expect_response(lambda response: re.fullmatch(CONVERSATIONS_REGEX, response.url) and response.status == 200) as response_info:
            await self.new_chat()
        response = await response_info.value
        conversations = json.loads(await response.text())
        ret = []
        for item in conversations["items"]:
            ret.append(Conversation(self, item["id"], item["title"], item["create_time"]))
        return ret
    
    async def get_conversation(self, conversation_index: Optional[Union[str, int]]=None):
        async with self.page.expect_response(lambda response: re.fullmatch(CONVERSATION_REGEX, response.url) and response.status == 200) as response_info:
            await self.new_chat()
            await self.select_conversation(conversation_index)
        response = await response_info.value
        history = json.loads(await response.text())
        return History.from_dict(history)
    
    async def delete_conversation(self, conversation_index: Optional[Union[str, int]]=None):
        if conversation_index is not None:
            await self.select_conversation(conversation_index)
        await self.click_ui("xpath=//nav/div[1]/div/a/div[2]/button[2]")
        await asyncio.sleep(1)
        await self.click_ui("xpath=//nav/div[1]/div/a/div[2]/button[1]")
        await asyncio.sleep(1)
    
    async def wait_until_response(self):
        while True:
            if not await self.check_ui("xpath=//div[@class='text-2xl']"):
                break
            await asyncio.sleep(1)
        
    async def submit_question(self, text: str, conversation_index: Optional[str]=None, delay:int=50):
        if conversation_index is not None:
            await self.select_conversation(conversation_index)
        await self.page.wait_for_selector(selector="xpath=//textarea")
        await self.page.locator(selector="xpath=//textarea").type(text, delay=delay)
        await self.page.locator(selector="xpath=//textarea").press("Enter")