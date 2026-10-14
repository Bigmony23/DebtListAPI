import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth2 import AuthJWT
from sqlalchemy.orm import Session, joinedload, query

from models import Users, Debt, Person

from database import get_db,engine
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import or_

from schema import DebtCreateModel,DebtResponse

debt_router=APIRouter(
    prefix="/debts",
)

@debt_router.post('/',response_model=DebtResponse)
def create_debt(debt:DebtCreateModel,Authorize: AuthJWT = Depends(),db:Session=Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = db.query(Users).filter(Users.username == current_user).first()
    name=debt.person_full_name
    if not name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Person name cannot be empty")
    person=(db.query(Person).filter(Person.user_id==user.id,Person.full_name==name).first())
    if not person:
        person=Person(user_id=user.id,full_name=name)
        db.add(person)
        db.commit()
    new_debt=Debt(
        user_id=user.id,
        person_id=person.id,
        debt_type=debt.debt_type,
        summa=debt.summa,
        currency=debt.currency,
        description=debt.description,
        date_get=debt.date_get,
        date_give=debt.date_give,
        reminder_at=debt.reminder_at,
    )
    db.add(new_debt)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Could not save debt')
    db.refresh(new_debt)
    return new_debt



@debt_router.get('/list')
def get_debt(debt_type:str, person_id: int = None,Authorize: AuthJWT = Depends(),db:Session=Depends(get_db)):
    Authorize.jwt_required()
    current_user=Authorize.get_jwt_subject()
    user=db.query(Users).filter(Users.username==current_user).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

    if debt_type=='owed_to':
        debt_owed_to = db.query(Debt).filter(Debt.user_id == user.id,Debt.debt_type=='owed_to').all()
        if not debt_owed_to:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Debt not found")
        data=[{
            "success":True,
            "code":200,
            "date_get":debts.date_get,
            "date_give":debts.date_give,
            "description":debts.description,
            "summa":debts.summa,
            "currency":debts.currency,




        } for debts in debt_owed_to
        ]

        return data
    elif debt_type=='owed_by':
        debt_owed_by = db.query(Debt).filter(Debt.user_id == user.id, Debt.debt_type == 'owed_by').all()
        if not debt_owed_by:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debt not found, good job you owe to no one")
        data = [{
            "success": True,
            "code": 200,
            "date_get": debts.date_get,
            "date_give": debts.date_give,
            "description": debts.description,
            "summa": debts.summa,
            "currency": debts.currency,

        } for debts in debt_owed_by
        ]
        return data
    elif debt_type == 'individual':

        query = (db.query(Person).options(joinedload(Person.debts)).filter(Person.user_id == user.id))
        if person_id is not None:
            query = query.filter(Person.id == person_id)
        persons = query.all()

        if person_id is not None and not persons:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Person not found")
        result=[]
        for p in persons:
            totals={}
            debts_list=[]
            for d in p.debts:
                t=totals.setdefault(d.currency,{"given":0,"taken":0})
                if d.debt_type =="owed_to":
                    t["given"]+=d.summa
                else:
                    t["taken"]+=d.summa
                debts_list.append({
                        "id":d.id,
                        "debt_type":d.debt_type,
                        "currency":d.currency,
                        "description":d.description,
                        "summa":d.summa,
                        "date_get":d.date_get,
                        "date_give":d.date_give,
                        "reminder_at":d.reminder_at,

                    })
                result.append({
                        "person_id":p.id,
                        "full_name":p.full_name,
                        "totals": [
                    {"currency": c, "given": v["given"], "taken": v["taken"],
                     "balance": v["given"] - v["taken"]}
                            for c, v in totals.items()
                    ],
                    "debts": debts_list,
                    })
        return {"success":True,"people":result}






