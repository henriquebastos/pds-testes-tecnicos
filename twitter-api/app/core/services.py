from django.utils import timezone

from core.models import Post
from core.models import User


class CannotFollowYourself(Exception):
    ...


class MaximumLimitPostsForToday(Exception):
    ...


class FollowService:
    def can_follow(self, user_id: int, following_id: int):
        if user_id == following_id:
            raise CannotFollowYourself("You can not follow yourself.")
        return True

    def follow_user(self, user_id: int, data):
        self.can_follow(user_id, data.get("user_id"))
        user = User.objects.get(id=user_id)
        user.following.add(data.get("user_id"))

    def unfollow_user(self, user_id: int, data):
        user = User.objects.get(id=user_id)
        user.following.remove(data.get("user_id"))


class PostService:
    def can_post(self, user_id: int):
        now = timezone.now()

        count = Post.objects.filter(
            user_id=user_id,
            created_at__day=now.day,
            created_at__month=now.month,
            created_at__year=now.year,
        ).count()

        if count >= 5:
            raise MaximumLimitPostsForToday(
                "You have reached the maximum number for creating posts today."
            )

        return True

    def create_post(self, user_id: int, data):
        self.can_post(user_id)
        post = Post.objects.create(**data, user_id=user_id)
        return post

    def create_repost(self, user_id: int, data):
        self.can_post(user_id)
        post = Post.objects.get(id=data.get("post_id"))
        repost = Post.objects.create(
            user_id=user_id,
            type=Post.Type.REPOST,
            content=post.content,
        )
        return repost

    def create_quote_post(self, user_id: int, data):
        self.can_post(user_id)
        post = Post.objects.get(id=data.get("post_id"))
        quote_post = Post.objects.create(
            user_id=user_id,
            type=Post.Type.QUOTE,
            content=post.content,
            comment=data.get("comment"),
        )
        return quote_post

    def all_posts(self):
        return Post.objects.all().order_by("-created_at")

    def following_posts(self, user_id):
        user = User.objects.get(id=user_id)

        return (
            Post.objects.all()
            .filter(user_id__in=user.following.all().values("id"))
            .order_by("-created_at")
        )


class UserService:
    def is_following(self, user_id, following_user_id):
        user = User.objects.get(id=user_id)
        return user.following.filter(id=following_user_id).exists()

    def posts_for(self, user_id):
        return Post.objects.filter(user_id=user_id).order_by("-created_at")
