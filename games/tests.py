from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from games.game import RandomGameStarter, InvalidSizeParameterException, InvalidMinesParameterException, GameInteractor


class TestsCommonGenerator:
    def generate(self):
        User.objects.create(username="test")
        setattr(self,'user', User.objects.get(username='test'))


class TestRandomGameStarter(TestCase, TestsCommonGenerator):
    user = None

    def setUp(self) -> None:
        self.generate()

    def test_start_valid_game(self):
        starter = RandomGameStarter()
        game = starter.start_game(8, 10, self.user)
        self.assertTrue(game.is_active)
        self.assertEqual(10, game.mine_count)
        self.assertEqual(0, game.flag_count)
        self.assertEqual(0, game.mark_count)
        self.assertEqual(8,game.size)
        self.assertEqual(self.user, game.user)

    def test_start_invalid_game(self):
        starter = RandomGameStarter()
        self.assertRaises(InvalidSizeParameterException, starter.start_game, size=-8, mines=10, user=self.user)
        self.assertRaises(InvalidMinesParameterException, starter.start_game, size=10, mines=-8, user=self.user)


class TestGamePlay(TestCase, TestsCommonGenerator):
    user = None
    def setUp(self) -> None:
        self.generate()

    def test_make_valid_mark_non_flag(self):
        interactor = GameInteractor()
        starter = RandomGameStarter()
        game = starter.start_game(8, 10, self.user)
        game, mark = interactor.mark(game, 5, 5)
        self.assertEqual(10, game.flag_count)
