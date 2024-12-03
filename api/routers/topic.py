from fastapi import APIRouter, HTTPException, Depends, status, Response, Header, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, select
from api import config, schemas, models
from api.database import get_db
from api.models import Topic

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token/")

router = APIRouter(
    prefix="/api/topic",
    tags=['Topic']
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
        data = db.query(Topic).filter(Topic.name.ilike(f'%{search}%'))
        if sort == "asc":
            if order == 'name':
                data = data.order_by(Topic.name).all()
            else:
                data = data.order_by(Topic.created_at).all()
        else:
            if order == 'name':
                data = data.order_by(desc(Topic.name)).all()
            else:
                data = data.order_by(desc(Topic.created_at)).all()

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
        request:schemas.Topic,
        db: Session = Depends(get_db)
    ):
    status_code = status.HTTP_201_CREATED
    try:        
        is_duplicate = db.query(Topic).filter(Topic.name==request.name).first()
        if is_duplicate:
            raise Exception('name is duplicate')
        
        data = Topic(
            name = request.name,
            is_active = True
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
        data = db.query(Topic).filter(Topic.id==id)
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
        request: schemas.Topic,
        db: Session = Depends(get_db)
    ):
    status_code=status.HTTP_202_ACCEPTED
    try:
        data = db.query(Topic).filter(Topic.id==id)
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

@router.put('/{id}/enable', status_code=status.HTTP_202_ACCEPTED)
def enable(
        id:str,
        db: Session = Depends(get_db)
    ):
    status_code=status.HTTP_202_ACCEPTED
    try:
        data = db.query(Topic).filter(Topic.id==id)
        if not data.first():
            status_code=status.HTTP_400_BAD_REQUEST
            raise Exception('data is not exist')
        data.update(
            {
                'is_active': True
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

@router.put('/{id}/disable', status_code=status.HTTP_202_ACCEPTED)
def disable(
        id:str,
        db: Session = Depends(get_db)
    ):
    status_code=status.HTTP_202_ACCEPTED
    try:
        data = db.query(Topic).filter(Topic.id==id)
        if not data.first():
            status_code=status.HTTP_400_BAD_REQUEST
            raise Exception('data is not exist')
        data.update(
            {
                'is_active': False
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
        data = db.query(Topic).filter(Topic.id==id)
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

