
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.company import Company
from app.schemas.company import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
)

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
):
    new_company = Company(**company.model_dump())

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return new_company


@router.get(
    "",
    response_model=list[CompanyResponse],
)
def get_companies(
    db: Session = Depends(get_db),
):
    statement = select(Company).order_by(Company.id.asc())
    return db.scalars(statement).all()


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
):
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    return company


@router.patch(
    "/{company_id}",
    response_model=CompanyResponse,
)
def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: Session = Depends(get_db),
):
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    update_data = company_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return company


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
):
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    db.delete(company)
    db.commit()
