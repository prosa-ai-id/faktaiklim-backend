from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.sqltypes import Boolean, Date
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
import datetime
import uuid

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    content = Column(Text)
    content_html = Column(Text)
    creator = Column(String)
    source = Column(String)
    topic = Column(String)
    category = Column(String)
    tag = Column(String)
    classification = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
    created_by = Column(String)
    modified_at = Column(DateTime)
    modified_by = Column(String)

class Keyword(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
    created_by = Column(String)

class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    is_active = Column(Boolean)
    created_at = Column(DateTime, default=datetime.datetime.now)
    created_by = Column(String)

class Complaint(Base):
    __tablename__ = 'complaints'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    content = Column(Text)
    content_html = Column(Text)
    topic = Column(String)
    source = Column(String)
    tag = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
    created_by = Column(String)

class Issue(Base):
    __tablename__ = 'issues'

    id = Column(Integer, primary_key=True, autoincrement=True)
    social_media = Column(String)
    content = Column(Text)
    taken_at = Column(DateTime)
    type = Column(String)
    keyword = Column(String)
    topic = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
    created_by = Column(String)
