
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.company import Company
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate


router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"],
)


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
):
    # Check whether the company exists
    company = db.get(Company, contact.company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    # Create the contact
    new_contact = Contact(**contact.model_dump())

    db.add(new_contact)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact conflicts with an existing record",
        )

    db.refresh(new_contact)

    return new_contact



@router.get(
    "",
    response_model=list[ContactResponse],
)
def get_contacts(
    company_id: int | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Contact)

    if company_id is not None:
        statement = statement.where(
            Contact.company_id == company_id
        )

    statement = statement.order_by(Contact.id.asc())

    contacts = db.scalars(statement).all()

    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
):
    contact = db.get(Contact, contact_id)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return contact


@router.patch(
    "/{contact_id}",
    response_model=ContactResponse,
)
def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: Session = Depends(get_db),
):
    contact = db.get(Contact, contact_id)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    update_data = contact_update.model_dump(exclude_unset=True)

    # Verify a new company exists before moving the contact
    if "company_id" in update_data:
        company = db.get(Company, update_data["company_id"])

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )

    for field, value in update_data.items():
        setattr(contact, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact update conflicts with an existing record",
        )

    db.refresh(contact)

    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
):
    contact = db.get(Contact, contact_id)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    db.delete(contact)
    db.commit()
    return None
