from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class user(Base):
    __tablename__ = "usrModel"

    uID = Column(Integer, nullable=False, primary_key=True, unique=True)
    name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Tokens(Base):
    __tablename__ = "Tokens"

    rustToken = Column(Integer, nullable=False, primary_key=True)
    steamID = Column(Integer, nullable=False)
    IP = Column(String, nullable=False)
    port = Column(String, nullable=False)

class rustInfo(Base):
    __tablename__ = "rustInfo"

    map = Column(String, nullable=False, primary_key=True)
    name = Column(String)
    players = Column(Integer)
    maxPlayers = Column(Integer)
    size = Column(Integer)