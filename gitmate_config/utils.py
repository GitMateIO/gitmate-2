from django.contrib.auth.models import User

from IGitt.Interfaces.User import User as IGittUser
from IGitt.Interfaces import Token
from social_django.models import UserSocialAuth


def store_user(user: IGittUser, token: Token):
    """
    Creates and stores an IGitt User object in the database.
    """
    db_user, _ = User.objects.get_or_create(username=user.username,
                                            email=user.data['email'])
    auth, _ = UserSocialAuth.get_or_create(
        user=db_user,
        provider=user.hoster,
        default={'extra_data': {'private_token': token.value}}
    )

    auth.save()
    return user
