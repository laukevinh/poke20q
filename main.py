from datetime import datetime

Q = 0
A = 1
C = 2
NO = 0
YES = 1
MAX_TEXT_LEN = 10 # max text length in repr
TYPICAL_RESP_THRESHOLD = 0.5
ANS_CONFIDENCE_THRESHOLD = 0.5
CONF_LVL_READY = 0
CONF_LVL_SEARCHING = 1
CONF_LVL_GUESS = -1
CONF_LVL_STOP = -2

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
        self.filtered_q = []
        self.filtered_a = []
        self.tie_breaker = 0
        self.keep_guessing = True
        
    def get_index(self, text_key):
        if text_key == CONF_LVL_GUESS:
            return CONF_LVL_GUESS
        elif text_key == CONF_LVL_STOP:
            return CONF_LVL_STOP
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
                point = self.get_point(entry.index, last.index)
                point.inc(entry.resp, 1)
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
            potential_answers = (potential_answers[1], potential_answers[0])
            return potential_answers
        match, maybe = [], []
        match, maybe = self.split_to_match_and_maybe(last_entry, prev_match, match, maybe)
        match, maybe = self.split_to_match_and_maybe(last_entry, prev_maybe, match, maybe)
        return (match, maybe)

    def get_confidence_lvl(self, prev_len_potential_answers, potential_answers):
        len_match = len(potential_answers[0])
        len_maybe = len(potential_answers[1])
        if (len_match == 1):
            return CONF_LVL_READY
        elif (len_match > 1):
            if (prev_len_potential_answers == len_match):
                return CONF_LVL_GUESS
            return CONF_LVL_SEARCHING
        elif (len_maybe > 0):
            return CONF_LVL_GUESS
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
                point = self.get_point(q_index, a_index)
                subtotal_point.inc(YES, point.yes)
                subtotal_point.inc(NO, point.no)
            try:
                value = abs(subtotal_point.ytoa() - TYPICAL_RESP_THRESHOLD)
            except TypeError:
                value = None
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

        confidence_lvl = self.get_confidence_lvl(prev_len_potential_answers, potential_answers)

        # if READY, ask answer but don't remove from potential answers
        # leave that for game to handle
        if confidence_lvl == CONF_LVL_READY:
            node = self.get_node(potential_answers[0].pop())
        elif confidence_lvl == CONF_LVL_STOP:
            node = Node(C, CONF_LVL_STOP)
        elif confidence_lvl == CONF_LVL_GUESS:
            node = Node(C, CONF_LVL_GUESS)
        elif confidence_lvl == CONF_LVL_SEARCHING:
            q_index = min(self.diff_from_halving_answers(potential_answers, potential_questions))[1]
            node = self.get_node(q_index)

        return (node, potential_answers, potential_questions)

    def reset_filter(self, type_):
        return [i for i in range(self.size) if self.get_node(i).type_ == type_]

    def init_filtered_q(self):
        self.filtered_q = self.reset_filter(Q)
        return self.filtered_q

    def init_filtered_a(self):
        self.filtered_a = self.reset_filter(A)
        return self.filtered_a

    def update_filtered_q(self, entry):
        self.filtered_q = self.filter_out(entry.index, self.filtered_q)
        return self.filtered_q

# TODO update so if match answers don't work, try for maybes
    def update_filtered_a(self, entry):
        match = []
        maybe = []
        for a_index in self.filtered_a:
            point = self.get_point(entry.index, a_index)
            if point.typical_resp() == entry.resp:
                match.append(a_index)
            elif point.typical_resp() is None:
                maybe.append(a_index)
        if len(match) == 0:
            self.filtered_a = maybe
        else:
            self.filtered_a = match
        
    # calculates the yes to all answers ratio based on the remaining
    # answers. for example, given a list of filtered_answers [0, 1, 2]
    # and list of questions [3, 4, 5], return a list
    # [None, None, None, %, %, %] where the % indicates that question's
    # ratio of yes to all answers

    def calc_ytoa(self, filtered_a, filtered_q):
        subtotal_ytoa = [Point(0,0) for i in range(self.size)]
        for a_index in filtered_a:
            for q_index in filtered_q:
                point = self.get_point(q_index, a_index)
                index = q_index
                subtotal_ytoa[index].inc(YES, point.yes)
                subtotal_ytoa[index].inc(NO, point.no)
        return [p.ytoa() for p in subtotal_ytoa]

    def calc_dfrom50(self, array):
        for i in range(len(array)):
            try:
                array[i] = abs(array[i] - TYPICAL_RESP_THRESHOLD)
            except TypeError:
                array[i] = None

    def check_all_ans_same(self):
        temp = []
        if len(self.filtered_a) == 0:
            print("empty filtered ans")
            return True
        for i in self.filtered_a:
            temp.append(self.calc_ytoa([i], self.filtered_q))
        for i in range(len(self.filtered_a)):
            for j in range(i+1, len(self.filtered_a)):
                if temp[i] != temp[j]:
                    print(self.get_text(self.filtered_a[i]), temp[i])
                    print(self.get_text(self.filtered_a[j]), temp[j])
                    return False
        return True

    def get_ans_confidence(self):
        return 1 if len(self.filtered_a) == 1 else 0

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

    def next_question(self, history):
        if len(history) == 0:
            self.init_filtered_q()
            self.init_filtered_a()
        else:
            self.update_filtered_a(history[-1])
            self.update_filtered_q(history[-1])

            if self.get_ans_confidence() > ANS_CONFIDENCE_THRESHOLD:
                return self.get_best_ans()

# consider checking whether all ans are same only if
# there is good reason e.g. number of filtered ans
# didn't decrease from previous iteration

            all_ans_same = self.check_all_ans_same()
            if all_ans_same is True:
# guess based on % of times selected as answer.
                if self.keep_guessing == True:
                    self.keep_guessing = False
                    print("guessing!")
                    #a_index = self.round_robin(self.filtered_a)
                    #return self.get_node(a_index)
                    return self.get_best_ans()
                if len(self.filtered_q) > 0:
# if incorrect, ask if want to continue.
# if no, add it to existing.
# if yes, find (0, 1, None). 
                    q_index = self.round_robin(self.filtered_q)
                    return self.get_node(q_index)
                else:
                    print("You got us! No more questions from next question")
                    return -1

        subtotal = self.calc_ytoa(self.filtered_a, self.filtered_q)
        self.calc_dfrom50(subtotal)
        q_index = self.filtered_q[0]
        q_dfrom50 = TYPICAL_RESP_THRESHOLD

        min_list = [q_index]
        for i in self.filtered_q:
            if subtotal[i] is not None:
                if subtotal[i] < q_dfrom50:
                    q_dfrom50 = subtotal[i]
                    q_index = i
                    del(min_list[:])
                    min_list.append(q_index)
                elif subtotal[i] == q_dfrom50:
                    min_list.append(i)

        q_index = self.round_robin(min_list)
        return self.get_node(q_index)

class Game:

    def __init__(self, saved_file=None):
        self.saved_file = saved_file
        self.graph = Graph()
        self.history = []
        self.play = True

    def track_resp(self, index, type_, resp):
        self.history.append(Entry(index, type_, resp))

    def add_optional_question(self):
        question = input("Add a keyword to describe the pokemon (optional): ")
        if question is not "":
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

    def remove_incorrect_ans(self):
        if self.history[-1].type_ == A:
            print("Popped", self.history.pop())

    def swap_last_two_entries(self):
        self.history[-1], self.history[-2] = self.history[-2], self.history[-1]

    def ask_answer(self):
        if len(self.history) > 0:
            self.remove_incorrect_ans()
            self.add_answer()
            self.add_optional_question()
        else:
            self.add_answer()
            self.add_question()
        if self.history[-1].type_ == Q:
            self.swap_last_two_entries()

    def ask_question(self):
        question = self.graph.next_question(self.history)
        if question == -1:
            self.ask_answer()
        else:
            resp = get_ans(question.text)
            self.track_resp(self.graph.get_index(question.text), question.type_, resp)

    def update_graph(self, history):
        self.graph.update(history)

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

    def check_win(self):
        if self.history[-1].resp == YES:
            print("We guessed it!")
            return True
        elif self.history[-1].resp == NO:
            print("Darn...we lost!")
            self.ask_answer()
            return True
        else:
            print("Error????", self.history)
            return False

    def start(self):
        if (self.saved_file is None):
            self.new_game()
        else:
            self.resume_game()

        finished = False
        while (not finished):
            self.ask_question()
            if self.history[-1].type_ == A:
                finished = self.check_win()

        self.update_graph(self.history)
        print(self.graph.data, self.graph.order)
        self.save()

    def stop(self):
        self.play = False

    def reset(self):
        self.graph.keep_guessing = True

    def prompt_replay(self):
        if get_ans("Replay? (y/n) ") == NO: 
            game.stop()
        else:
            game.reset()

if __name__ == "__main__":
    game = Game()
    while (game.play is True):
        game.start()
        game.prompt_replay()
