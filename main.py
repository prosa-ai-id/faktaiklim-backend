from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from api import models, config
from api.database import get_db
from sqlalchemy.orm import Session
from api.models import Article
from api.routers import article, complaint, dashboard, keyword, topic
from api.database import engine
from datetime import datetime, timedelta

import requests, json, jwt, hashlib

app = FastAPI()

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=['Content-Disposition']
)

models.Base.metadata.create_all(bind=engine)
app.include_router(topic.router)
app.include_router(keyword.router)
app.include_router(article.router)
app.include_router(complaint.router)
app.include_router(dashboard.router)

#app.mount("/static", StaticFiles(directory="static"), name="static")

'''
@app.post("/token")
def token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
    ):
    try:
        hashuserpass = generateHashPassword(form_data.password)
        user = db.query(User).filter(User.username==form_data.username).filter(User.userpass==hashuserpass).first()
        if not user:
            raise Exception('username and password is not match or exist')
        data = {
            "userid": str(user.id),
            "username": user.username,
            "fullname": user.fullname,
            "role": user.role,
            "prodi": user.prodi
        }
        token = jwt.encode(data, config.SECRET_KEY, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message":str(e),
            }
        )
'''