from fastapi import APIRouter, HTTPException, Depends, status, Response, Header, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, select
from api import config, schemas, models
from api.database import get_db
from api.models import Article, Issue
import random

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token/")

router = APIRouter(
    prefix="/api/dashboard",
    tags=['Dashboard']
)

@router.get('/', status_code=status.HTTP_200_OK)
def dashboard(
        db: Session = Depends(get_db),
        keyword: str = "",
        start_date: str = "2024-03-01",
        end_date: str = "2024-03-23"
    ):
    status_code = status.HTTP_200_OK
    try:
        # check valid date

        # get day start and day end
        start_day = start_date.split("-")
        end_day = end_date.split("-")
        list_tanggal = []
        list_instagram = []
        list_twitter = []
        for x in range ( int(start_day[2]), int(end_day[2])+1):
            if len(str(x)) == 1: 
                tanggal = start_day[0] + '-' + start_day[1] + '-0' + str(x)
                tanggal_awal = start_day[0] + '-' + start_day[1] + '-0' + str(x) + ' 00:00:00'
                tanggal_akhir = start_day[0] + '-' + start_day[1] + '-0' + str(x) + ' 23:59:59'
            else:
                tanggal = start_day[0] + '-' + start_day[1] + '-' + str(x)
                tanggal_awal = start_day[0] + '-' + start_day[1] + '-' + str(x) + ' 00:00:00'
                tanggal_akhir = start_day[0] + '-' + start_day[1] + '-' + str(x) + ' 23:59:59'
            list_tanggal.append(tanggal)

            #issue_instagram = db.query(Issue).filter(Issue.social_media=='instagram', Issue.type=='HOAX', Issue.created_at>=tanggal, Issue.created_at<=tanggal).count()
            issue_instagram = db.query(Issue).filter(Issue.social_media=='instagram', Issue.type=='HOAX', Issue.created_at>=tanggal_awal, Issue.created_at<=tanggal_akhir).count()
            #list_instagram.append(random.randint(1, 100))
            list_instagram.append(issue_instagram)
            #issue_twitter = db.query(Issue).filter(Issue.social_media=='twitter', Issue.type=='HOAX', Issue.created_at>=tanggal, Issue.created_at<=tanggal).count()
            issue_twitter = db.query(Issue).filter(Issue.social_media=='twitter', Issue.type=='HOAX', Issue.created_at>=tanggal_awal, Issue.created_at<=tanggal_akhir).count()
            list_twitter.append(issue_twitter)
        result = {
            'date' : list_tanggal,
            'instagram' : list_instagram,
            'twitter' : list_twitter,
            'akurasi' : 96
        }
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
