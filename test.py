import unittest
from main import Q, A, C, YES, NO
from main import CONF_LVL_READY, CONF_LVL_SEARCHING, CONF_LVL_TRY_MAYBE, CONF_LVL_GUESS, CONF_LVL_STOP

from main import Point, Node, Entry, Graph, Game

class TestGraph1(unittest.TestCase):
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
        q2 = self.g.get_index("q2")
        a0 = self.g.get_index("a0")
        a1 = self.g.get_index("a1")
        a2 = self.g.get_index("a2")
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

        # update history with control entries and incorrect answers
        history = [
            Entry(q0, Q, NO), 
            Entry(a1, A, NO),
            Entry(CONF_LVL_TRY_MAYBE, C, YES),
            Entry(q1, Q, NO),
            Entry(CONF_LVL_GUESS, C, YES),
            Entry(a2, A, YES)
            ]
        self.g.update(history)

        # test that Control entries and incorrect answers are skipped
        point = self.g.get_point(q0, a1)
        self.assertEqual((point.yes, point.no), (0,1))
        point = self.g.get_point(q1, a1)
        self.assertEqual((point.yes, point.no), (1,0))
        point = self.g.get_point(q2, a1)
        self.assertEqual((point.yes, point.no), (0,0))
        point = self.g.get_point(q0, a2)
        self.assertEqual((point.yes, point.no), (0,1))
        point = self.g.get_point(q1, a2)
        self.assertEqual((point.yes, point.no), (0,1))
        point = self.g.get_point(q2, a2)
        self.assertEqual((point.yes, point.no), (0,0))

    def test_get_all_potentials(self):
        self.assertEqual(self.g.get_all_potentials(A), [1, 3, 5])
        self.assertEqual(self.g.get_all_potentials(Q), [0, 2, 4])
        self.assertEqual(self.g.get_all_potential_answers(), ([1, 3, 5], []))
        self.assertEqual(self.g.get_all_potential_questions(), [0, 2, 4])

    def test_filter_out(self):
        self.assertEqual(self.g.filter_out(3, [0, 1, 2, 3, 4]), [0, 1, 2, 4])

class TestGraph2(unittest.TestCase):

    def setUp(self):
        self.g = Graph()
        for i in range(3):
            self.g.add_question("q{}".format(i))
            self.g.add_answer("a{}".format(i))
        # Set up a mock history and update
        self.q0 = self.g.get_index("q0")
        self.q1 = self.g.get_index("q1")
        self.q2 = self.g.get_index("q2")
        self.a0 = self.g.get_index("a0")
        self.a1 = self.g.get_index("a1")
        self.a2 = self.g.get_index("a2")
        history = [
            Entry(self.q0, Q, YES), 
            Entry(self.q1, Q, NO), 
            Entry(self.q2, Q, YES),
            Entry(self.a0, A, YES)
            ]
        self.g.update(history)
        history = [
            Entry(self.q1, Q, YES), 
            Entry(self.a1, A, YES)
            ]
        self.g.update(history)
        history = [
            Entry(self.q1, Q, NO), 
            Entry(self.q2, Q, NO),
            Entry(self.a2, A, YES)
            ]
        self.g.update(history)

    def test_get_potential_questions(self):
        # get all potential questions 
        potential_questions = self.g.get_all_potential_questions()

        # test update potential questions
        last_question = Entry(self.q0, Q, YES)
        self.assertEqual(
            self.g.get_potential_questions(last_question, potential_questions), 
            [self.q1, self.q2]
            )

        last_question = Entry(self.q2, Q, YES)
        self.assertEqual(
            self.g.get_potential_questions(last_question, potential_questions), 
            [self.q1]
            )
        
    def test_get_potential_answers(self):
        # get all potential answers 
        potential_answers = self.g.get_all_potential_answers()

        # test update potential answers after 1 question entry
        last_question = Entry(self.q0, Q, YES)
        self.assertEqual(
            self.g.get_potential_answers(last_question, potential_answers),
            ([self.a0], [self.a1, self.a2])
            )
        last_question = Entry(self.q0, Q, NO)
        self.assertEqual(
            self.g.get_potential_answers(last_question, potential_answers), 
            ([], [self.a1, self.a2])
            )
        last_question = Entry(self.q1, Q, NO)
        self.assertEqual(
            self.g.get_potential_answers(last_question, potential_answers),
            ([self.a0, self.a2], [])
            )

        # update potential answers with 1 entry
        prev_question = Entry(self.q0, Q, YES)
        potential_answers = self.g.get_potential_answers(prev_question, potential_answers)

        # test update potential answers after 2nd question entry
        last_question = Entry(self.q1, Q, YES)
        self.assertEqual(
            self.g.get_potential_answers(last_question, potential_answers),
            ([self.a1], [])
            )
        last_question = Entry(self.q1, Q, NO)
        self.assertEqual(
            self.g.get_potential_answers(last_question, potential_answers),
            ([self.a0, self.a2], [])
            )
        last_question = Entry(self.q2, Q, YES)
        self.assertEqual(
            self.g.get_potential_answers(last_question, potential_answers),
            ([self.a0], [self.a1])
            )
        last_question = Entry(self.q2, Q, NO)
        self.assertEqual(
            self.g.get_potential_answers(last_question, potential_answers),
            ([self.a2], [self.a1])
            )

    def test_answer_confidence(self):
        len_prev_potential_answers = 4
        len_prev_potential_questions = -1
        potential_answers = ([self.a1], [])
        potential_questions = [self.q0, self.q1]
        history = []
        self.assertEqual(
            self.g.get_confidence_lvl(
                len_prev_potential_answers, 
                potential_answers,
                len_prev_potential_questions,
                potential_questions,
                history,
                ),
            CONF_LVL_READY
            )

        len_prev_potential_answers = 4
        potential_answers = ([self.a1], [self.a0])
        self.assertEqual(
            self.g.get_confidence_lvl(
                len_prev_potential_answers, 
                potential_answers,
                len_prev_potential_questions,
                potential_questions,
                history
                ),
            CONF_LVL_READY
            )

        len_prev_potential_answers = 4
        potential_answers = ([self.a0, self.a1], [self.a0])
        self.assertEqual(
            self.g.get_confidence_lvl(
                len_prev_potential_answers, 
                potential_answers,
                len_prev_potential_questions,
                potential_questions,
                history
                ),
            CONF_LVL_SEARCHING
            )

        len_prev_potential_answers = 4
        potential_answers = ([self.a0, self.a1, self.a2], [])
        self.assertEqual(
            self.g.get_confidence_lvl(
                len_prev_potential_answers, 
                potential_answers,
                len_prev_potential_questions,
                potential_questions,
                history
                ),
            CONF_LVL_SEARCHING
            )

        len_prev_potential_answers = 3
        potential_answers = ([self.a0, self.a1, self.a2], [])
        self.assertEqual(
            self.g.get_confidence_lvl(
                len_prev_potential_answers, 
                potential_answers,
                len_prev_potential_questions,
                potential_questions,
                history
                ),
            CONF_LVL_GUESS
            )

        len_prev_potential_answers = 3
        potential_answers = ([], [self.a0])
        self.assertEqual(
            self.g.get_confidence_lvl(
                len_prev_potential_answers, 
                potential_answers,
                len_prev_potential_questions,
                potential_questions,
                history
                ),
            CONF_LVL_TRY_MAYBE
            )

        len_prev_potential_answers = 0
        potential_answers = ([], [self.a0, self.a1])
        self.assertEqual(
            self.g.get_confidence_lvl(
                len_prev_potential_answers, 
                potential_answers,
                len_prev_potential_questions,
                potential_questions,
                history
                ),
            CONF_LVL_TRY_MAYBE
            )
        
        len_prev_potential_answers = 0
        potential_answers = ([], [])
        self.assertEqual(
            self.g.get_confidence_lvl(
                len_prev_potential_answers, 
                potential_answers,
                len_prev_potential_questions,
                potential_questions,
                history
                ),
            CONF_LVL_STOP
            )

    def test_get_best_answer(self):
        pass

    def test_diff_from_halving_answers(self):
        potential_answers = self.g.get_all_potential_answers()
        potential_questions = self.g.get_all_potential_questions()
        result = self.g.diff_from_halving_answers(potential_answers, potential_questions)
        self.assertEqual(
            result, 
            [
                (0.5, self.q0),
                (abs(1/3-1/2), self.q1),
                (0, self.q2)
                ]
            )
        self.assertEqual(min(result)[1], self.q2)

        potential_answers = ([self.a1, self.a2], [])
        potential_questions = [self.q1, self.q2]
        result = self.g.diff_from_halving_answers(potential_answers, potential_questions)
        self.assertEqual(
            result,
            [
                (0, self.q1),
                (0.5, self.q2)
                ]
            )
        self.assertEqual(min(result)[1], self.q1)

    def test_get_next_question(self):
        # get all potential answers and questions
        history = []
        potential_answers = []
        potential_questions = []
        result = self.g.get_next_question(history, potential_answers, potential_questions)
        (node, potential_answers, potential_questions) = result
        q_index = self.g.get_index(node.text)
        self.assertEqual(q_index, self.q2)
        self.assertEqual(potential_answers, ([self.a0, self.a1, self.a2], []))
        self.assertEqual(potential_questions, [self.q0, self.q1, self.q2])

        history.append(Entry(q_index, Q, YES))
        result = self.g.get_next_question(history, potential_answers, potential_questions)
        (node, potential_answers, potential_questions) = result
        q_index = self.g.get_index(node.text)
        self.assertEqual(q_index, self.a0)
        self.assertEqual(potential_answers, ([], [self.a1]))
        self.assertEqual(potential_questions, [self.q0, self.q1])

        history.append(Entry(q_index, A, NO))
        result = self.g.get_next_question(history, potential_answers, potential_questions)
        (node, potential_answers, potential_questions) = result
        q_index = self.g.get_index(node.text)
        self.assertEqual(q_index, CONF_LVL_TRY_MAYBE)
        self.assertEqual(potential_answers, ([], [self.a1]))
        self.assertEqual(potential_questions, [self.q0, self.q1])

        history.append(Entry(q_index, C, YES))
        result = self.g.get_next_question(history, potential_answers, potential_questions)
        (node, potential_answers, potential_questions) = result
        q_index = self.g.get_index(node.text)
        self.assertEqual(q_index, self.a1)
        self.assertEqual(potential_answers, ([], []))
        self.assertEqual(potential_questions, [self.q0, self.q1])

        history.append(Entry(q_index, A, NO))
        result = self.g.get_next_question(history, potential_answers, potential_questions)
        (node, potential_answers, potential_questions) = result
        q_index = self.g.get_index(node.text)
        self.assertEqual(q_index, CONF_LVL_STOP)
        self.assertEqual(potential_answers, ([], []))
        self.assertEqual(potential_questions, [self.q0, self.q1])

    def test_get_next_question_2(self):
        # get all potential answers and questions
        history = [
            Entry(self.q1, Q, YES), 
            Entry(self.a1, A, YES)
            ]
        self.g.update(history)
        history = [
            Entry(self.q0, Q, YES), 
            Entry(self.q2, Q, YES),
            Entry(self.a2, A, YES)
            ]
        self.g.update(history)
        history = [
            Entry(self.q2, Q, YES),
            Entry(self.a2, A, YES)
            ]
        self.g.update(history)

        history = []
        potential_answers = []
        potential_questions = []
        result = self.g.get_next_question(history, potential_answers, potential_questions)
        (node, potential_answers, potential_questions) = result
        q_index = self.g.get_index(node.text)
        self.assertEqual(q_index, self.q1)
        self.assertEqual(potential_answers, ([self.a0, self.a1, self.a2], []))
        self.assertEqual(potential_questions, [self.q0, self.q1, self.q2])

        history.append(Entry(q_index, Q, NO))
        result = self.g.get_next_question(history, potential_answers, potential_questions)
        (node, potential_answers, potential_questions) = result
        q_index = self.g.get_index(node.text)
        self.assertEqual(q_index, self.q0)
        self.assertEqual(potential_answers, ([self.a0, self.a2], []))
        self.assertEqual(potential_questions, [self.q0, self.q2])

        history.append(Entry(q_index, Q, YES))
        result = self.g.get_next_question(history, potential_answers, potential_questions)
        (node, potential_answers, potential_questions) = result
        q_index = self.g.get_index(node.text)
        self.assertEqual(q_index, CONF_LVL_GUESS)
        self.assertEqual(potential_answers, ([self.a0, self.a2], []))
        self.assertEqual(potential_questions, [self.q2])

        history.append(Entry(q_index, C, YES))
        result = self.g.get_next_question(history, potential_answers, potential_questions)
        (node, potential_answers, potential_questions) = result
        q_index = self.g.get_index(node.text)
        self.assertEqual(q_index, self.a2)
        self.assertEqual(potential_answers, ([self.a0], []))
        self.assertEqual(potential_questions, [self.q2])

        history.append(Entry(q_index, A, NO))
        result = self.g.get_next_question(history, potential_answers, potential_questions)
        (node, potential_answers, potential_questions) = result
        q_index = self.g.get_index(node.text)
        self.assertEqual(q_index, CONF_LVL_TRY_MAYBE)
        self.assertEqual(potential_answers, ([], [self.a0]))
        self.assertEqual(potential_questions, [self.q2])

class TestNewGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_new_game(self):
        self.assertEqual(self.game.saved_file, None)

if __name__ == "__main__":
    unittest.main()
