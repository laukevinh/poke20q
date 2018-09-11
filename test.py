import unittest
from main import Q, A
from main import Point, Node, Entry, Graph, Game

class TestNewGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_new_game(self):
        self.assertEqual(self.game.saved_file, None)

    def test_graph_get(self):
        self.game.graph.add(A, "venemoth", [])
        self.assertEqual(self.game.graph.keys["venemoth"], 0)
        self.assertEqual(self.game.graph.order[0].type_, A)
        self.assertEqual(self.game.graph.order[0].text, "venemoth")
        self.assertEqual(self.game.graph.data[0][0].yes, 0)
        self.assertEqual(self.game.graph.data[0][0].no, 0)

        self.game.graph.add(Q, "wings", [])
        self.assertEqual(self.game.graph.keys["wings"], 1)
        self.assertEqual(self.game.graph.order[1].type_, Q)
        self.assertEqual(self.game.graph.order[1].text, "wings")
        self.assertEqual(len(self.game.graph.data[0]), 1)
        self.assertEqual(len(self.game.graph.data[1]), 2)
        self.assertEqual(self.game.graph.data[1][0].yes, 0)
        self.assertEqual(self.game.graph.data[1][1].no, 0)

    def test_graph_update(self):
        self.game.graph.add(A, "venemoth", [])
        self.game.graph.add(Q, "wings", [])
        self.game.graph.update("venemoth", [Entry(1, Q, "y"), Entry(0, A, "y")])
        self.assertEqual(self.game.graph.data[1][0].yes, 1)
        self.assertEqual(self.game.graph.data[1][0].no, 0)

        self.game.graph.add(A, "rihorn", [])
        self.game.graph.update("rihorn", [Entry(1, Q, "n"), Entry(2, A, "y")])

    def test_init(self):
        


"""
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
        """

class TestLoadGame(unittest.TestCase):
    def setUp(self):
        self.game = Game("saved-2018-09-08.csv")

    def test_new_game(self):
        self.assertEqual(self.game.saved_file, "saved-2018-09-08.csv")

if __name__ == "__main__":
    unittest.main()
