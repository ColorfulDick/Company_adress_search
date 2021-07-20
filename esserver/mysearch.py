from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import sys
import hashlib
app = FastAPI()
print('进行注册')
from elasticsearch import Elasticsearch
from elasticsearch import AsyncElasticsearch
import time
# 连接ES
es = Elasticsearch([{'host':'10.48.60.72','port':9200}], timeout=3600)
async_es = AsyncElasticsearch([{'host':'10.48.60.72','port':9200}], timeout=3600)#启用异步连接头
index="ropledata2"

class CompanySearch(BaseModel):
    search_content:Optional[str] = None

class Extract(BaseModel):
    original_text:Optional[str] = None

class SimilarAddressJudge(BaseModel):
    original_text:Optional[str] = None


class User(BaseModel):
    username: str
    cookie: Optional[str] = None

class CompanyName(BaseModel):
    companyname: Optional[str] = None

class Address(BaseModel):
    address: Optional[str] = None


@app.post("/companysearch")#地址搜索
async def company_search(user:User,search_content:CompanySearch):
    params={"user":user,"content":search_content}
    query=  {
        "query": {
        "multi_match":{
        "query":params['content'].search_content,
        "fields":["address","company"]
                        } 
                },
            "from":0,
            "size":20    
            }
    result =await async_es.search(index=index, body=query)
    return result['hits']['hits']

@app.post("/extract")#信息提取
async def company_search(user:User,extract:Extract):
    params={"user":user,"original_text":extract}
    query=  {
        "query": {
        "multi_match":{
        "query":params['original_text'].original_text,
        "fields":["address","company"]
                        } 
                },
            "from":0,
            "size":5
            }
    es_results =await async_es.search(index=index, body=query)
    #print(es_results)
    for j in es_results['hits']['hits']:
        for i in j['_source']['company']:
            if i in params['original_text'].original_text:
                res = {'企业名称：':i,'地址：':j['_source']['address']}
                return res

@app.post("/similaraddressjudge")#相似地址判断
async def company_search(user:User,original_text:SimilarAddressJudge):
    params={"user":user,"content":original_text}
    company_address=params['content'].original_text.split('\r\n')
    print(company_address)
    result_array=[]
    for i in company_address:
        query=  {
        "query": {
        "match_phrase": {
            "company":i
                }
            }
        }
        es_results =await async_es.search(index=index, body=query)
        if len(es_results['hits']['hits'])==0:
            res = {'企业名称：':i,'地址：':'系统中不存在该企业，请检查是否有输错'}
            result_array.append(res)
            continue
        for j in es_results['hits']['hits'][0]['_source']['company']:
            if i in j:
                res = {'企业名称：':j,'地址：':es_results['hits']['hits'][0]['_source']['address']}
                result_array.append(res)
    return result_array

@app.get("/esinfo")#查看es请求头信息
async def es_info():
    #return await es.info()
    return dir(es)

async def es_post(url, data, headers=None):
    async with aiohttp.ClientSession(headers=headers) as session:
        result = await session.post(url, data=data)
        return await result.json()

async def add_company(doc_id,companyname):
    for i in companyname:
        body={
        "script": {
        "source": "int a=0;for (int i=0;i<ctx._source.company.size();i++) {if(ctx._source.company[i]==params.tag){a=1;break;}}if(a==0){ctx._source.company.add(params.tag)}",
        "lang": "painless",
        "params": {
            "tag": i
                }
            }
        }
        print(i)
        result=await async_es.update(index=index,id=doc_id,body=body)
            

@app.post("/addinfo")#添加地址及企业信息
async def add_info(user:User,companyname:CompanyName,address:Address):
    params={"user":user,"companyname":companyname,'address':address}
    actions = []
    doc_id=hashlib.md5(params['address'].address.encode("utf8")).hexdigest()
    companyname=params['companyname'].companyname.split(',')
    query={
    "query": {
        "match_phrase": {
            "_id":doc_id
             }
        }
    }
    search_result=await async_es.search(index=index, body=query)
    print(search_result)
    if len(search_result["hits"]["hits"])==0:
        address_insert_result=await async_es.index(index=index,id=doc_id,body={"address":address.address,"company":[]})
        await add_company(doc_id,companyname)
    else:
        await add_company(doc_id,companyname)
        return {'result':'仅新增企业'}
    return {'result':'新增地址及企业'}

@app.post("/changecompany")#修改公司
async def add_info(user:User,new:str,old:str):
    print(new,old)
    body={
    "query": {
        "match_phrase": {
            "company":old
        }
    },
    "script": {              
    "lang": "painless",             
    "source": "for (int i=0;i<ctx._source.company.size();i++) {if(ctx._source.company[i]== params.old) { ctx._source.company[i] = params.new} }",
    "params": {
    "old": old,
    "new": new
            }
        }
    }
    await async_es.update_by_query(index=index,body=body)
    return {'result':'修改完成'}

@app.post("/changeaddress")#修改地址
async def add_info(user:User,new:str,old:str):
    print(new,old)
    body={
    "query": {
        "match_phrase": {
            "address":old
        }
    },
    "script": {              
    "lang": "painless",             
    "source": "if(ctx._source.address== params.old) { ctx._source.address = params.new}",
    "params": {
    "old": old,
    "new": new
            }
        }
    }
    await async_es.update_by_query(index=index,body=body)
    return {'result':'修改完成'}