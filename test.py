import unittest
from main import Q, A, YES, NO
from main import Point, Node, Entry, Graph, Game

class TestGraph(unittest.TestCase):
    def setUp(self):
        self.g = Graph()
        for i in range(3):
            self.g.add_question("q{}".format(i))
            self.g.add_answer("a{}".format(i))
        
    def test_get_index(self):
        self.assertEqual(self.g.get_index("q0"), 0)

    def test_get_node(self):
        node = self.g.get_node(1)
        self.assertEqual(node.type_, A)
        self.assertEqual(node.text, "a0")

    def test_get_text(self):
        self.assertEqual(self.g.get_text(2), "q1")

    def test_get_point(self):
        i, j = 2, 3
        self.assertIs(self.g.get_point(i, j), self.g.data[j][i])
        i, j = 3, 2
        self.assertIs(self.g.get_point(i, j), self.g.data[i][j])

    def test_update(self):
        # Set up a mock history and update
        q0 = self.g.get_index("q0")
        q1 = self.g.get_index("q1")
        a1 = self.g.get_index("a1")
        history = [
            Entry(q0, Q, NO), 
            Entry(q1, Q, YES), 
            Entry(a1, A, YES)
            ]
        self.g.update(history)

        # test that definitive answers were recorded correctly
        p_q0_a1 = self.g.get_point(q0, a1)
        p_q1_a1 = self.g.get_point(q1, a1)
        self.assertEqual(p_q0_a1.typical_resp(), NO)
        self.assertEqual(p_q1_a1.typical_resp(), YES)

        # test that unlinked questions and answers remain N/A
        q2 = self.g.get_index("q2")
        p_q2_a1 = self.g.get_point(q2, a1)
        self.assertEqual(p_q2_a1.typical_resp(), None)

    def test_reset_filter(self):
        self.assertEqual(self.g.reset_filter(A), [1, 3, 5])
        self.assertEqual(self.g.reset_filter(Q), [0, 2, 4])

    def test_filter_out(self):
        self.assertEqual(self.g.filter_out(3, [0, 1, 2, 3, 4]), [0, 1, 2, 4])

    def test_update_filtered_q(self):
        index = self.g.get_index("q1")
        entry = Entry(index, Q, YES)
        #self.assertEqual(self.g.update_filtered_q(


class TestNewGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_new_game(self):
        self.assertEqual(self.game.saved_file, None)

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
""" 

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
"""

"""
        dragonite: [[1.0, None, 1.0, None, 1.0, None],
        charizard:  [1.0, None, 1.0, None, 1.0, None],
        rihorn:     [None, None, None, None, None, None]]
"""

"""
        self.assertEqual(self.game.graph.check_all_ans_same(), False)
"""


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
        self.game.graph.update_filtered_q(self.game.history[-1])
        self.assertEqual(self.game.graph.filtered_a, [4, 5])
        self.assertEqual(self.game.graph.filtered_q, [1, 6])
        
        self.assertEqual(
            self.game.graph.calc_ytoa(self.game.graph.filtered_a, self.game.graph.filtered_q), 
            [None, 1.0, None, None, None, None, 0.5])
""" 

"""
        self.assertEqual(self.game.graph.next_question(self.game.history), "starter")
        self.assertEqual(self.game.graph.filtered_a, [4, 5])
        self.assertEqual(self.game.graph.filtered_q, [1, 6])
        self.game.track_resp(self.game.graph.get_index("starter"), Q, YES)

        #self.game.graph.update_filtered_a(self.game.history[-1])
        self.assertEqual(self.game.graph.filtered_a, [4])
"""

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
