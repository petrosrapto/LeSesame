"""
Le Sésame Backend - Admin Router

Admin endpoints for user management.

Author: Petros Raptopoulos
Date: 2026/02/08
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db, User, UserRepository
from ..schemas import (
    AdminUserResponse,
    AdminUserListResponse,
    AdminApproveRequest,
    AdminRoleRequest,
    AdminBulkDeleteRequest,
    UserActivityResponse,
    UserActivityListResponse,
)
from ..routers.auth import require_admin
from ..core import logger

router = APIRouter()


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    admin: Annotated[User, Depends(require_admin)],
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List all users (admin only)."""
    repo = UserRepository(db)
    users, total = await repo.get_all_users(page=page, per_page=per_page)
    
    return AdminUserListResponse(
        users=[AdminUserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("/users/approve")
async def approve_user(
    request: AdminApproveRequest,
    admin: Annotated[User, Depends(require_admin)],
    db: AsyncSession = Depends(get_db),
):
    """Approve a user account (admin only)."""
    repo = UserRepository(db)
    user = await repo.get_by_id(request.user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_approved:
        return {"message": f"User '{user.username}' is already approved."}
    
    await repo.approve_user(user)
    logger.info(f"Admin {admin.username} approved user {user.username}")
    
    return {"message": f"User '{user.username}' has been approved."}


@router.post("/users/disapprove")
async def disapprove_user(
    request: AdminApproveRequest,
    admin: Annotated[User, Depends(require_admin)],
    db: AsyncSession = Depends(get_db),
):
    """Revoke approval from a user account (admin only)."""
    repo = UserRepository(db)
    user = await repo.get_by_id(request.user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot disapprove yourself.")
    
    await repo.disapprove_user(user)
    logger.info(f"Admin {admin.username} disapproved user {user.username}")
    
    return {"message": f"User '{user.username}' approval has been revoked."}


@router.post("/users/role")
async def change_user_role(
    request: AdminRoleRequest,
    admin: Annotated[User, Depends(require_admin)],
    db: AsyncSession = Depends(get_db),
):
    """Change a user's role (admin only)."""
    repo = UserRepository(db)
    user = await repo.get_by_id(request.user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot change your own role.")
    
    await repo.set_role(user, request.role)
    logger.info(f"Admin {admin.username} changed role of {user.username} to {request.role}")
    
    return {"message": f"User '{user.username}' role changed to '{request.role}'."}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: Annotated[User, Depends(require_admin)],
    db: AsyncSession = Depends(get_db),
):
    """Delete a user and all their data (admin only)."""
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself.")
    
    username = user.username
    await repo.delete_user_cascade(user)
    logger.info(f"Admin {admin.username} deleted user {username}")
    
    return {"message": f"User '{username}' and all related data have been deleted."}


@router.post("/users/bulk-delete")
async def bulk_delete_users(
    request: AdminBulkDeleteRequest,
    admin: Annotated[User, Depends(require_admin)],
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple users and all their data (admin only)."""
    repo = UserRepository(db)
    deleted = []
    skipped = []

    for user_id in request.user_ids:
        if user_id == admin.id:
            skipped.append(user_id)
            continue
        user = await repo.get_by_id(user_id)
        if not user:
            skipped.append(user_id)
            continue
        username = user.username
        await repo.delete_user_cascade(user)
        deleted.append(username)

    logger.info(f"Admin {admin.username} bulk-deleted {len(deleted)} user(s): {deleted}")
    return {
        "message": f"{len(deleted)} user(s) deleted.",
        "deleted": deleted,
        "skipped_ids": skipped,
    }


@router.get("/activity", response_model=UserActivityListResponse)
async def get_activity_logs(
    admin: Annotated[User, Depends(require_admin)],
    user_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get user activity logs (admin only). Optionally filter by user_id."""
    repo = UserRepository(db)
    logs, total = await repo.get_activity_logs(user_id=user_id, page=page, per_page=per_page)

    # Build responses – attach username via the user relationship
    activities = []
    for log in logs:
        # Eagerly load user if not already loaded
        if log.user:
            uname = log.user.username
        else:
            user = await repo.get_by_id(log.user_id)
            uname = user.username if user else "unknown"
        activities.append(
            UserActivityResponse(
                id=log.id,
                user_id=log.user_id,
                username=uname,
                action=log.action,
                detail=log.detail,
                ip_address=log.ip_address,
                timestamp=log.timestamp,
            )
        )

    return UserActivityListResponse(
        activities=activities,
        total=total,
        page=page,
        per_page=per_page,
    )
