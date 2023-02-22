#!/usr/bin/env python
#coding:utf-8

class ChatGPTServiceError(Exception):
    pass


class InternalError(Exception):
    pass


class ParamsError(ChatGPTServiceError):
    pass


class ServerOverloadError(ChatGPTServiceError):
    pass

class UnsupportedCountryError(ChatGPTServiceError):
    pass

class AccessDeniedError(ChatGPTServiceError):
    pass


class MissDataError(InternalError):
    pass


class InitObjError(InternalError):
    pass


class InvalidDataError(InternalError):
    pass


class TimeoutError(InternalError):
    pass

