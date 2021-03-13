from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from API.Endpoints import BaseEndpoint

from API.Schemas.blog.post import Post
from API.Schemas.user import User

from API.auth import check_authentication

posts = [
    {
        "id": 1,
        "title": "Pancake",
        "content": "Lorem Ipsum ..."
    }
]


class Posts(BaseEndpoint):
    route = APIRouter(prefix="/blog")

    tags = ["posts"]

    @staticmethod
    @route.get("/posts", tags=tags)
    async def get_posts() -> dict:
        return {"data": posts}

    @staticmethod
    @route.get("/posts/{id}", tags=tags)
    async def get_single_post(id: int) -> [dict, HTTPException]:
        error = HTTPException(status_code=404)
        if id > len(posts):
            return error

        for post in posts:
            if post["id"] == id:
                return {
                    "data": post
                }

        return error

    @staticmethod
    @route.post("/posts", tags=tags)
    async def add_post(post: Post, user: User = Depends(check_authentication)) -> dict:
        post.id = len(posts) + 1
        posts.append(post.dict())
        return {
            "data": "post added"
        }