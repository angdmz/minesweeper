from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from games.managers import MineManager, MarkManager, FlagManager


class Game(models.Model):
    size = models.IntegerField()
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, auto_now_add=True)
    end_date = models.DateTimeField(null=True)
    is_active= models.BooleanField(default=True)


class GameProxy(Game):
    class Meta:
        proxy = True


class Landable(models.Model):
    game = models.ForeignKey(Game, db_column='game_id', on_delete=models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()

    class Meta:
        abstract = True

class Mine(Landable):
    objects = MineManager()


class Mark(Landable):
    objects = MarkManager()
    create_date = models.DateTimeField(auto_now_add=True)


class Flag(Landable):
    objects = FlagManager()
    create_date = models.DateTimeField(auto_now_add=True)
