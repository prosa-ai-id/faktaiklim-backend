from fastapi import APIRouter, HTTPException, Depends, status, Response, Header, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, select
from api import config, schemas, models
from api.database import get_db
from api.models import Keyword, Issue

import requests, json
from api import config
from apify_client import ApifyClient
from datetime import datetime

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token/")

router = APIRouter(
    prefix="/api/keyword",
    tags=['Keyword']
)


@router.get('/list/', status_code=status.HTTP_200_OK)
def list(
        db: Session = Depends(get_db),
        search: Optional[str] = "",
        order: Optional[str] = "name",
        sort: Optional[str] = "asc"
    ):
    status_code = status.HTTP_200_OK
    try:
        data = db.query(Keyword).filter(Keyword.name.ilike(f'%{search}%'))
        if sort == "asc":
            if order == 'name':
                data = data.order_by(Keyword.name).all()
            else:
                data = data.order_by(Keyword.created_at).all()
        else:
            if order == 'name':
                data = data.order_by(desc(Keyword.name)).all()
            else:
                data = data.order_by(desc(Keyword.created_at)).all()

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
        request:schemas.Keyword,
        db: Session = Depends(get_db)
    ):
    status_code = status.HTTP_201_CREATED
    try:        
        is_duplicate = db.query(Keyword).filter(Keyword.name==request.name).first()
        if is_duplicate:
            raise Exception('name is duplicate')
        
        data = Keyword(
            name = request.name
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
        data = db.query(Keyword).filter(Keyword.id==id)
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
        request: schemas.Keyword,
        db: Session = Depends(get_db)
    ):
    status_code=status.HTTP_202_ACCEPTED
    try:
        data = db.query(Keyword).filter(Keyword.id==id)
        if not data.first():
            status_code=status.HTTP_400_BAD_REQUEST
            raise Exception('data is not exist')
        data.update(
            {
                'name':request.name
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
        data = db.query(Keyword).filter(Keyword.id==id)
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

@router.get('/medsos/', status_code=status.HTTP_200_OK)
def medsos(db: Session = Depends(get_db)):
    status_code = status.HTTP_200_OK
    try:
        data = db.query(Keyword).all()
        for item in data:
          query = item.name

          # APIFY/INSTAGRAM
          client = ApifyClient(config.APIFY_TOKEN)
          run_input = {
              "addParentData": False,
              "enhanceUserSearchWithFacebookPage": False,
              "isUserReelFeedURL": False,
              "isUserTaggedFeedURL": False,
              "onlyPostsNewerThan": datetime.today().strftime('%Y-%m-%d'),
              "resultsLimit": 1,
              "resultsType": "posts",
              "search": query,
              "searchLimit": 1,
              "searchType": "hashtag"
          }
          run = client.actor("apify/instagram-scraper").call(run_input=run_input)
          for item in client.dataset(run["defaultDatasetId"]).iterate_items():
              for post in item['topPosts']:
                if post['timestamp'].split('T')[0] == datetime.today().strftime('%Y-%m-%d'):
                  data = Issue(
                      social_media = 'instagram',
                      content = post['caption'],
                      taken_at = post['timestamp'],
                      type = '',
                      keyword = query, 
                      topic = ''
                  )
                  db.add(data)
                  db.commit()
                  db.refresh(data)
              
          #TWITTER
          bearer_token = config.X_BEARER_TOKEN
          url = "https://api.twitter.com/2/tweets/search/recent"
          params = {
              'query': query,
              # 'start_date': 'YYYY-MM-DDTHH:mm:ssZ',
              # 'end_date': 'YYYY-MM-DDTHH:mm:ssZ',
              'max_results': config.MAX_RESULTS
          }
          headers = {
              'Authorization': f'Bearer {bearer_token}'
          }
          response = requests.get(url, headers=headers, params=params)
          if response.status_code == 200:
              result = response.json()
              for i in result['data']:
                data = Issue(
                    social_media = 'twitter',
                    content = i['text'],
                    # taken_at = ''
                    type = '',
                    keyword = query, 
                    topic = ''
                )
                db.add(data)
                db.commit()
                db.refresh(data)
          else:
              print(f"Error: {response.status_code}: {response.text}")
        
        # CHECK HOAX
        list_issues = db.query(Issue).filter(Issue.type=='').all()
        for issue in list_issues:
            # check hoax
            headers = {
                "Content-Type": "application/json",
                "x-api-key":config.X_API_KEY
            }
            url = config.URL_API_NLP_CHECK
            params = {
                "text": issue.content
            }
            response = requests.post(url, headers=headers, data=json.dumps(params))
            if response.status_code == 200:
                data = response.json()
                hoax_probability = data['hoax_probability']
                tipe = 'HOAX'
                if int(hoax_probability) < 50:
                    tipe = 'NOT HOAX'

                update = db.query(Issue).filter(Issue.id==issue.id)
                update.update(
                    {
                        'type':tipe
                    }
                )
                db.commit()

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message":str(e),
            }
        )
    return {
        "data": "success"
    }
