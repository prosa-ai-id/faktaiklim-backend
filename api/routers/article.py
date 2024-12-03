from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Response, Header, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, select
from api import config, schemas, models
from api.database import get_db
from api.models import Article,Topic
from datetime import datetime
import pandas, shutil, requests, json

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token/")

router = APIRouter(
    prefix="/api/article",
    tags=['Article']
)

@router.get('/', status_code=status.HTTP_200_OK)
def getAll(
        db: Session = Depends(get_db),
        search: Optional[str] = "",
        topic: Optional[str] = "",
        page_size: Optional[int] = 10,
        page_number: Optional[int] = 1,
        order: Optional[str] = "title",
        sort: Optional[str] = "asc"
    ):
    status_code = status.HTTP_200_OK
    try:
        if page_number < 1:
            page_number = 1
        
        data = db.query(Article).filter(
                (Article.title.ilike(f'%{search}%')) | (Article.content.ilike(f'%{search}%'))
            )
        if topic != "":
            data= data.filter(Article.topic.ilike(f'%{topic}%'))
        total = data.count()

        if sort == "asc":
            if order == 'title':
                data = data.order_by(Article.title).limit(page_size).offset((page_number-1)*page_size).all()
            elif order == 'content':
                data = data.order_by(Article.content).limit(page_size).offset((page_number-1)*page_size).all()
            elif order == 'creator':
                data = data.order_by(Article.creator).limit(page_size).offset((page_number-1)*page_size).all()
            elif order == 'source':
                data = data.order_by(Article.source).limit(page_size).offset((page_number-1)*page_size).all()
            elif order == 'topic':
                data = data.order_by(Article.topic).limit(page_size).offset((page_number-1)*page_size).all()
            elif order == 'tag':
                data = data.order_by(Article.tag).limit(page_size).offset((page_number-1)*page_size).all()
            else:
                data = data.order_by(Article.created_at).limit(page_size).offset((page_number-1)*page_size).all()
        else:
            if order == 'title':
                data = data.order_by(desc(Article.title)).limit(page_size).offset((page_number-1)*page_size).all()
            elif order == 'content':
                data = data.order_by(desc(Article.content)).limit(page_size).offset((page_number-1)*page_size).all()
            elif order == 'creator':
                data = data.order_by(desc(Article.creator)).limit(page_size).offset((page_number-1)*page_size).all()
            elif order == 'source':
                data = data.order_by(desc(Article.source)).limit(page_size).offset((page_number-1)*page_size).all()
            elif order == 'topic':
                data = data.order_by(desc(Article.topic)).limit(page_size).offset((page_number-1)*page_size).all()
            elif order == 'tag':
                data = data.order_by(desc(Article.tag)).limit(page_size).offset((page_number-1)*page_size).all()
            else:
                data = data.order_by(desc(Article.created_at)).limit(page_size).offset((page_number-1)*page_size).all()

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST if status_code==status.HTTP_200_OK else status_code,
            content={
                "message":str(e),
            }
        )
    return {
        "data": data,
        "meta":{
            "page":page_number,
            "perPage": page_size,
            "total":total
        }
    }

@router.get('/list/', status_code=status.HTTP_200_OK)
def list(
        db: Session = Depends(get_db),
        search: Optional[str] = "",
        topic: Optional[str] = "",
        order: Optional[str] = "title",
        sort: Optional[str] = "asc"
    ):
    status_code = status.HTTP_200_OK
    try:
        data = db.query(Article).filter(
                (Article.title.ilike(f'%{search}%')) | (Article.content.ilike(f'%{search}%'))
            )
        if topic != "":
            data= data.filter(Article.topic.ilike(f'%{topic}%'))
        if sort == "asc":
            if order == 'title':
                data = data.order_by(Article.title).all()
            elif order == 'content':
                data = data.order_by(Article.content).all()
            elif order == 'creator':
                data = data.order_by(Article.creator).all()
            elif order == 'source':
                data = data.order_by(Article.source).all()
            elif order == 'topic':
                data = data.order_by(Article.topic).all()
            elif order == 'tag':
                data = data.order_by(Article.tag).all()
            else:
                data = data.order_by(Article.created_at).all()
        else:
            if order == 'title':
                data = data.order_by(desc(Article.title)).all()
            elif order == 'content':
                data = data.order_by(desc(Article.content)).all()
            elif order == 'creator':
                data = data.order_by(desc(Article.creator)).all()
            elif order == 'source':
                data = data.order_by(desc(Article.source)).all()
            elif order == 'topic':
                data = data.order_by(desc(Article.topic)).all()
            elif order == 'tag':
                data = data.order_by(desc(Article.tag)).all()
            else:
                data = data.order_by(desc(Article.created_at)).all()

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST if status_code==status.HTTP_200_OK else status_code,
            content={
                "message":str(e),
            }
        )
    return {
        "data": data
    }

@router.post('/create/', status_code=status.HTTP_201_CREATED)
def create(
        request:schemas.Article,
        db: Session = Depends(get_db)
    ):
    status_code = status.HTTP_201_CREATED
    try:        
        is_duplicate = db.query(Article).filter(Article.title==request.title).first()
        if is_duplicate:
            raise Exception('title is duplicate')
        
        data = Article(
            title = request.title,
            content = request.content,
            content_html = request.content_html,
            creator = request.creator,
            source = request.source,
            topic = request.topic,
            category = request.category,
            tag = request.tag,
            classification = request.classification
        )
        db.add(data)
        db.commit()
        db.refresh(data)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if status_code==status.HTTP_201_CREATED else status_code,
            content={
                "message":str(e),
            }
        )
    return {
        "data":data.id
    }

@router.get('/{id}', status_code=status.HTTP_200_OK)
def read(
        id: str,
        db: Session = Depends(get_db)
    ):
    status_code = status.HTTP_200_OK
    try:
        data = db.query(Article).filter(Article.id==id)
        if not data.first():
            status_code=status.HTTP_400_BAD_REQUEST
            raise Exception('data is not exist')
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if status_code==status.HTTP_200_OK else status_code,
            content={
                "message":str(e),
            }
        )
    return {
        "data":data.first()
    }

@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(
        id:str,
        request: schemas.Article,
        db: Session = Depends(get_db)
    ):
    status_code=status.HTTP_202_ACCEPTED
    try:
        data = db.query(Article).filter(Article.id==id)
        if not data.first():
            status_code=status.HTTP_400_BAD_REQUEST
            raise Exception('data is not exist')
        data.update(
            {
                'title':request.title,
                'content':request.content,
                'content_html':request.content_html,
                'creator':request.creator,
                'source':request.source,
                'topic':request.topic,
                'category':request.category,
                'tag':request.tag,
                'classification':request.classification
            }
        )
        db.commit()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if status_code==status.HTTP_202_ACCEPTED else status_code,
            content={
                "message":str(e),
            }
        )
    return {
        "data":data.first()
    }

@router.delete('/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete(
        id: str,
        db: Session = Depends(get_db)
    ):
    status_code=status.HTTP_202_ACCEPTED
    try:
        data = db.query(Article).filter(Article.id==id)
        if not data.first():
            status_code=status.HTTP_400_BAD_REQUEST
            raise Exception('data is not exist')
        data.delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if status_code==status.HTTP_202_ACCEPTED else status_code,
            content={
                "message":str(e),
            }
        )
    return {
        "message": "Data has been deleted"
    }

@router.post("/upload/")
def upload(
        file:UploadFile=File(...),
        db: Session = Depends(get_db)
    ):
    status_code=status.HTTP_201_CREATED
    try:
        save_file = str(int(round(datetime.now().timestamp()))) +"-"+ file.filename
        upload_file = config.PATH_BERKAS + save_file
        with open(upload_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        df = pandas.read_excel(upload_file)
        result_insert_nlp = ""

        for index, row in df.iterrows():
            list_category = ''
            source_category = str(row[4]).split("\n")
            for cat in source_category:
                if cat == '':
                    continue
                list_category = list_category + cat+','
                exist_topic = db.query(Topic).filter(Topic.name==cat)
                if not exist_topic.first():
                    data = Topic(
                        name = cat,
                        is_active = True
                    )
                    db.add(data)
                    db.commit()
            list_category = list_category[:-1]

            # Check duplicate
            is_duplicate = db.query(Article).filter(Article.title==str(row[0]), Article.source==str(row[2]))
            if is_duplicate.first():
                is_duplicate.update({
                    'title': str(row[3]),
                    'content': str(row[0]),
                    'content_html': str(row[0]),
                    'source': str(row[1]),
                    #'category': str(row[4]),
                    'category': list_category,
                    'classification': str(row[5]),
                    'created_at': str(row[2])
                })
                db.commit()
            else:
                insert = Article(
                    title = str(row[3]),
                    content = str(row[0]),
                    content_html = str(row[0]),
                    source = str(row[1]),
                    topic = list_category,
                    category = list_category,
                    classification = str(row[5]),
                    modified_at = datetime.now(),
                    created_by = 'admin',
                    created_at = str(row[2])
                )
                db.add(insert)
                db.commit()
                db.refresh(insert)

                # Insert to API AI-NLP
                article = db.query(Article).filter(Article.id==insert.id).first()
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key":config.X_API_KEY
                }
                url = config.URL_API_NLP_SAVE_ARTICLE + str(id)
                params = {
                    "id": article.id,
                    "title":article.title,
                    "content": article.content,
                    "html_content": article.content_html,
                    "short_content": article.title,
                    "created_by": article.created_by,
                    "localtime": str(article.created_at),
                    "publish_localtime": str(article.created_at),
                    "user_publish_date": str(article.created_at),
                    "stamped_image_url": [],
                    "classification": article.classification,
                    "category": article.category,
                    "status_name": "submitted",
                    "status_reason": "",
                    "status_created_by": article.created_by,
                    "status_localtime": str(article.created_at),
                    "tags": [],
                    "verify_url": [],
                    "distributions": [],
                    "source_description": article.source
                }
                response = requests.put(url, headers=headers, data=json.dumps(params))
                if response.status_code == 200:
                    data = response.json()
                    result_insert_nlp = result_insert_nlp + str(insert.id) + ' berhasil; '
                else:
                    result_insert_nlp = result_insert_nlp + str(insert.id) + ' gagal; '

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST  
                if status_code==status.HTTP_201_CREATED else status_code,
            content={
                "message":str(e)
            }
        )
    return {
        "message":result_insert_nlp
    }

#@router.post('/test/', status_code=status.HTTP_201_CREATED)
def test(
        db: Session = Depends(get_db)
    ):
    status_code = status.HTTP_201_CREATED
    try:
        id = 1
        article = db.query(Article).filter(Article.id==id).first()

        headers = {
            "Content-Type": "application/json",
            "x-api-key":config.X_API_KEY
        }
        url = config.URL_API_NLP_SAVE_ARTICLE + str(id)
        params = {
            "id": article.id,
            "title":article.title,
            "content": article.content,
            "html_content": article.content_html,
            "short_content": article.title,
            "created_by": article.created_by,
            "localtime": str(article.created_at),
            "publish_localtime": str(article.created_at),
            "user_publish_date": str(article.created_at),
            "stamped_image_url": [],
            "classification": article.classification,
            "category": article.topic,
            "status_name": "submitted",
            "status_reason": "empty",
            "status_created_by": article.created_by,
            "status_localtime": str(article.created_at),
            "tags": [],
            "verify_url": [],
            "distributions": [],
            "source_description": article.source
        }
        response = requests.put(url, headers=headers, data=json.dumps(params))
        result = ""
        if response.status_code == 200:
            data = response.json()
            result = data['status']
        else:
            result = response.text
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if status_code==status.HTTP_201_CREATED else status_code,
            content={
                "message":str(e),
            }
        )
    return {
        "data":result
    }

@router.get('/crawl-kominfo/', status_code=status.HTTP_200_OK)
def crawl_kominfo(
        db: Session = Depends(get_db)
    ):
    status_code = status.HTTP_200_OK
    try:
        # Note: Next dibuat menjadi worker sehingga tidak timeout
        result = ''
        headers = {
            "x-api-key":config.X_API_KEY_KOMINFO
        }

        # Get list category/topic
        '''
        jml_update_topic = 0
        url = config.URL_API_CATEGORY_KOMINFO
        response = requests.get(url, headers=headers)
        # Sinkronisasi Topic
        if response.status_code == 200:
            data = response.json()
            for item in data['data']:
                if (item['is_active']):
                    jml_update_topic = jml_update_topic + 1
                    topic = db.query(Topic).filter(Topic.name==item['name'])
                    if not topic.first():
                        data = Topic(
                            name = item['name'],
                            is_active = True
                        )
                        db.add(data)
                        db.commit()
            result = result + 'update topics: ' + str(jml_update_topic) + '; '
        else:
            result = result + 'get-list-category-kominfo failed; '
            print('get-list-category-kominfo failed')

        # Crawl New Article
        url = config.URL_API_ARTICLE_KOMINFO
        jml_new_article = 0
        jml_new_article_nlp = 0
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for item in data['data']['references']:
                tag_str = ''
                for tag in item['issue_tags']:
                    tag_str = tag_str + ',' + tag

                is_duplicate = db.query(Article).filter(Article.title==item['title']).first()
                if not is_duplicate:
                    jml_new_article = jml_new_article + 1
                    # Insert New Article
                    data = Article(
                        title = item['title'],
                        content = item['content'],
                        content_html = item['content'],
                        creator = item['created_by'],
                        source = item['source_description'],
                        topic = item['category'],
                        category = item['category'],
                        tag = tag_str,
                        classification = item['classification'].upper(),
                        created_at = item['publish_localtime'],
                        created_by = item['created_by'],
                    )
                    db.add(data)
                    db.commit()
                    db.refresh(data)

                    # Insert Article to NLP DB
                    article = db.query(Article).filter(Article.id==data.id).first()
                    headers = {
                        "Content-Type": "application/json",
                        "x-api-key":config.X_API_KEY
                    }
                    url = config.URL_API_NLP_SAVE_ARTICLE + str(data.id)
                    params = {
                        "id": article.id,
                        "title":article.title,
                        "content": article.content,
                        "html_content": article.content_html,
                        "short_content": article.title,
                        "created_by": article.created_by,
                        "localtime": str(article.created_at),
                        "publish_localtime": str(article.created_at),
                        "user_publish_date": str(article.created_at),
                        "stamped_image_url": [],
                        "classification": article.classification,
                        "category": article.topic,
                        "status_name": "submitted",
                        "status_reason": "empty",
                        "status_created_by": article.created_by,
                        "status_localtime": str(article.created_at),
                        "tags": [],
                        "verify_url": [],
                        "distributions": [],
                        "source_description": article.source
                    }
                    response = requests.put(url, headers=headers, data=json.dumps(params))
                    if response.status_code == 200:
                        data = response.json()
                        jml_new_article_nlp = jml_new_article_nlp + 1
                        print('Insert Article #' + str(article.id) + ' berhasil; ')
                    else:
                        result = result + "Insert Article #" + str(article.id) + " gagal; "
                        print('Insert Article #' + str(article.id) + ' gagal; ')
            result = result + 'add new articles: ' + str(jml_new_article) + '/' + str(jml_new_article_nlp) + '; '
        else:
            result = result + 'get-list-new-article-kominfo failed;'
            print('get-list-new-article-kominfo failed')
        '''

        # Looping by Category:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": config.X_API_KEY_KOMINFO
        }
        url = config.URL_API_ARTICLE_HOAX_CATEGORY_KOMINFO
        list_topic = db.query(Topic).filter(Topic.is_active==True).all()
        for topic in list_topic:
            params = {
                "category":topic.name,
                "size":30,
                "page":1
            }
            jml_article_topic = 0
            jml_article_topic_nlp = 0
            response = requests.post(url, headers=headers, data=json.dumps(params))
            if response.status_code == 200:
                data = response.json()
                for item in data['data']['references']:
                    tag_str = ''
                    for tag in item['issue_tags']:
                        tag_str = tag_str + ',' + tag

                    is_duplicate = db.query(Article).filter(Article.title==item['title']).first()
                    if not is_duplicate:
                        jml_article_topic = jml_article_topic + 1
                        # Insert New Article
                        data = Article(
                            title = item['title'],
                            content = item['html_content'],
                            content_html = item['html_content'],
                            creator = item['status_created_by'],
                            source = item['source_description'],
                            topic = item['category'],
                            category = item['category'],
                            tag = tag_str,
                            classification = item['classification'].upper(),
                            created_at = item['publish_localtime'],
                            created_by = 'system',
                        )
                        db.add(data)
                        db.commit()
                        db.refresh(data)

                        # Insert Article to NLP DB
                        article = db.query(Article).filter(Article.id==data.id).first()
                        headers = {
                            "Content-Type": "application/json",
                            "x-api-key":config.X_API_KEY
                        }
                        url = config.URL_API_NLP_SAVE_ARTICLE + str(id)
                        params = {
                            "id": article.id,
                            "title":article.title,
                            "content": article.content,
                            "html_content": article.content_html,
                            "short_content": article.title,
                            "created_by": article.created_by,
                            "localtime": str(article.created_at),
                            "publish_localtime": str(article.created_at),
                            "user_publish_date": str(article.created_at),
                            "stamped_image_url": [],
                            "classification": article.classification,
                            "category": article.topic,
                            "status_name": "submitted",
                            "status_reason": "empty",
                            "status_created_by": article.created_by,
                            "status_localtime": str(article.created_at),
                            "tags": [],
                            "verify_url": [],
                            "distributions": [],
                            "source_description": article.source
                        }
                        response = requests.put(url, headers=headers, data=json.dumps(params))
                        if response.status_code == 200:
                            data = response.json()
                            jml_article_topic_nlp = jml_article_topic_nlp + 1
                            print('Insert Article #' + str(article.id) + ' berhasil; ')
                        else:
                            print('Insert Article #' + str(article.id) + ' gagal; ')
            else:
                print(response.status_code)
                print(response.text)
                print('get-hoax-article-kominfo dengan topic/category '+topic.name+' failed')
            result = result + 'add articles category: '+topic.name+': ' + str(jml_article_topic) + '/' + str(jml_article_topic_nlp) + '; '

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST if status_code==status.HTTP_200_OK else status_code,
            content={
                "message":str(e),
            }
        )
    return {
        "data": result
    }

@router.post('/check/', status_code=status.HTTP_201_CREATED)
def check(
        text: str = "Penyelidikan oleh jaksa penuntut di New York, Maryland, California, dan Kepulauan Virgin yang memeriksa apakah tindakan ExxonMobil melanggar undang-undang perlindungan konsumen atau investor menunjukkan pentingnya memastikan bahwa perusahaan bahan bakar fosil mematuhi peraturan terkait perubahan iklim",
        db: Session = Depends(get_db)
    ):
    status_code = status.HTTP_201_CREATED
    try:
        # Call API NLP Check
        headers = {
            "Content-Type": "application/json",
            "x-api-key":config.X_API_KEY
        }
        url = config.URL_API_NLP_CHECK
        params = {
            "text": text
        }
        response = requests.post(url, headers=headers, data=json.dumps(params))
        status_result = "success"
        message = ""
        hoax_probability = -1
        relevant_item = []
        topic = []
        if response.status_code == 200:
            data = response.json()
            relevant_item = data['relevant_items']
            hoax_probability = data['hoax_probability']
        else:
            status_result = "error"
            message = response.text
        
        # Call API NLP 
        url = config.URL_API_NLP_TOPIC
        response = requests.post(url, headers=headers, data=json.dumps(params))
        if response.status_code == 200:
            data = response.json()
            topic = data
        else:
            status_result = "error"
            message = response.text

        result = {
            "status": status_result,
            "hoax_probability": hoax_probability,
            "relevant_item": relevant_item,
            "topic": topic,
            "message": message
        }

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if status_code==status.HTTP_201_CREATED else status_code,
            content={
                "message":str(e),
            }
        )
    return {
        "data":result
    }
