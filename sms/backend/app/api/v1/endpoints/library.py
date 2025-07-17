"""
Library management API endpoints.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, and_, or_, select, literal, text, exists
from sqlalchemy.sql.expression import true, false

from app.core.deps import get_db, get_current_user
from app.models.user import User, Role
from app.schemas.library import (
    Book, BookCreate, BookUpdate, BookWithCategory,
    BookCategory, BookCategoryCreate, BookCategoryUpdate,
    BookIssue, BookIssueCreate, BookIssueUpdate, BookIssueWithDetails,
    BookReservation, BookReservationCreate, BookReservationUpdate, BookReservationWithDetails,
    LibrarySettingsBase
)
from app.models.library import (
    Book as BookModel,
    BookCategory as BookCategoryModel,
    BookIssue as BookIssueModel,
    BookReservation as BookReservationModel,
    LibrarySettings as LibrarySettingsModel,
    BookStatus
)


router = APIRouter()


# Book Category endpoints
@router.get("/categories", response_model=List[BookCategory])
def get_book_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve book categories.
    """
    categories = db.query(BookCategoryModel).offset(skip).limit(limit).all()
    return categories


@router.post("/categories", response_model=BookCategory, status_code=status.HTTP_201_CREATED)
def create_book_category(
    category: BookCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new book category.
    """
    # Check if user has admin or librarian role
    if current_user.role.name not in ["admin", "librarian"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if category already exists
    db_category = db.query(BookCategoryModel).filter(BookCategoryModel.name == category.name).first()
    if db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    # Create new category
    db_category = BookCategoryModel(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/categories/{category_id}", response_model=BookCategory)
def get_book_category(
    category_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific book category by ID.
    """
    category = db.query(BookCategoryModel).filter(BookCategoryModel.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.put("/categories/{category_id}", response_model=BookCategory)
def update_book_category(
    category: BookCategoryUpdate,
    category_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a book category.
    """
    # Check if user has admin or librarian role
    if current_user.role.name not in ["admin", "librarian"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_category = db.query(BookCategoryModel).filter(BookCategoryModel.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Update category fields
    update_data = category.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_category(
    category_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a book category.
    """
    # Check if user has admin role
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_category = db.query(BookCategoryModel).filter(BookCategoryModel.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if category has books
    books_count = db.query(BookModel).filter(BookModel.category_id == category_id).count()
    if books_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with books"
        )
    
    db.delete(db_category)
    db.commit()
    return None


# Book endpoints
@router.get("/books", response_model=List[BookWithCategory])
def get_books(
    skip: int = 0,
    limit: int = 100,
    title: Optional[str] = None,
    author: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[BookStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve books with optional filtering.
    """
    query = db.query(BookModel)
    
    # Apply filters if provided
    if title:
        query = query.filter(BookModel.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(BookModel.author.ilike(f"%{author}%"))
    if category_id:
        query = query.filter(BookModel.category_id == category_id)
    if status:
        query = query.filter(BookModel.status == status)
    
    books = query.offset(skip).limit(limit).all()
    return books


@router.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new book.
    """
    # Check if user has admin or librarian role
    if current_user.role.name not in ["admin", "librarian"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if category exists if provided
    if book.category_id:
        category = db.query(BookCategoryModel).filter(BookCategoryModel.id == book.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID {book.category_id} not found"
            )
    
    # Create new book
    db_book = BookModel(**book.dict())
    db.add(db_book)
    try:
        db.commit()
        db.refresh(db_book)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book with this ISBN already exists"
        )
    
    return db_book


@router.get("/books/{book_id}", response_model=BookWithCategory)
def get_book(
    book_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific book by ID.
    """
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book


@router.put("/books/{book_id}", response_model=Book)
def update_book(
    book_update: BookUpdate,
    book_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a book.
    """
    # Check if user has admin or librarian role
    if current_user.role.name not in ["admin", "librarian"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check if category exists if provided
    if book_update.category_id:
        category = db.query(BookCategoryModel).filter(BookCategoryModel.id == book_update.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID {book_update.category_id} not found"
            )
    
    # Update book fields
    update_data = book_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    try:
        db.commit()
        db.refresh(db_book)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book with this ISBN already exists"
        )
    
    return db_book


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a book.
    """
    # Check if user has admin or librarian role
    if current_user.role.name not in ["admin", "librarian"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check if book has active issues
    active_issues_count = db.query(BookIssueModel).filter(
        BookIssueModel.book_id == book_id,
        BookIssueModel.returned == False
    ).count()
    
    if active_issues_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete book with active loans"
        )
    
    db.delete(db_book)
    db.commit()
    return None


# Book Issue endpoints
@router.get("/issues", response_model=List[BookIssue])
def get_book_issues(
    skip: int = 0,
    limit: int = 100,
    returned: Optional[bool] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve book issues with optional filtering.
    """
    # Regular users can only see their own issues
    if current_user.role.name not in ["admin", "librarian", "teacher"]:
        user_id = current_user.id
    
    query = db.query(BookIssueModel)
    
    # Apply filters
    if returned is not None:
        query = query.filter(BookIssueModel.returned == returned)
    if user_id:
        query = query.filter(BookIssueModel.user_id == user_id)
    
    issues = query.offset(skip).limit(limit).all()
    return issues


@router.post("/issues", response_model=BookIssue, status_code=status.HTTP_201_CREATED)
def create_book_issue(
    issue: BookIssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new book issue (loan).
    """
    # Check if user has admin or librarian role, or is creating for themselves
    if current_user.role.name not in ["admin", "librarian"] and current_user.id != issue.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if book exists and is available
    book = db.query(BookModel).filter(BookModel.id == issue.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {issue.book_id} not found"
        )
    
    # Check if the book has available copies - avoid comparing column directly
    available_copies = db.query(BookModel.available_copies).filter(
        BookModel.id == issue.book_id
    ).scalar()
    
    if available_copies is None or available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book is not available for loan"
        )
    
    # Check if user exists
    user = db.query(User).filter(User.id == issue.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {issue.user_id} not found"
        )
    
    # Check library settings for max loans
    lib_settings = db.query(LibrarySettingsModel).first()
    if not lib_settings:
        # Create default settings if not exist
        lib_settings = LibrarySettingsModel()
        db.add(lib_settings)
        db.commit()
    
    # Count user's active loans
    user_active_loans_count = db.query(BookIssueModel).filter(
        BookIssueModel.user_id == issue.user_id,
        BookIssueModel.returned == False
    ).count()
    
    # Determine the maximum loans based on user role
    max_loans = (
        lib_settings.max_books_per_staff 
        if user.role.name in ["admin", "librarian", "teacher"] 
        else lib_settings.max_books_per_student
    )
    
    # Check if user has reached the loan limit
    # SQLAlchemy count() returns an integer directly
    if user_active_loans_count >= max_loans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User has reached the maximum limit of {max_loans} books"
        )
    
    # Create new issue
    db_issue = BookIssueModel(**issue.dict())
    db.add(db_issue)
    
    # Execute update statement to decrease available copies
    # Use case/when for conditional logic instead of Python if/else in the update values
    stmt = (
        update(BookModel)
        .where(BookModel.id == issue.book_id)
        .values({
            "available_copies": BookModel.available_copies - 1
        })
    )
    db.execute(stmt)
    
    # Separate update for the status to avoid conditional issues
    if available_copies <= 1:
        status_stmt = (
            update(BookModel)
            .where(BookModel.id == issue.book_id)
            .values({
                "status": BookStatus.ISSUED
            })
        )
        db.execute(status_stmt)
    
    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.get("/issues/{issue_id}", response_model=BookIssue)
def get_book_issue(
    issue_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific book issue by ID.
    """
    issue = db.query(BookIssueModel).filter(BookIssueModel.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Regular users can only see their own issues
    is_admin_or_teacher = current_user.role.name in ["admin", "librarian", "teacher"]
    is_owner = issue.user_id == current_user.id
    
    # Convert SQLAlchemy expression to Python boolean
    if not (is_admin_or_teacher or bool(db.query(literal(True)).filter(issue.user_id == current_user.id).scalar())):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return issue


@router.put("/issues/{issue_id}/return", response_model=BookIssue)
def return_book(
    issue_id: int = Path(..., gt=0),
    fine_amount: Optional[int] = None,
    remarks: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return a book and update the issue record.
    """
    # Check if user has admin or librarian role
    if current_user.role.name not in ["admin", "librarian"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to return books in system"
        )
    
    # Get the issue record
    issue = db.query(BookIssueModel).filter(BookIssueModel.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check if the issue is already returned
    is_returned = db.query(BookIssueModel.returned).filter(BookIssueModel.id == issue_id).scalar()
    
    if is_returned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book already returned"
        )
    
    # Update the issue record using an update statement
    update_values = {
        "returned": True,
        "return_date": date.today()
    }
    
    if fine_amount is not None:
        update_values["fine_amount"] = fine_amount
    
    if remarks:
        update_values["remarks"] = remarks
    
    stmt = (
        update(BookIssueModel)
        .where(BookIssueModel.id == issue_id)
        .values(**update_values)
    )
    db.execute(stmt)
    
    # Get book information
    book = db.query(BookModel).filter(BookModel.id == issue.book_id).first()
    
    if book:
        # Update book's available copies
        book_stmt = (
            update(BookModel)
            .where(BookModel.id == issue.book_id)
            .values({
                "available_copies": BookModel.available_copies + 1
            })
        )
        db.execute(book_stmt)
        
        # Separate status update to avoid conditional issues
        book_status = db.query(BookModel.status).filter(BookModel.id == book.id).scalar()
        if book_status == BookStatus.ISSUED:
            status_stmt = (
                update(BookModel)
                .where(BookModel.id == issue.book_id)
                .values({
                    "status": BookStatus.AVAILABLE
                })
            )
            db.execute(status_stmt)
    
    db.commit()
    
    # Refresh the issue record
    updated_issue = db.query(BookIssueModel).filter(BookIssueModel.id == issue_id).first()
    return updated_issue


@router.put("/issues/{issue_id}", response_model=BookIssue)
def update_book_issue(
    issue_update: BookIssueUpdate,
    issue_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a book issue.
    """
    # Check if user has admin or librarian role
    if current_user.role.name not in ["admin", "librarian"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get the issue
    db_issue = db.query(BookIssueModel).filter(BookIssueModel.id == issue_id).first()
    if not db_issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Update issue fields
    update_data = issue_update.dict(exclude_unset=True)
    
    # Check if we're marking the issue as returned
    was_returned = db.query(BookIssueModel.returned).filter(BookIssueModel.id == issue_id).scalar() or False
    will_return = "returned" in update_data and update_data["returned"] and not was_returned
    
    if will_return:
        update_data["return_date"] = update_data.get("return_date", date.today())
        
        # Get book information
        book = db.query(BookModel).filter(BookModel.id == db_issue.book_id).first()
        
        if book:
            # Update book's available copies
            book_stmt = (
                update(BookModel)
                .where(BookModel.id == db_issue.book_id)
                .values({
                    "available_copies": BookModel.available_copies + 1
                })
            )
            db.execute(book_stmt)
            
            # Separate status update to avoid conditional issues
            book_status = db.query(BookModel.status).filter(BookModel.id == book.id).scalar()
            if book_status == BookStatus.ISSUED:
                status_stmt = (
                    update(BookModel)
                    .where(BookModel.id == db_issue.book_id)
                    .values({
                        "status": BookStatus.AVAILABLE
                    })
                )
                db.execute(status_stmt)
    
    # Update the issue record
    for field, value in update_data.items():
        setattr(db_issue, field, value)
    
    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.get("/library-settings", response_model=LibrarySettingsBase)
def get_library_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve library settings.
    """
    settings = db.query(LibrarySettingsModel).first()
    if not settings:
        # Create default settings
        settings = LibrarySettingsModel()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/library-settings", response_model=LibrarySettingsBase)
def update_library_settings(
    settings: LibrarySettingsBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update library settings.
    """
    # Check if user has admin role
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_settings = db.query(LibrarySettingsModel).first()
    if not db_settings:
        # Create settings if not exist
        db_settings = LibrarySettingsModel(**settings.dict())
        db.add(db_settings)
    else:
        # Update existing settings
        for field, value in settings.dict().items():
            setattr(db_settings, field, value)
    
    db.commit()
    db.refresh(db_settings)
    return db_settings 