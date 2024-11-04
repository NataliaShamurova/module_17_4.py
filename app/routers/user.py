from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete

from typing import Annotated
from slugify import slugify

from app.backend.db_depends import get_db
from app.models import *
from app.schemas import CreateUser, UpdateUser

router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get('/user_id')
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    users = db.scalar(select(User).where(User.id == user_id))
    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User was not found")
    return users


@router.get('/user_id/task')
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    tasks = db.scalar(select(Task).where(Task.id == user_id)).all
    if tasks is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Task was not found")
    return tasks


@router.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], create_user: CreateUser):
    db.execute(insert(User).values(username=create_user.username,
                                   firstname=create_user.firstname,
                                   lastname=create_user.lastname,
                                   age=create_user.age,
                                   slug=slugify(create_user.username)))

    db.commit()

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int,
                      update_user: UpdateUser):
    users = db.scalar(select(User).where(User.id == user_id))
    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User was not found")

    db.execute(update(User).where(User.id == user_id).values(firstname=update_user.firstname,
                                                             lastname=update_user.lastname,
                                                             age=update_user.age))

    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User update is successful!'
    }


@router.delete('/delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    users = db.scalar(select(User).where(User.id == user_id))
    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User was not found")

    db.execute(delete(User).where(User.id == user_id))
    db.commit()

    # Удаляем задачи, связанные с пользователем
    db.execute(delete(Task).where(Task.user_id == user_id))
    # Удаляем пользователя
    db.execute(delete(User).where(User.id == user_id))
    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User delete is successful!'
    }
