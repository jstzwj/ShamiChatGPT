
import json
import json
import string
import asyncio
from playwright._impl._api_types import TimeoutError
from playwright.async_api import async_playwright
from playwright.async_api import Playwright

from chatgpt.exceptions import ServerOverloadError


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
    
    async def start_session(self):
        self.pw_manager = async_playwright()
        self.pw = await self.pw_manager.__aenter__()

        self.browser = await self.pw.chromium.launch(headless=self.headless, devtools=False)
        self.context = await self.browser.new_context()
        await self.context.add_init_script("Object.defineProperties(navigator, {webdriver:{get:()=>false}});")
        
        try:
            await self.login()
        except ServerOverloadError as e:
            await self.end_session()

    async def end_session(self):
        await self.context.close()
        await self.browser.close()
        await self.pw_manager.__aexit__()
        self.context = None
        self.browser = None
        self.pw = None
        self.pw_manager = None

    async def login(self):
        self.page = await self.context.new_page()
        await self.page.goto("https://chat.openai.com/auth/login")
        try:
            await self.page.wait_for_selector(selector="xpath=//button[text()='Log in']")
        except TimeoutError as e:
            await self.page.wait_for_selector(selector="xpath=//div[text()='ChatGPT is at capacity right now']")
            raise ServerOverloadError("ChatGPT is at capacity right now")
        
        await asyncio.sleep(3)
        await self.page.locator("xpath=//button[text()='Log in']").click()
        await self.page.wait_for_url("https://auth0.openai.com/u/login/identifier?state=*")
        await asyncio.sleep(0.5)
        await self.page.locator("xpath=//input[@name='username']").fill(self.account)
        await self.page.locator("xpath=//button[text()='Continue']").click()
        await self.page.wait_for_selector(selector="xpath=//input[@name='password']")
        await self.page.locator("xpath=//input[@name='password']").fill(self.password)
        await self.page.locator("xpath=//button[text()='Continue']").click()
        await self.page.wait_for_url("https://chat.openai.com/chat")
        await self.skip_button("Next")
        await self.skip_button("Next")
        await self.skip_button("Done")
    
    async def skip_button(self, name):
        if await self.page.locator(f"xpath=//button[text()='{name}']").count() > 0:
            await self.page.locator(f"xpath=//button[text()='{name}']").click()

    async def click_ui(self, xpath: str):
        await self.page.wait_for_selector(selector=f"xpath={xpath}")
        await self.page.locator(selector=f"xpath={xpath}").click()

    async def new_chat(self):
        await self.click_ui("xpath=//a[text()='New chat']")
    
    async def conversation_select(self, index: int):
        await self.click_ui(f'xpath=//nav/div[1]/div/a[{index}]')
    
    async def conversation_info(self):
        conversation_info = []
        all_conversation = await self.page.locator(f'xpath=//nav/div[1]/div/a').all()
        for chat_conversation in all_conversation:
            text = chat_conversation.locator("xpath=div[1]").text_content()
            conversation_info.append(text)
        
        return conversation_info