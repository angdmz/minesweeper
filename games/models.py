from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from games.managers import FieldManager, GameManager


class Game(models.Model):
    size = models.IntegerField()
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, auto_now_add=True)
    end_date = models.DateTimeField(null=True)
    is_active= models.BooleanField(default=True)
    objects = GameManager()


class GameProxy(Game):
    class Meta:
        proxy = True


class Field(models.Model):
    game = models.ForeignKey(Game, db_column='game_id', on_delete=models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()
    symbol = models.CharField(max_length=1, default='E')
    objects = FieldManager()    # Perform initial map generation

    def is_mine(self):
        return self.symbol=='M'

    def is_empty(self):
        return self.symbol=='E'

    def __str__(self):
        return "X: {} Y: {} {}".format(str(self.x), str(self.y), str(self.symbol))
