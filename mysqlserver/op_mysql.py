# coding=utf-8
from __future__ import unicode_literals, absolute_import
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime,select
#fastapi
from typing import Optional
from fastapi import FastAPI,Depends
from pydantic import BaseModel
import datetime
import uuid
ModelBase = declarative_base() #<-元类

class User(ModelBase):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True)
    dateJoined = Column(DateTime)
    username = Column(String(length=30))
    password = Column(String(length=128))

class ImportRecord(ModelBase):
    __tablename__ = "import_record"

    def __init__(self, id, importFileName, importTime, username,dataAmount=0, questionDataDict=0):
        
        self.id = id
        self.importFileName = importFileName
        self.importTime = importTime
        self.dataAmount = dataAmount
        self.questionDataDict = questionDataDict
        self.username = username

    id = Column(Integer, primary_key=True)
    importFileName = Column(String(length=30))
    importTime = Column(DateTime)
    dataAmount = Column(Integer)
    questionDataDict = Column(String(length=200))
    username = Column(String(length=30))

    def to_dict(self):
        return dict(id=self.id,importFileName=self.importFileName,importTime=self.importTime,dataAmount=self.dataAmount,questionDataDict=self.questionDataDict,username=self.username)

# 初始化数据库连接:
engine = create_async_engine('mysql+aiomysql://root:admin@10.48.60.72:3306/business')


# 创建DBSession类型:
SessionLocal = sessionmaker(class_=AsyncSession,autocommit=False,autoflush=False,bind=engine)

async def get_db_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

app = FastAPI()

@app.get('/all_import_record')
async def read_all_record(*, db_session: AsyncSession = Depends(get_db_session)):
    async with db_session.begin():
        results = await db_session.execute(select(ImportRecord))
        data = results.scalars().all()
        data = [item.to_dict() for item in data]
    return data

@app.post('/add_data')
async def add_record(*, db_session: AsyncSession = Depends(get_db_session), importFileName:str,username:str,dataAmount:int,importTime:str):
    snowId = int(str(int(uuid.uuid1()))[0:18])
    async with db_session.begin():
    	lab = ImportRecord(id=snowId,importFileName=importFileName, username=username, dataAmount=dataAmount,importTime=importTime)
    	db_session.add(lab)
    	await db_session.flush()
    return snowId
