import unittest
from main import Game

class TestNewGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_new_game(self):
        self.assertEqual(self.game.saved_file, None)

    def test_graph_get(self):
        self.graph.add("pikachu")
        self.assertEqual(self.graph.get("pikachu").weight, 1)

    def test_add_answer(self):
        self.game.graph["pikachu"] = 1
        self.assertEqual(self.game.graph["pikachu"], 1)

    def test_add_question(self):
        self.game.graph["Is it yellow?"] = 1
        self.assertEqual(self.game.graph["Is it yellow?"], 1)

    def test_add_answer_to_existing(self):
        self.game.graph["pikachu"] = 1
        self.assertEqual(self.game.graph["pikachu"], 1)
        self.game.graph["pikachu"] += 1
        self.assertEqual(self.game.graph["pikachu"], 2)

class TestLoadGame(unittest.TestCase):
    def setUp(self):
        self.game = Game("saved-2018-09-08.csv")

    def test_new_game(self):
        self.assertEqual(self.game.saved_file, "saved-2018-09-08.csv")

if __name__ == "__main__":
    unittest.main()
