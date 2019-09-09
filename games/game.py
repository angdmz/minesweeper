import random
from games.models import Game as GameModel
from games.models import Mine as MineModel
from games.models import Mark as MarkModel
from games.models import Flag as FlagModel

from django.db import transaction

class GameWrapper:
    game_manager = GameModel.objects
    mine_manager = MineModel.objects
    mark_manager = MarkModel.objects
    flag_manager = FlagModel.objects

    def __init__(self, gamemodel):
        self.gamemodel = gamemodel

    @property
    def is_active(self):
        return self.gamemodel.is_active

    @property
    def mine_count(self):
        return len(self.mine_manager.game_mines(self.gamemodel))

    @property
    def size(self):
        return self.gamemodel.size

    @property
    def flag_count(self):
        return len(self.flag_manager.game_flags(self.gamemodel))

    @property
    def mark_count(self):
        return len(self.mark_manager.game_marks(self.gamemodel))

    @property
    def user(self):
        return self.gamemodel.user


class RandomGameStarter:
    game_manager = GameModel.objects
    mine_manager = MineModel.objects

    def start_game(self, size, mines, user):
        if size < 0:
            raise InvalidSizeParameterException("Size is {}, must be greater than zero")
        if mines < 0:
            raise InvalidMinesParameterException("Mines is {}, must be greater than zero")

        with transaction.atomic():
            game = self.game_manager.create(user=user, size=size)
            created_mines = 0
            while created_mines < mines:
                x = random.randint(0, size - 1)
                y = random.randint(0, size - 1)
                if not self.mine_manager.is_mine_on(x, y, game):
                    self.mine_manager.create_mine(x, y, game)
                    created_mines = created_mines + 1

        return GameWrapper(game)


class GameIsNotActiveException(Exception):
    pass


class GameInteractor:
    def mark(self, game, x, y):
        if not game.is_active:
            raise GameIsNotActiveException("Game is not active")
        return


class InvalidSizeParameterException(Exception):
    pass


class InvalidMinesParameterException(Exception):
    pass