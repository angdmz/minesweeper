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

    def check_for_win(self):
        return not self.field_manager.are_empty_left_on(self.gamemodel)

    # Get a matrix version of the map
    @property
    def notrevealed_matrix(self):
        matrix = []
        for y in range(self.gamemodel.size):
            row = []
            for x in range(self.gamemodel.size):
                content = self.field_manager.find_field_by_coordenates(x, y, self.gamemodel)
                content_value = content.symbol
                # a non revealing matrix will show everything
                if content.is_mine() or content.is_empty():
                    content_value = ''
                row.append(content_value)
            matrix.append(row)

        return matrix

    @property
    def notrevealed_matrix_string(self):
        matrix = self.notrevealed_matrix
        result = []
        for x in range(self.gamemodel.size):
            row = []
            for y in range(self.gamemodel.size):
                content = matrix[x][y] if matrix[x][y] is not '' else 'X'
                row.append(content)
            result.append("".join(row))

        return result

    @property
    def revealed_matrix(self):
        matrix = []

        for y in range(self.gamemodel.size):
            row = []
            for x in range(self.gamemodel.size):
                content = self.field_manager.find_field_by_coordenates(x, y, self.gamemodel)
                # a revealing matrix will show everything
                content_value = content.symbol
                if not content.is_mine():
                    content_value = self.field_manager.count_adjacent_mines(x, y, self.gamemodel)
                row.append(content_value)
            matrix.append(row)

        return matrix

    @property
    def revealed_matrix_string(self):
        matrix = self.revealed_matrix
        result = []
        for x in range(self.gamemodel.size):
            row = []
            for y in range(self.gamemodel.size):
                content = matrix[x][y] if matrix[x][y] is not '' else 'X'
                row.append(content)
            result.append("".join(row))
        return result

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
        if size <= 0:
            raise InvalidSizeParameterException("Size is {}, must be greater than zero".format(size))
        if mines <= 0:
            raise InvalidMinesParameterException("Mines is {}, must be greater than zero".format(mines))

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
        with transaction.atomic():
            # User chose a bomb
            if self.field_manager.is_mine_on(x, y, game.gamemodel):
                result['status'] = 'dead'
                result['map'] = game.revealed_matrix
                self.game_manager.set_to_not_active(game.gamemodel)
                return result
            num_bombs = self.field_manager.count_adjacent_mines(x, y, game.gamemodel)
            self.field_manager.define_count(x, y, str(num_bombs), game.gamemodel)
            win = game.check_for_win()
            if win:
                result['status'] = 'win'
                result['map'] = game.revealed_matrix_string
                self.game_manager.set_to_not_active(game.gamemodel)
                return result

            # Hit a regular space
            if num_bombs > 0:
                result['status'] = 'clear'
                result['num_bombs'] = num_bombs
                result['map'] = game.notrevealed_matrix_string

            # Hit a super space
            elif num_bombs == 0:
                result['status'] = 'superclear'
                result['num_bombs'] = num_bombs
                self.compile_empties(x, y, game.gamemodel)
                result['map'] = game.notrevealed_matrix_string

        return result

    # Perform chain reaction of supers to find all revealed coords
    def compile_empties(self, x, y, game):
        empties = set(self.field_manager.get_adj_empties(x, y, game))
        supers = self.field_manager.get_unmarked_supers(empties, game)

        while supers:
            group = supers.pop()
            new_empties = self.field_manager.get_adj_empties(group[0], group[1], game)
            new_supers = self.field_manager.get_unmarked_supers(new_empties, game)
            supers = supers.union(new_supers)
            empties = empties.union(new_empties)
            self.field_manager.define_count(group[0], group[1], str(group[2]), game)

        return list(empties)





class InvalidSizeParameterException(Exception):
    pass


class InvalidMinesParameterException(Exception):
    pass
