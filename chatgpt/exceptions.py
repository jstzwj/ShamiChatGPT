#!/usr/bin/env python
#coding:utf-8

class ChatGPTError(Exception):
    pass


class InternalError(Exception):
    pass


class ParamsError(ChatGPTError):
    pass


class ServerOverloadError(ChatGPTError):
    pass


class MissDataError(InternalError):
    pass


class InitObjError(InternalError):
    pass


class InvalidDataError(InternalError):
    pass


class TimeoutError(InternalError):
    pass

