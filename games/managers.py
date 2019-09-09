from django.db import models


class MineManager(models.Manager):
    def is_mine_on(self, x, y, game):
        return self.filter(x=x, y=y, game=game).exists()

    def create_mine(self, x, y, game):
        return self.create(x=x, y=y, game=game)

    def game_mines_queryset(self, game):
        return self.filter(game=game)

    def game_mines(self, game):
        return set(self.game_mines_queryset(game))


class MarkManager(models.Manager):
    def game_marks_queryset(self, game):
        return self.filter(game=game)

    def game_marks(self, game):
        return set(self.game_marks_queryset(game))


class FlagManager(models.Manager):
    def game_flags_queryset(self, game):
        return self.filter(game=game)

    def game_flags(self, game):
        return set(self.game_flags_queryset(game))
