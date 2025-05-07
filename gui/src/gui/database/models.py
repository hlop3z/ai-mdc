import json

from sqlalchemy import Column, Enum, Integer, String, Text, create_engine

from .base import BaseModel


class SystemPrompt(BaseModel):
    """Model for storing system prompts."""

    __tablename__ = "system_prompts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, primary_key=True)
    text = Column(Text, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "text": self.text}


class Rule(BaseModel):
    """Model for storing business rules."""

    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum("always", "manual", name="rule_types"), nullable=False)
    content = Column(Text, nullable=False)


class Template(BaseModel):
    """Model for storing prompt templates."""

    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    body = Column(Text, nullable=False)
    args = Column(Text, nullable=False, default="{}")
    meta = Column(Text, nullable=False, default="{}")
