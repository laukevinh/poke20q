from datetime import datetime

Q = 0
A = 1
C = 2
NO = 0
YES = 1
MAX_TEXT_LEN = 10 # max text length in repr
TYPICAL_RESP_THRESHOLD = 0.5
ANS_CONFIDENCE_THRESHOLD = 0.5
MAX_DIFF_VAL = 1
CONF_LVL_READY = 0
CONF_LVL_SEARCHING = 1
CONF_LVL_GUESS = -1
CONF_LVL_STOP = -2
CONF_LVL_TRY_MAYBE = -3
CONF_LVL_WIN = -4

def convert_yes_no(resp):
    resp = str.lower(resp)
    if resp in ["y", "yes"]:
        return YES
    elif resp in ["n", "no"]:
        return NO
    else:
        raise ValueError

def get_ans(prompt):
    responded = False
    while (not responded):
        try:
            resp = convert_yes_no(input("{}? ".format(prompt)))
        except ValueError:
            print("Please enter yes or no")
        else:
            return resp

class Point:

    def __init__(self, yes, no):
        self.yes = yes
        self.no = no
        self.total = yes + no

    def inc(self, field, amt):
        if (field == YES):
            self.yes += amt
            self.total += amt
        elif (field == NO):
            self.no += amt
            self.total += amt
        else:
            raise IndexError

    def ytoa(self):
        if (self.total == 0):
            return None
        return self.yes / self.total

    def typical_resp(self):
        ytoa = self.ytoa()
        if (ytoa is None):
            return None
        elif (ytoa >= TYPICAL_RESP_THRESHOLD):
            return YES
        return NO

    def __repr__(self):
        return "<Point({}:{})>".format(self.yes, self.no)

class Node:

    def __init__(self, type_, text):
        self.type_ = type_
        self.text = text

    def __repr__(self):
        return "<Node({}, {})>".format(
            self.type_, self.text[:MAX_TEXT_LEN])

class Entry:

    def __init__(self, index, type_, resp):
        self.index = index
        self.type_ = type_
        self.resp = resp

    def __repr__(self):
        return "<Entry({}, {}, {})>".format(
            self.index, self.type_, self.resp)

class Graph:

    def __init__(self):
        self.index = dict()
        self.order = []
        self.data = []
        self.size = 0
        self.tie_breaker = 0
        
    def get_index(self, text_key):
        if text_key == CONF_LVL_GUESS:
            return CONF_LVL_GUESS
        elif text_key == CONF_LVL_STOP:
            return CONF_LVL_STOP
        elif text_key == CONF_LVL_TRY_MAYBE:
            return CONF_LVL_TRY_MAYBE
        elif text_key == CONF_LVL_WIN:
            return CONF_LVL_WIN
        return self.index.get(text_key)

    def get_node(self, index):
        return self.order[index]

    def get_text(self, index):
        return self.get_node(index).text

    def get_point(self, ques_index, ans_index):
        (i, j) = ques_index, ans_index
        (i, j) = (j, i) if j > i else (i, j)
        return self.data[i][j]

    def add(self, type_, text):
        if self.get_index(text) is None:
            self.size += 1
            self.order.append(Node(type_, text))
            self.index[text] = self.size - 1
            row = [Point(0,0) for i in range(self.size)]
            self.data.append(row)
        else:
            print("{} already exists in the db".format(text))

    def add_answer(self, text):
        self.add(A, text)

    def add_question(self, text):
        self.add(Q, text)

    def update(self, history):
        last = history[-1]
        if last.type_ == A and last.resp == YES:
            for entry in history:
                if entry.type_ == Q:
                    point = self.get_point(entry.index, last.index)
                    point.inc(entry.resp, 1)
            point = self.get_point(last.index, last.index)
            point.inc(last.resp, 1)
        del(history[:])

    def get_all_potentials(self, type_):
        return [i for i in range(self.size) if self.get_node(i).type_ == type_]

    def get_all_potential_questions(self):
        return self.get_all_potentials(Q)

    def get_all_potential_answers(self):
        match = self.get_all_potentials(A)
        maybe = []
        return (match, maybe)

    def filter_out(self, index, array):
        while index in array: array.remove(index)
        return array
        
    def get_potential_questions(self, last_entry, potential_questions):
        if (last_entry.type_ == C):
            return potential_questions
        return self.filter_out(last_entry.index, potential_questions)

    def split_to_match_and_maybe(self, last_entry, array, match, maybe):
        for a_index in array:
            point = self.get_point(last_entry.index, a_index)
            if point.typical_resp() == last_entry.resp:
                match.append(a_index)
            elif point.typical_resp() is None:
                maybe.append(a_index)
        return (match, maybe)

    def get_potential_answers(self, last_entry, potential_answers):
        prev_match, prev_maybe = potential_answers[0], potential_answers[1]
        if (last_entry.type_ == C):
            while len(potential_answers[1]) > 0:
                potential_answers[0].append(potential_answers[1].pop())
            return potential_answers
        match, maybe = [], []
        match, maybe = self.split_to_match_and_maybe(last_entry, prev_match, match, maybe)
        match, maybe = self.split_to_match_and_maybe(last_entry, prev_maybe, match, maybe)
        return (match, maybe)

    def get_confidence_lvl(self, prev_len_potential_answers, potential_answers, history):
        len_match = len(potential_answers[0])
        len_maybe = len(potential_answers[1])
        last_entry = history[-1] if len(history) > 0 else None
        if (last_entry is not None
                and last_entry.type_ == A
                and last_entry.resp == YES):
            return CONF_LVL_WIN
        if (len_match == 1):
            return CONF_LVL_READY
        elif (len_match > 1):
            if (last_entry is not None 
                    and last_entry.type_ == C 
                    and last_entry.index == CONF_LVL_GUESS):
                if last_entry.resp == YES:
                    return CONF_LVL_READY
                elif last_entry.resp == NO:
                    return CONF_LVL_STOP
            if (prev_len_potential_answers == len_match):
                return CONF_LVL_GUESS
            return CONF_LVL_SEARCHING
        elif (len_maybe > 0):
            return CONF_LVL_TRY_MAYBE
        else:
            return CONF_LVL_STOP

    def diff_from_halving_answers(self, potential_answers, potential_questions):
        match = potential_answers[0]
        len_match = len(match)
        len_potential_questions = len(potential_questions)
        result = []
        for i in range(len_potential_questions):
            q_index = potential_questions[i]
            subtotal_point = Point(0,0)
            for j in range(len_match):
                a_index = match[j]
                typical_resp = self.get_point(q_index, a_index).typical_resp()
                if typical_resp is not None:
                    subtotal_point.inc(typical_resp, 1)
            try:
                value = abs(subtotal_point.ytoa() - TYPICAL_RESP_THRESHOLD)
            except TypeError:
                value = MAX_DIFF_VAL
            result.append((value, q_index))
        return result

    def get_next_question(self, history, potential_answers, potential_questions):
        # if no history, get all potential questions and answers
        # else apply filter based on last entry in history
        # last entry in history must be a question
        # return value of get_next_question is a Node(type_, text)
        if len(history) == 0:
            potential_answers = self.get_all_potential_answers()
            potential_questions = self.get_all_potential_questions()
            prev_len_potential_answers = len(potential_answers[0]) + 1
        else:
            last_entry = history[-1]
            prev_len_potential_answers = len(potential_answers[0])
            potential_answers = self.get_potential_answers(last_entry, potential_answers)
            potential_questions = self.get_potential_questions(last_entry, potential_questions)

        confidence_lvl = self.get_confidence_lvl(prev_len_potential_answers, potential_answers, history)

        if confidence_lvl == CONF_LVL_READY:
            node = self.get_node(potential_answers[0].pop())
        elif confidence_lvl == CONF_LVL_STOP:
            node = Node(C, CONF_LVL_STOP)
        elif confidence_lvl == CONF_LVL_WIN:
            node = Node(C, CONF_LVL_WIN)
        elif confidence_lvl == CONF_LVL_GUESS:
            node = Node(C, CONF_LVL_GUESS)
        elif confidence_lvl == CONF_LVL_TRY_MAYBE:
            node = Node(C, CONF_LVL_TRY_MAYBE)
        elif confidence_lvl == CONF_LVL_SEARCHING:
            q_index = min(self.diff_from_halving_answers(potential_answers, potential_questions))[1]
            node = self.get_node(q_index)

        return (node, potential_answers, potential_questions)

    def round_robin(self, array):
        self.tie_breaker = (self.tie_breaker + 1) % len(array)
        return array[self.tie_breaker]

    def get_best_ans(self):
        max_index = self.filtered_a[0]
        max_yes_count = 0
        max_list = [max_index]
        for a_index in self.filtered_a:
            point = self.get_point(a_index, a_index)
            if max_yes_count < point.yes:
                max_index = a_index
                max_yes_count = point.yes
                del(max_list[:])
                max_list.append(a_index)
            elif max_yes_count == point.yes:
                max_list.append(a_index)
        return self.get_node(self.round_robin(max_list))

class Game:

    def __init__(self, saved_file=None):
        self.saved_file = saved_file
        self.graph = Graph()
        self.history = []
        self.play = True
        self.potential_answers = []
        self.potential_questions = []

    def track_resp(self, index, type_, resp):
        self.history.append(Entry(index, type_, resp))

    def add_optional_question(self):
        question = input("Add a keyword to describe the pokemon (optional): ")
        if question != "":
            self.graph.add(Q, question)
            self.track_resp(self.graph.get_index(question), Q, YES)

    def add_question(self):
        question = input("Add a keyword to describe the pokemon: ")
        self.graph.add(Q, question)
        self.track_resp(self.graph.get_index(question), Q, YES)

    def add_answer(self):
        answer = input("Enter the name of the pokemon: ")
        self.graph.add(A, answer)
        self.track_resp(self.graph.get_index(answer), A, YES)

    def update_graph(self, history):
        self.graph.update(history)

    def swap_last_two_entries(self):
        self.history[-1], self.history[-2] = self.history[-2], self.history[-1]

    def ask_answer(self):
        if len(self.history) > 0:
            self.add_answer()
            self.add_optional_question()
        else:
            self.add_answer()
            self.add_question()
        if self.history[-1].type_ == Q:
            self.swap_last_two_entries()

    def ask_question(self):
        result = self.graph.get_next_question(
            self.history, 
            self.potential_answers, 
            self.potential_questions
            )
        (node, self.potential_answers, self.potential_questions) = result
        if node.type_ == C:
            if node.text == CONF_LVL_STOP:
                print("Darn, we didn't get it")
                self.ask_answer()
                self.update_graph(self.history)
                return NO
            elif node.text == CONF_LVL_WIN:
                print("We got it! Play again?")
                self.update_graph(self.history)
                return NO
            elif node.text == CONF_LVL_GUESS:
                resp = get_ans("Tricky...want me to guess?")
                self.track_resp(CONF_LVL_GUESS, C, resp)
                return resp
            elif node.text == CONF_LVL_TRY_MAYBE:
                resp = get_ans("Tricky...try the maybes?")
                self.track_resp(CONF_LVL_TRY_MAYBE, C, resp)
                return resp
            else:
                print("Error: Undefined Control flag {}".format(node.index))
                raise 
        else:
            resp = get_ans(node.text)
            self.track_resp(self.graph.get_index(node.text), node.type_, resp)
            return YES

    def save(self):
        if self.saved_file is None:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            self.saved_file = "saved-{}.csv".format(timestamp)
        print("Saving file to {}".format(self.saved_file))

    def new_game(self):
        print("New game")
        add_more = YES
        while (add_more):
            self.ask_answer()
            self.update_graph(self.history)
            add_more = get_ans("Add another question and answer (y/n)?")
        
    def resume_game(self):
        print("Loading game {}".format(self.saved_file))

    def start(self):
        if (self.saved_file is None):
            self.new_game()
        else:
            self.resume_game()

        while (self.ask_question() == YES):
            pass

        del(self.history[:])
        self.save()

    def stop(self):
        self.play = False

    def reset(self):
        pass

    def prompt_replay(self):
        if get_ans("Replay (y/n)") == NO: 
            game.stop()
        else:
            game.reset()

if __name__ == "__main__":
    game = Game()
    while (game.play is True):
        game.start()
        game.prompt_replay()
