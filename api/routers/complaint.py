from fastapi import APIRouter, HTTPException, Depends, status, Response, Header, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, select
from api import config, schemas, models
from api.database import get_db
from api.models import Complaint
import pandas

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token/")

router = APIRouter(
    prefix="/api/aduan",
    tags=['Aduan']
)


@router.get('/list/', status_code=status.HTTP_200_OK)
def list(
        db: Session = Depends(get_db),
        search: Optional[str] = "",
        order: Optional[str] = "title",
        sort: Optional[str] = "asc"
    ):
    status_code = status.HTTP_200_OK
    try:
        data = db.query(Complaint).filter(Complaint.title.ilike(f'%{search}%'))
        if sort == "asc":
            if order == 'title':
                data = data.order_by(Complaint.title).all()
            elif order == 'content':
                data = data.order_by(Complaint.content).all()
            elif order == 'topic':
                data = data.order_by(Complaint.topic).all()
            elif order == 'source':
                data = data.order_by(Complaint.source).all()
            else:
                data = data.order_by(Complaint.created_at).all()
        else:
            if order == 'title':
                data = data.order_by(desc(Complaint.title)).all()
            elif order == 'content':
                data = data.order_by(desc(Complaint.content)).all()
            elif order == 'topic':
                data = data.order_by(desc(Complaint.topic)).all()
            elif order == 'source':
                data = data.order_by(desc(Complaint.source)).all()
            else:
                data = data.order_by(desc(Complaint.created_at)).all()

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
        request:schemas.Complaint,
        db: Session = Depends(get_db)
    ):
    status_code = status.HTTP_201_CREATED
    try:        
        data = Complaint(
            title = request.title,
            content = request.content,
            content_html = request.content_html,
            topic = request.topic,
            source = request.source
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
        data = db.query(Complaint).filter(Complaint.id==id)
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
        request: schemas.Complaint,
        db: Session = Depends(get_db)
    ):
    status_code=status.HTTP_202_ACCEPTED
    try:
        data = db.query(Complaint).filter(Complaint.id==id)
        if not data.first():
            status_code=status.HTTP_400_BAD_REQUEST
            raise Exception('data is not exist')
        data.update(
            {
                'title':request.title,
                'content':request.content,
                'content_html':request.content_html,
                'topic':request.topic,
                'source':request.source
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
        data = db.query(Complaint).filter(Complaint.id==id)
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

@router.get('/export/', status_code=status.HTTP_200_OK)
def list(
        db: Session = Depends(get_db),
        start_date: Optional[str] = "2024-12-01",
        end_date: Optional[str] = "2024-12-30"
    ):
    status_code = status.HTTP_200_OK
    try:
        list_complaint = db.query(Complaint).all()
        list_date = []
        list_creator = []
        list_title = []
        list_content = []
        list_topic = []
        list_source = []
        for complain in list_complaint:
            list_date.append(complain.created_at)
            list_creator.append(complain.created_by)
            list_title.append(complain.title)
            list_content.append(complain.content)
            list_topic.append(complain.topic)
            list_source.append(complain.source)

        list_result = {
            'Date': list_date,
            'By': list_creator,
            'Title': list_title,
            'Content': list_content,
            'Topic': list_topic,
            'Source': list_source,
        }

        df = pandas.DataFrame(data = list_result)
        file_name = "import_aduan.xlsx"
        df.to_excel(file_name, index=False)
        file_response = FileResponse(file_name, filename = file_name)
        return  file_response
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST if status_code==status.HTTP_200_OK else status_code,
            content={
                "message":str(e),
            }
        )
    
    
