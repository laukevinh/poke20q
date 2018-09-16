import unittest
from main import Q, A, YES, NO
from main import Point, Node, Entry, Graph, Game

class TestNewGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_new_game(self):
        self.assertEqual(self.game.saved_file, None)

    def test_graph_get(self):
        self.game.graph.add(A, "venemoth")
        self.assertEqual(self.game.graph.index["venemoth"], 0)
        self.assertEqual(self.game.graph.order[0].type_, A)
        self.assertEqual(self.game.graph.order[0].text, "venemoth")
        self.assertEqual(self.game.graph.data[0][0].yes, 0)
        self.assertEqual(self.game.graph.data[0][0].no, 0)

        self.game.graph.add(Q, "wings")
        self.assertEqual(self.game.graph.index["wings"], 1)
        self.assertEqual(self.game.graph.order[1].type_, Q)
        self.assertEqual(self.game.graph.order[1].text, "wings")
        self.assertEqual(len(self.game.graph.data[0]), 1)
        self.assertEqual(len(self.game.graph.data[1]), 2)
        self.assertEqual(self.game.graph.data[1][0].yes, 0)
        self.assertEqual(self.game.graph.data[1][1].no, 0)

    """
    "venemoth"  [[ [1,0] ],
    "wings"      [ [1,0], [0,0] ],
    "rihorn"     [ [0,0], [0,1], [1,0] ]
                ]
    """
    def test_graph_update(self):
        self.game.graph.add(A, "venemoth")
        self.game.graph.add(Q, "wings")
        self.game.graph.update([Entry(1, Q, YES), Entry(0, A, YES)])
        self.game.graph.add(A, "rihorn")
        self.game.graph.update([Entry(1, Q, NO), Entry(2, A, YES)])
        
        self.assertEqual(self.game.graph.data[0][0].yes, 1)
        self.assertEqual(self.game.graph.data[0][0].no, 0)
        self.assertEqual(self.game.graph.data[1][0].yes, 1)
        self.assertEqual(self.game.graph.data[1][0].no, 0)
        self.assertEqual(self.game.graph.data[1][1].yes, 0)
        self.assertEqual(self.game.graph.data[1][1].no, 0)
        self.assertEqual(self.game.graph.data[2][0].yes, 0)
        self.assertEqual(self.game.graph.data[2][0].no, 0)
        self.assertEqual(self.game.graph.data[2][1].yes, 0)
        self.assertEqual(self.game.graph.data[2][1].no, 1)
        self.assertEqual(self.game.graph.data[2][2].yes, 1)
        self.assertEqual(self.game.graph.data[2][2].no, 0)

    """
    "starter"   [[ [0,0] ],
    "bipedal"    [ [0,0], [0,0] ],
    "wings"      [ [0,0], [0,0], [0,0] ]
    "venemoth"   [ [0,1], [0,1], [1,0], [0,0] ]
    "rihorn"     [ [0,1], [0,1], [0,1], [0,0], [0,0] ]
    "charizard"  [ [1,0], [1,0], [1,0], [0,0], [0,0], [0,0] ]
    "dragonite"  [ [0,1], [1,0], [1,0], [0,0], [0,0], [0,0], [0,0] ]
                ]
    """
    def test_graph_update_2(self):
        self.game.graph.add(Q, "bipedal")
        self.game.graph.add(Q, "wings")
        self.game.graph.add(A, "venemoth")
        self.game.graph.add(A, "rihorn")
        self.game.graph.add(A, "charizard")
        self.game.graph.add(A, "dragonite")
        self.game.graph.add(Q, "starter")

        self.game.graph.update([
            Entry(self.game.graph.get_index("starter"), Q, NO), 
            Entry(self.game.graph.get_index("bipedal"), Q, NO), 
            Entry(self.game.graph.get_index("wings"), Q, YES), 
            Entry(self.game.graph.get_index("venemoth"), A, YES)])
        
        i = self.game.graph.get_index("starter")
        j = self.game.graph.get_index("venemoth")
        self.assertEqual(self.game.graph.get_point(i, j).yes, 0)
        self.assertEqual(self.game.graph.get_point(i, j).no, 1)
        
        i = self.game.graph.get_index("wings")
        j = self.game.graph.get_index("venemoth")
        self.assertEqual(self.game.graph.get_point(i, j).yes, 1)
        self.assertEqual(self.game.graph.get_point(i, j).no, 0)

    """
    "starter"   [[ [0,0] ],
    "bipedal"    [ [0,0], [0,0] ],
    "wings"      [ [0,0], [0,0], [0,0] ]
    "venemoth"   [ [0,1], [0,1], [1,0], [0,0] ]
    "rihorn"     [ [0,1], [0,1], [0,1], [0,0], [0,0] ]
    "charizard"  [ [1,0], [1,0], [1,0], [0,0], [0,0], [0,0] ]
    "dragonite"  [ [0,1], [1,0], [1,0], [0,0], [0,0], [0,0], [0,0] ]
                ]
    """
    def test_calc_ytoa(self):
        self.game.graph.add(Q, "bipedal")
        self.game.graph.add(Q, "wings")
        self.game.graph.add(A, "venemoth")
        self.game.graph.add(A, "rihorn")
        self.game.graph.add(A, "charizard")
        self.game.graph.add(A, "dragonite")
        self.game.graph.add(Q, "starter")

        self.game.graph.update([
            Entry(self.game.graph.get_index("starter"), Q, NO), 
            Entry(self.game.graph.get_index("bipedal"), Q, NO), 
            Entry(self.game.graph.get_index("wings"), Q, YES), 
            Entry(self.game.graph.get_index("venemoth"), A, YES)])
        self.game.graph.init_filtered_q()
        self.game.graph.init_filtered_a()
        self.assertEqual(
            self.game.graph.calc_ytoa(self.game.graph.filtered_a, self.game.graph.filtered_q), 
            [0.0, 1.0, None, None, None, None, 0.0])
        self.game.graph.update([
            Entry(self.game.graph.get_index("starter"), Q, NO), 
            Entry(self.game.graph.get_index("bipedal"), Q, NO),
            Entry(self.game.graph.get_index("wings"), Q, NO),
            Entry(self.game.graph.get_index("rihorn"), A, YES)])
        self.assertEqual(
            self.game.graph.calc_ytoa(self.game.graph.filtered_a, self.game.graph.filtered_q), 
            [0.0, 0.5, None, None, None, None, 0.0])
        self.game.graph.update([
            Entry(self.game.graph.get_index("starter"), Q, YES),
            Entry(self.game.graph.get_index("bipedal"), Q, YES),
            Entry(self.game.graph.get_index("wings"), Q, YES),
            Entry(self.game.graph.get_index("charizard"), A, YES)])
        self.game.graph.update([
            Entry(self.game.graph.get_index("starter"), Q, NO), 
            Entry(self.game.graph.get_index("bipedal"), Q, YES),
            Entry(self.game.graph.get_index("wings"), Q, YES),
            Entry(self.game.graph.get_index("dragonite"), A, YES)])
        self.assertEqual(
            self.game.graph.calc_ytoa(self.game.graph.filtered_a, self.game.graph.filtered_q), 
            [0.5, 0.75, None, None, None, None, 0.25])

        self.assertEqual(
            self.game.graph.calc_ytoa([4, 5], self.game.graph.filtered_q), 
            [1.0, 1.0, None, None, None, None, 0.5])

    """
    "starter"   [[ [0,0] ],
    "bipedal"    [ [0,0], [0,0] ],
    "wings"      [ [0,0], [0,0], [0,0] ]
    "venemoth"   [ [0,1], [0,1], [1,0], [0,0] ]
    "rihorn"     [ [0,1], [0,1], [0,1], [0,0], [0,0] ]
    "charizard"  [ [1,0], [1,0], [1,0], [0,0], [0,0], [0,0] ]
    "dragonite"  [ [0,1], [1,0], [1,0], [0,0], [0,0], [0,0], [0,0] ]
                ]
    """
    def test_all_ans_same(self):
        self.game.graph.add(Q, "bipedal")
        self.game.graph.add(A, "dragonite")
        self.game.graph.add(Q, "wings")
        self.game.graph.add(A, "charizard")
        self.game.graph.add(Q, "horns")
        self.game.graph.add(A, "rihorn")

        self.game.graph.update([
            Entry(self.game.graph.get_index("bipedal"), Q, YES), 
            Entry(self.game.graph.get_index("wings"), Q, YES), 
            Entry(self.game.graph.get_index("horns"), Q, YES), 
            Entry(self.game.graph.get_index("charizard"), A, YES)])
        self.game.graph.update([
            Entry(self.game.graph.get_index("bipedal"), Q, YES), 
            Entry(self.game.graph.get_index("wings"), Q, YES), 
            Entry(self.game.graph.get_index("horns"), Q, YES), 
            Entry(self.game.graph.get_index("dragonite"), A, YES)])
        self.game.graph.init_filtered_q()
        self.game.graph.init_filtered_a()
        self.assertEqual(self.game.graph.check_all_ans_same(), True)


    """
    "starter"   [[ [0,0] ],
    "bipedal"    [ [0,0], [0,0] ],
    "wings"      [ [0,0], [0,0], [0,0] ]
    "venemoth"   [ [0,1], [0,1], [1,0], [0,0] ]
    "rihorn"     [ [0,1], [0,1], [0,1], [0,0], [0,0] ]
    "charizard"  [ [1,0], [1,0], [1,0], [0,0], [0,0], [0,0] ]
    "dragonite"  [ [0,1], [1,0], [1,0], [0,0], [0,0], [0,0], [0,0] ]
                ]
    """
    def test_filter_update(self):
        self.game.graph.add(Q, "bipedal")
        self.game.graph.add(Q, "wings")
        self.game.graph.add(A, "venemoth")
        self.game.graph.add(A, "rihorn")
        self.game.graph.add(A, "charizard")
        self.game.graph.add(A, "dragonite")
        self.game.graph.add(Q, "starter")
        self.assertEqual(self.game.graph.check_all_ans_same(), True)

        self.game.graph.update([
            Entry(self.game.graph.get_index("starter"), Q, NO), 
            Entry(self.game.graph.get_index("bipedal"), Q, NO), 
            Entry(self.game.graph.get_index("wings"), Q, YES), 
            Entry(self.game.graph.get_index("venemoth"), A, YES)])

        self.game.graph.update([
            Entry(self.game.graph.get_index("starter"), Q, NO), 
            Entry(self.game.graph.get_index("bipedal"), Q, NO),
            Entry(self.game.graph.get_index("wings"), Q, NO),
            Entry(self.game.graph.get_index("rihorn"), A, YES)])
        self.game.graph.update([
            Entry(self.game.graph.get_index("starter"), Q, YES),
            Entry(self.game.graph.get_index("bipedal"), Q, YES),
            Entry(self.game.graph.get_index("wings"), Q, YES),
            Entry(self.game.graph.get_index("charizard"), A, YES)])
        self.game.graph.update([
            Entry(self.game.graph.get_index("starter"), Q, NO), 
            Entry(self.game.graph.get_index("bipedal"), Q, YES),
            Entry(self.game.graph.get_index("wings"), Q, YES),
            Entry(self.game.graph.get_index("dragonite"), A, YES)])

        self.game.graph.init_filtered_q()
        self.game.graph.init_filtered_a()
        self.assertEqual(self.game.graph.check_all_ans_same(), False)
        
        self.assertEqual(
            self.game.graph.calc_ytoa(self.game.graph.filtered_a, self.game.graph.filtered_q), 
            [0.5, 0.75, None, None, None, None, 0.25])

        self.assertEqual(self.game.graph.next_question(self.game.history).text, "bipedal")
        self.game.track_resp(self.game.graph.get_index("bipedal"), Q, YES)

        self.game.graph.update_filtered_a(self.game.history[-1])
        self.game.graph.update_filtered_q(self.game.history[-1].index)
        self.assertEqual(self.game.graph.filtered_a, [4, 5])
        self.assertEqual(self.game.graph.filtered_q, [1, 6])
        
        self.assertEqual(
            self.game.graph.calc_ytoa(self.game.graph.filtered_a, self.game.graph.filtered_q), 
            [None, 1.0, None, None, None, None, 0.5])
        """

        self.assertEqual(self.game.graph.next_question(self.game.history), "starter")
        self.assertEqual(self.game.graph.filtered_a, [4, 5])
        self.assertEqual(self.game.graph.filtered_q, [1, 6])
        self.game.track_resp(self.game.graph.get_index("starter"), Q, YES)

        #self.game.graph.update_filtered_a(self.game.history[-1])
        self.assertEqual(self.game.graph.filtered_a, [4])
        """

    def test_next_question(self):
        self.game.graph.add(Q, "starter")
        self.game.graph.add(Q, "bipedal")
        self.game.graph.add(Q, "wings")
        self.game.graph.add(A, "venemoth")
        self.game.graph.add(A, "rihorn")
        self.game.graph.add(A, "charizard")
        self.game.graph.add(A, "dragonite")

        self.game.graph.update([
            Entry(0, Q, NO), 
            Entry(1, Q, NO), 
            Entry(2, Q, YES), 
            Entry(3, A, YES)])
        self.game.graph.update([
            Entry(0, Q, NO), 
            Entry(1, Q, NO),
            Entry(2, Q, NO),
            Entry(4, A, YES)])
        self.game.graph.update([
            Entry(0, Q, YES),
            Entry(1, Q, YES),
            Entry(2, Q, YES),
            Entry(5, A, YES)])
        self.game.graph.update([
            Entry(0, Q, NO), 
            Entry(1, Q, YES),
            Entry(2, Q, YES),
            Entry(6, A, YES)])

        self.game.graph.init_filtered_q()
        self.game.graph.init_filtered_a()
        self.assertEqual(self.game.graph.filtered_q, [0, 1, 2])
        self.assertEqual(self.game.graph.filtered_a, [3, 4, 5, 6])

        """
        node = self.game.graph.next_question(self.game.history)
        self.assertEqual(node.text, "bipedal")

        self.game.history.append(Entry(1, Q, YES))
        node = self.game.graph.next_question(self.game.history)
        self.assertEqual(node.text, "starter")
        self.assertEqual(self.game.graph.filtered_a, [5, 6])

        self.game.history.append(Entry(0, Q, YES))
        
        self.assertEqual(
            self.game.graph.next_question(self.game.history).text,
            "charizard")
        """


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
