from datetime import datetime

Q = 0
A = 1
NO = 0
YES = 1
ENTRY_TEXT_IND = 0
ENTRY_TYPE_IND = 1
ENTRY_YN_IND = 2

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

def get_correct_i_j(i, j):
    return (j, i) if j > i else (i, j)

class Point:

    def __init__(self, yes, no):
        self.yes = yes
        self.no = no

    def ytoa(self):
        if (self.yes + self.no) == 0:
            return None
        return self.yes / (self.yes+self.no)

    def typical_resp(self):
        if (self.yes + self.no) == 0:
            return None
        if (self.yes / (self.yes+self.no)) >= 0.5:
            return 1
        return 0

    def __repr__(self):
        return "<Point({}, {})>".format(self.yes, self.no)

class Node:

    def __init__(self, type_=Q, text="", weight=0):
        self.type_ = type_
#        self.weight = weight
        self.text = text
#        self.next = None

    def __repr__(self):
        return "<Node({}, {})>".format(self.type_, self.text[:8])

class Entry:

    def __init__(self, index, type_, resp):
        self.index = index
        self.type_ = type_
        self.resp = resp

    def __repr__(self):
        return "<Entry({}, {}, {})".format(
            self.n, self.type_, self.resp
        )

class Graph:

    def __init__(self):
        self.keys = dict()
        self.order = []
        self.data = []
        self.size = 0
        self.filtered_q = []
        self.filtered_a = []
        self.tie_breaker = 0
        
    def init_filtered_q(self):
        del(self.filtered_q[:])
        for i in range(self.size):
            if self.order[i].type_ == Q:
                self.filtered_q.append(i)

    def init_filtered_a(self):
        del(self.filtered_a[:])
        for i in range(self.size):
            if self.order[i].type_ == A:
                self.filtered_a.append(i)

    def update_filtered_q(self, index_to_del):
        for i in range(len(self.filtered_q)):
            if self.filtered_q[i] == index_to_del:
                del(self.filtered_q[i])
                break;

    def update_filtered_a(self, entry):
        temp = []
        for a_index in self.filtered_a:
            point = self.get_point(entry.index, a_index)
            if point.typical_resp() == entry.resp:
                temp.append(a_index)
        self.filtered_a = temp
        """
        for i in self.filtered_a:
            (a, b) = (entry.index, i) if i < entry.index else (i, entry.index)
            if self.data[a][b].typical_resp() == entry.resp:
                updated_filtered_a.append(a)
        self.filtered_a = updated_filtered_a
        """
        
    # calculates the yes to all answers ratio based on the remaining
    # answers. for example, given a list of filtered_answers [0, 1, 2]
    # and list of questions are [3, 4, 5], return a list
    # [None, None, None, %, %, %] where the % indicates that question's
    # ratio of yes to all answers

    def calc_ytoa(self, filtered_a, filtered_q):
        subtotal_ytoa = [Point(0,0) for i in range(self.size)]
        """
        if filtered_a is None or len(filtered_a) == 0:
            filtered_a = range(self.size)
        """
        for a_index in filtered_a:
            for q_index in filtered_q:
                """
                (a, b) = (j, i) if i < j else (i, j)
                subtotal_ytoa[j].yes += self.data[a][b].yes
                subtotal_ytoa[j].no += self.data[a][b].no
                """
                point = self.get_point(q_index, a_index)
                #index, oth = get_correct_i_j(q_index, a_index)
                index = q_index
                subtotal_ytoa[index].yes += point.yes
                subtotal_ytoa[index].no += point.no
        return [p.ytoa() for p in subtotal_ytoa]

    def calc_dfrom50(self, array):
        for i in range(len(array)):
            try:
                array[i] = abs(array[i] - 0.5)
            except TypeError:
                array[i] = None


    def first_question(self):
        self.init_filtered_q()
        if len(self.filtered_q) == 0:
            print("No questions")
            return None

        self.init_filtered_a()
        temp = self.calc_ytoa(self.filtered_a, self.filtered_q)
        
        q_index = self.filtered_q[0]
        q_dfrom50 = 0.5
        self.calc_dfrom50(temp)

        min_list = [q_index]
        for i in self.filtered_q:
            """
            if abs(temp[i] - 0.5) < q_dfrom50:
                q_dfrom50 = abs(temp[i] - 0.5)
                q_index = i
                del(min_list[:])
                min_list.append(q_index)
            elif abs(temp[i] - 0.5) == q_dfrom50:
                min_list.append(i)
            """
            if temp[i] is not None:
                if temp[i] < q_dfrom50:
                    q_dfrom50 = temp[i]
                    q_index = i
                    del(min_list[:])
                    min_list.append(q_index)
                elif temp[i] == q_dfrom50:
                    min_list.append(i)

        q_index = min_list[self.tie_breaker]
        self.tie_breaker = (self.tie_breaker + 1) % len(min_list)
        self.update_filtered_q(q_index)
# delete q_index and update filtered_q
        return self.get_text(q_index)

        

    def next_question(self, history):
        if len(history) == 0:
            return self.first_question()

        self.update_filtered_a(history[-1])
        all_ans_same = False
        if len(self.filtered_a) > 1 or all_ans_same:
            return self.get_text(self.filtered_a[0])

        temp = self.calc_ytoa(self.filtered_a, self.filtered_q)
        """
        for i in range(len(temp)):
            temp[i] = abs(temp[i] - 0.5)
        q_index = int(min(temp))

        return self.order[q_index]
        """
        q_index = self.filtered_q[0]
        q_dfrom50 = 0.5
        self.calc_dfrom50(temp)

        min_list = [q_index]
        for i in self.filtered_q:
            if temp[i] is not None:
                if temp[i] < q_dfrom50:
                    q_dfrom50 = temp[i]
                    q_index = i
                    del(min_list[:])
                    min_list.append(q_index)
                elif temp[i] == q_dfrom50:
                    min_list.append(i)

        q_index = min_list[self.tie_breaker]
        self.tie_breaker = (self.tie_breaker + 1) % len(min_list)
        #return self.order[q_index]
        return self.get_text(q_index)

    def get_index(self, key):
        return self.keys.get(key)

    def get_text(self, index):
        return self.order[index].text

    def get_point(self, ques_index, ans_index):
        #(i, j) = get_correct_i_j(ans_index, ques_index)
        (i, j) = get_correct_i_j(ques_index, ans_index)
        return self.data[i][j]

    def update(self, history):
        #last = history.pop()
        last = history[-1]
        if last.type_ == A:
            for entry in history:
                point = self.get_point(entry.index, last.index)
                if entry.resp == YES:
                    point.yes += 1
                else:
                    point.no += 1
        del(history[:])

    def add(self, type_, text):
        self.size += 1
        self.order.append(Node(type_, text))
        self.keys[text] = self.size - 1
        row = [Point(0,0) for i in range(self.size)]
        self.data.append(row)

class Game:

    def __init__(self, saved_file=None):
        self.saved_file = saved_file
        self.graph = Graph()
        self.history = []
        self.play = True

    def track_resp(self, index, type_, resp):
        self.history.append(Entry(index, type_, resp))

    def add_question(self):
        resp = input("Add a keyword to describe the pokemon: ")
        self.graph.add(Q, resp)

    def add_answer(self):
        resp = input("Enter the name of the pokemon you are thinking of: ");
        self.graph.add(A, resp)

    def ask_question(self):
        question = self.graph.next_question(self.history)
        if question is None:
            print("No more questions to ask")
        else:
            resp = get_ans(question.text)
            self.track_resp(self.graph.get_index(question.text), question.type_, resp)

    def update_graph(self, history):
        self.graph.update(history)

    def initialize_graph(self):
        answer = input("Enter the name of the pokemon you are thinking of: ");
        question = input("Add a keyword to describe the pokemon: ")
        self.graph.add(Q, question)
        self.graph.add(A, answer)
        self.track_resp(self.graph.get_index(question), Q, YES)
        self.track_resp(self.graph.get_index(answer), A, YES)
        self.update_graph(self.history)

    def save(self):
        if self.saved_file is None:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            self.saved_file = "saved-{}.csv".format(timestamp)
        print("Saving file to {}".format(self.saved_file))

    def new_game(self):
        print("New game")
        add_more = YES
        while (add_more):
            self.initialize_graph()
            add_more = get_ans("Add another question and answer (y/n)?")
        
    def resume_game(self):
        print("Loading game {}".format(self.saved_file))

    def check_win(self):
        if self.history[-1].resp == YES:
            print("We guessed it!")
            return True
        elif self.history[-1].resp == NO:
            print("Darn...we lost!")
            self.initialize_graph()
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

    def prompt_replay(self):
        if get_ans("Replay? (y/n) ") == NO: game.stop()

if __name__ == "__main__":
    game = Game()
    while (game.play is True):
        game.start()
        game.prompt_replay()
