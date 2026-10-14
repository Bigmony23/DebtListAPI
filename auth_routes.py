import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth2 import AuthJWT
from sqlalchemy.engine import row
from sqlalchemy.orm import Session

from models import Users, Debt

from database import get_db
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import or_

from schema import SignUpModel, LoginModel, LoginResponseModel, UserCurrencyModel
from sqlalchemy import func, case

auth_router=APIRouter(
    prefix="/auth",
)


@auth_router.get("/")
async def homepage (Authorize: AuthJWT = Depends()):
    print('welcome hit reload check jwt')

    Authorize.jwt_required()
    print('jwt_required passed')

    return {"message": "This is sign up page"}

@auth_router.post("/signup",status_code=status.HTTP_201_CREATED)
async def sign_up(user: SignUpModel,db:Session=Depends(get_db)):
    db_email=db.query(Users).filter(Users.email==user.email).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail='User with this email already exists')
    db_username=db.query(Users).filter(Users.username==user.username).first()
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail='User with this username already exists')
    new_user=Users(
        username=user.username,
        name=user.name,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff,
    )
    db.add(new_user)
    db.commit()
    data={
        'id': new_user.id,
        'username': new_user.username,
        'name': new_user.name,
        'email': new_user.email,
        'is_active': new_user.is_active,
        'is_staff': new_user.is_staff,
    }
    response_model={
        'success': True,
        'code':201,
        'message':'User created successfully',
        'data':data
    }
    return response_model

@auth_router.post("/login",status_code=200,response_model=LoginResponseModel)
async def login(user:LoginModel,Authorize:AuthJWT=Depends(),db:Session=Depends(get_db)):
    # db_user=session.query(User).filter(User.username==user.username).first()
    access_lifetime=datetime.timedelta(minutes=10)
    refresh_lifetime=datetime.timedelta(days=3)
    email_or_username=db.query(Users).filter(or_
                                                 (Users.username==user.username_or_email,
                                                  Users.email==user.username_or_email)).first()
    if email_or_username  and check_password_hash(email_or_username.password,user.password):
        access_token=Authorize.create_access_token(subject=email_or_username.username,expires_time=access_lifetime)
        refresh_token=Authorize.create_refresh_token(subject=email_or_username.username, expires_time=refresh_lifetime)

        token={
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
        response={
            'success': True,
            'code':200,
            'message':'User logged in',
            'data':token
        }
        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Incorrect username or password')

@auth_router.get('/monitoring')
async def monitoring(Authorize: AuthJWT = Depends(),db:Session=Depends(get_db)):
    Authorize.jwt_required()
    current_user=Authorize.get_jwt_subject()
    user=db.query(Users).filter(Users.username==current_user).first()
    rows=(
        db.query(Debt.currency,
                 func.sum(case((Debt.debt_type=='owed_to',Debt.summa),else_=0)).label("total_given"),
                 func.sum(case((Debt.debt_type == 'owed_to', Debt.summa), else_=0)).label("total_taken"),)


    .filter(Debt.user_id==user.id)
    .group_by(Debt.currency)
    .all()
    )
    return {
        'success': True,
        "data":[
            {
                "currency":r.currency,
                "total_given":r.total_given,
                "total_taken":r.total_taken,
                "balance":r.total_given-r.total_taken,
            }
            for r in rows
        ]
    }
@auth_router.get('/settings')
async def settinds(Authorize: AuthJWT = Depends(),db:Session=Depends(get_db)):
    Authorize.jwt_required()
    current_user=Authorize.get_jwt_subject()
    user=db.query(Users).filter(Users.username==current_user).first()
    data={
        "success": True,
        "id":user.id,
        "username":user.username,
        "currency":user.currency,
    }
    return jsonable_encoder(data)

@auth_router.put('/valyuta')
async def valyuta(updated_data:UserCurrencyModel,Authorize: AuthJWT = Depends(),db:Session=Depends(get_db)):
    Authorize.jwt_required()
    current_user=Authorize.get_jwt_subject()
    user = db.query(Users).filter(Users.username == current_user).first()
    user.currency = updated_data.currency
    db.commit()
    db.refresh(user)
    data = {
        "success": True,
        "id": user.id,
        "username": user.username,
        "currency": user.currency,
    }
    return jsonable_encoder(data)






