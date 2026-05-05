from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate, PaginatedPostsResponse

from auth import CurrentUser

router = APIRouter()

# @app.get("/api/posts", response_model=list[PostResponse])
# def home():
#     return posts
## get_posts
# @app.get("/api/posts", response_model=list[PostResponse])
# def get_posts(db: Annotated[Session, Depends(get_db)]):
#     result = db.execute(select(models.Post))
#     posts = result.scalars().all()
#     return posts

## get_posts
@router.get("", response_model=PaginatedPostsResponse)
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)], skip: Annotated[int, Query(ge=0)] = 0, limit: Annotated[int, Query(ge=1, le=100)] = 10,):
    count_result = await db.execute(select(func.count()).select_from(models.Post))
    total = count_result.scalar() or 0
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
        .offset(skip)
        .limit(limit),
    )
    posts = result.scalars().all()

    has_more = skip + len(posts) < total

    return PaginatedPostsResponse(
        posts=[PostResponse.model_validate(post) for post in posts],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )



## Create Post
# @app.post(
#     "/api/posts",
#     response_model=PostResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_post(post: PostCreate):
#     new_id = max(p["id"] for p in posts) + 1 if posts else 1
#     new_post = {
#         "id": new_id,
#         "author": post.author,
#         "title": post.title,
#         "content": post.content,
#         "date_posted": "April 23, 2025",
#     }
#     posts.append(new_post)
#     return new_post

## create_post
@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(post: PostCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post

# @app.get("/api/posts/{post_id}", response_model=PostResponse)
# def get_post(post_id: int):
#     for post in posts:
#         if post.get("id") == post_id:
#             return post
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


## get_post
@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id),
    )
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

## update_post_full
@router.put("/{post_id}", response_model=PostResponse)
async def update_post_full(
    post_id: int,
    post_data: PostCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    post.title = post_data.title
    post.content = post_data.content

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post

# @app.patch("/api/posts/{post_id}", response_model=PostResponse)
# def update_post_partial(post_id: int, post_data: PostUpdate, db: Annotated[Session, Depends(get_db)]):
#     result = db.execute(select(models.Post).where(models.Post.id == post_id))
#     post = result.scalars().first()
#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
#     # with exclude unset = true doesn't wipe our content entirely it sends only the modification part by the user
#     update_data = post_data.model_dump(exclude_unset=True)
#     # field: value == title : title's name
#     for field, value in update_data.items():
#         setattr(post, field, value)

#     db.commit()
#     db.refresh(post)
#     return post

## update_post_partial
@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(
    post_id: int,
    post_data: PostUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    

    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post

## delete_post
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    

    await db.delete(post)
    await db.commit()