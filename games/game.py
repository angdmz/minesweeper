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
    def user(self):
        return self.gamemodel.user

    def check_for_win(self):
        return not self.field_manager.are_empty_left_on(self.gamemodel)

    # Get a matrix version of the map
    @property
    def notrevealed_matrix(self):
        matrix = [[None for x in range(self.gamemodel.size)] for y in range(self.gamemodel.size)]
        fields = self.field_manager.game_fields(self.gamemodel)
        for f in fields:
            matrix[f.x][f.y] = '' if f.is_mine() or f.is_empty() else f.symbol
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
        matrix = [[None for x in range(self.gamemodel.size)] for y in range(self.gamemodel.size)]
        fields = self.field_manager.game_fields(self.gamemodel)
        for f in fields:
            matrix[f.x][f.y] = f.symbol
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
                result['map'] = game.revealed_matrix_string
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
                compiler = EmptiesCompiler(game.revealed_matrix)
                map_result = compiler.compile(x, y)
                self.field_manager.save_fields_matrix(map_result, game.gamemodel)
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


class EmptiesCompiler:

    def __init__(self, map_matrix):

        self.map_matrix = map_matrix

    def compile(self, x, y):
        empties = set(self.get_adj_empties(x, y))
        supers = self.get_unmarked_supers(empties)

        while supers:
            group = supers.pop()
            new_empties = self.get_adj_empties(group[0], group[1])
            new_supers = self.get_unmarked_supers(new_empties)
            supers = supers.union(new_supers)
            empties = empties.union(new_empties)
            self.define_count(group[0], group[1], str(group[2]))

        return self.map_matrix

    def get_adj_empties(self, x, y):
        bombs = self.count_adjacent_mines(x, y)
        empties = [(x, y, bombs)]
        coords = self.adj_coords(x, y)

        for pair in coords:
            out_of_bounds_x = pair[0] < 0 or pair[0] >= len(self.map_matrix)
            out_of_bounds_y = pair[1] < 0 or pair[1] >= len(self.map_matrix)

            if out_of_bounds_x or out_of_bounds_y:
                continue

            bombs = self.count_adjacent_mines(pair[0], pair[1])
            pair.append(bombs)
            empties.append(tuple(pair))

            if bombs != 0:
                self.define_count(pair[0], pair[1], str(bombs))

        return empties

    def get_unmarked_supers(self, superclears):
        supers = set()
        for group in superclears:
            if group[2] == 0 and self.is_empty_on(group[0], group[1]):
                supers.add(group)
        return supers

    def is_empty_on(self, x, y):
        return self.map_matrix[x][y] == 'E'

    def count_adjacent_mines(self, x, y):
        count = 0
        coords = self.adj_coords(x, y)

        for pair in coords:
            out_of_bounds_x = pair[0] < 0 or pair[0] >= len(self.map_matrix)
            out_of_bounds_y = pair[1] < 0 or pair[1] >= len(self.map_matrix)

            if out_of_bounds_x or out_of_bounds_y:
                continue

            if self.is_mine_on(pair[0], pair[1]):
                count += 1

        return count

    def adj_coords(self, x, y):
        return [
            [x - 1, y],
            [x - 1, y - 1],
            [x, y - 1],
            [x + 1, y - 1],
            [x + 1, y],
            [x + 1, y + 1],
            [x, y + 1],
            [x - 1, y + 1]
        ]

    def is_mine_on(self, x, y):
        return self.map_matrix[x][y] == 'M'

    def define_count(self, x, y, count):
        self.map_matrix[x][y] = count


class InvalidSizeParameterException(Exception):
    pass


class InvalidMinesParameterException(Exception):
    pass
