import random


from games.models import Game as GameModel, Field

from django.db import transaction

class GameInformationService:
    game_manager = GameModel.objects
    field_manager = Field.objects

    def __init__(self, gamemodel):
        self.gamemodel = gamemodel

    @property
    def pk(self):
        return self.gamemodel.pk

    @property
    def is_active(self):
        return self.gamemodel.is_active

    @property
    def mine_count(self):
        return len(self.field_manager.game_mines(self.gamemodel))

    @property
    def size(self):
        return self.gamemodel.size

    @property
    def flag_count(self):
        return len(self.field_manager.game_flags(self.gamemodel))

    @property
    def mark_count(self):
        return len(self.field_manager.game_marks(self.gamemodel))

    @property
    def user(self):
        return self.gamemodel.user


    # Get a matrix version of the map
    @property
    def notrevealed_matrix(self):
        matrix = []
        for x in range(self.gamemodel.size):
            row = []
            for y in range(self.gamemodel.size):
                content = self.field_manager.find_field_by_coordenates(x, y)

                content_value = content.symbol
                # a non revealing matrix will show everything
                if content.is_mine() or content.is_empty():
                    content_value = ''
                row.append(content_value)
            matrix.append(row)

        return matrix

    @property
    def revealed_matrix(self):
        matrix = []

        for x in range(self.gamemodel.size):
            row = []
            for y in range(self.gamemodel.size):
                content = self.field_manager.find_field_by_coordenates(x, y)
                # a revealing matrix will show everything
                content_value = content.symbol
                if not content.is_mine():
                    content_value = self.field_manager.count_adjacent_mines(x, y)
                row.append(content_value)
            matrix.append(row)

        return matrix

class RandomMapGenerator:
    field_manager = Field.objects

    # Perform initial map generation
    def generate_map(self, game, size, mines):
        # Make empty map
        for x in range(size):
            for y in range(size):
                self.field_manager.new_empty_field(game, x, y)

        created_mines = 0
        while created_mines < mines:
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
            if not self.field_manager.is_mine_on(x, y, game):
                self.field_manager.create_mine(x, y, game)
                created_mines += 1


class RandomGameStarter:
    game_manager = GameModel.objects
    field_manager = Field.objects
    map_generator = RandomMapGenerator()

    def start_game(self, size, mines, user):
        if size < 0:
            raise InvalidSizeParameterException("Size is {}, must be greater than zero")
        if mines < 0:
            raise InvalidMinesParameterException("Mines is {}, must be greater than zero")

        with transaction.atomic():
            game = self.game_manager.create(user=user, size=size)
            self.map_generator.generate_map(game, size, mines)

        return GameInformationService(game)


class GameIsNotActiveException(Exception):
    pass

class MarkResult:

    def is_regular_space_hit(self):
        return

    def is_super_space_hit(self):
        return


class GameInteractor:
    game_manager = GameModel.objects
    field_manager = Field.objects

    def mark(self, game, x, y):
        if not game.is_active:
            raise GameIsNotActiveException("Game is not active")

        result = {}

        # User chose a bomb
        if self.field_manager.is_mine_on(x, y, game):
            result['status'] = 'dead'
            result['map'] = game.revealed_matrix
            self.field_manager.set_to_not_active(game)
            return result

        win = game.check_for_win()

        if win:
            result['status'] = 'win'
            result['map'] = game.get_map_matrix('reveal')
            self.field_manager.set_to_not_active(game)

        num_bombs = self.calculate_num_bombs(x, y, game)

        # Hit a regular space
        if num_bombs > 0:
            result['status'] = 'clear'
            result['num_bombs'] = num_bombs

        # Hit a super space
        elif num_bombs == 0:
            result['status'] = 'superclear'
            result['num_bombs'] = num_bombs
            result['empties'] = game.compile_empties(x, y)
            game.save()

        return result


    # precondition: field on x, y in game is empty
    def calculate_num_bombs(self, x, y, game):
        num_bombs = self.field_manager.count_adjacent_mines(x, y, game)
        self.field_manager.define_count(x, y, str(num_bombs), game)
        return num_bombs



class InvalidSizeParameterException(Exception):
    pass


class InvalidMinesParameterException(Exception):
    pass