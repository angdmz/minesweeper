from django.db import models

class GameManager(models.Manager):

    def find_game_by_id(self, pk):
        return self.get(pk=pk)

    def set_to_not_active(self, game):
        game.active = False
        game.save()


class FieldManager(models.Manager):

    def game_fields_queryset(self, game):
        return self.filter(game=game)

    def game_fields(self, game):
        return set(self.game_fields_queryset(game))

    def game_mines_queryset(self, game):
        return self.filter(game=game, symbol='M')

    def game_mines(self, game):
        return set(self.game_mines_queryset(game))

    def new_empty_field(self, game, x, y):
        return self.create(game=game, x=x, y=y, symbol='E')

    def is_mine_on(self, x, y, game):
        return self.filter(x=x, y=y, game=game, symbol='M').exists()

    def is_empty_on(self, x, y, game):
        return self.filter(x=x, y=y, game=game, symbol='E').exists()

    def create_mine(self, x, y, game):
        return self.update_or_create(x=x, y=y, game=game, defaults={'symbol':'M'})

    def save_fields_matrix(self, fields_matrix, game):
        for x in range(len(fields_matrix)):
            for y in range(len(fields_matrix)):
                self.define_count(x, y, fields_matrix[x][y], game)

    def count_adjacent_mines(self, x, y, game):
        count = 0
        coords = self.adj_coords(x, y)

        for pair in coords:
            out_of_bounds_x = pair[0] < 0 or pair[0] >= game.size
            out_of_bounds_y = pair[1] < 0 or pair[1] >= game.size

            if out_of_bounds_x or out_of_bounds_y:
                continue

            if self.is_mine_on(pair[0], pair[1], game):
                count += 1

        return count

    def find_field_by_coordenates(self, x, y, game):
        return self.filter(game=game, x=x, y=y).first()

    def define_count(self, x, y, count, game):
        self.filter(game=game, x=x, y=y).update(symbol=str(count))

    def adj_coords(self, x, y):
        return [
          [x-1, y],
          [x-1, y-1],
          [x, y-1],
          [x+1, y-1],
          [x+1, y],
          [x+1, y+1],
          [x, y+1],
          [x-1, y+1]
        ]
    def are_empty_left_on(self, game):
        return self.filter(game=game, symbol='E').exists()
