from pydantic import BaseModel
from typing import Optional, Text, List
from uuid import UUID, uuid4

class Article(BaseModel):
    title: str
    content: str
    content_html: str
    creator: str
    source: str
    topic: str
    category: str
    tag: str
    classification: str

class Check(BaseModel):
    text: str

class Topic(BaseModel):
    name: str

class Keyword(BaseModel):
    name: str

class Complaint(BaseModel):
    title: str
    content: str
    content_html: str
    topic: str
    source: str

class Dashboard(BaseModel):
    keyword: str
    start_date: str
    start_end: str