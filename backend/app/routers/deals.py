
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.company import Company
from app.models.contact import Contact
from app.models.deal import Deal
from app.schemas.deal import DealCreate, DealResponse, DealUpdate


router = APIRouter(
    prefix="/deals",
    tags=["Deals"],
)


@router.post("", response_model=DealResponse, status_code=201)
def create_deal(
    deal_data: DealCreate,
    db: Session = Depends(get_db),
):
    # Verify that the company exists
    company = db.get(Company, deal_data.company_id)

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    # Verify the contact belongs to this company
    if deal_data.contact_id is not None:
        contact = db.get(Contact, deal_data.contact_id)

        if contact is None:
            raise HTTPException(
                status_code=404,
                detail="Contact not found",
            )

        if contact.company_id != deal_data.company_id:
            raise HTTPException(
                status_code=422,
                detail="Contact does not belong to this company",
            )

    # Create and save the deal
    new_deal = Deal(
        **deal_data.model_dump(mode="json")
    )

    db.add(new_deal)
    db.commit()
    db.refresh(new_deal)

    return new_deal



@router.get("", response_model=list[DealResponse])
def get_deals(
    db: Session = Depends(get_db),
):
    deals = db.scalars(
        select(Deal).order_by(Deal.id)
    ).all()

    return deals



@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(
    deal_id: int,
    db: Session = Depends(get_db),
):
    deal = db.get(Deal, deal_id)

    if deal is None:
        raise HTTPException(
            status_code=404,
            detail="Deal not found",
        )

    return deal


@router.patch("/{deal_id}", response_model=DealResponse)
def update_deal(
    deal_id: int,
    deal_data: DealUpdate,
    db: Session = Depends(get_db),
):
    # Find the existing deal
    deal = db.get(Deal, deal_id)

    if deal is None:
        raise HTTPException(
            status_code=404,
            detail="Deal not found",
        )

    # Only update fields included in the request
    updates = deal_data.model_dump(exclude_unset=True)

    # Prevent null values in required database columns
    required_fields = {
        "title",
        "value",
        "stage",
        "company_id",
    }

    for field in required_fields:
        if field in updates and updates[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null",
            )

    # Determine the resulting company and contact
    company_id = updates.get(
        "company_id",
        deal.company_id,
    )

    contact_id = updates.get(
        "contact_id",
        deal.contact_id,
    )

    # Verify the resulting company exists
    if "company_id" in updates:
        company = db.get(Company, company_id)

        if company is None:
            raise HTTPException(
                status_code=404,
                detail="Company not found",
            )

    # Verify the resulting contact belongs to the company
    if contact_id is not None:
        contact = db.get(Contact, contact_id)

        if contact is None:
            raise HTTPException(
                status_code=404,
                detail="Contact not found",
            )

        if contact.company_id != company_id:
            raise HTTPException(
                status_code=422,
                detail="Contact does not belong to this company",
            )

    # Apply the validated changes
    for field, value in updates.items():
        setattr(deal, field, value)

    db.commit()
    db.refresh(deal)

    return deal


@router.delete("/{deal_id}", status_code=204)
def delete_deal(
    deal_id: int,
    db: Session = Depends(get_db),
):
    deal = db.get(Deal, deal_id)

    if deal is None:
        raise HTTPException(
            status_code=404,
            detail="Deal not found",
        )

    db.delete(deal)
    db.commit()
