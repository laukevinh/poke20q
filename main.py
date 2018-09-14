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

class Point:

    def __init__(self, yes, no):
        self.yes = yes
        self.no = no

    def ytoa(self):
        if (self.yes + self.no) == 0:
            return 0
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
        self.ytoa = []
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

    def update_filtered_q(self, entry):
        pass

    def update_filtered_a(self, entry):
        updated_filtered_a = []
        for i in self.filtered_a:
            (a, b) = (entry.index, i) if i < entry.index else (i, entry.index)
            if self.data[a][b].typical_resp() == entry.resp:
                updated_filtered_a.append(a)
        self.filtered_a = updated_filtered_a
        
    def calc_ytoa(self, qa_subset):
        self.ytoa = [Point(0,0) for i in range(self.size)]
        if qa_subset is None or len(qa_subset) == 0:
            qa_subset = range(self.size)
        for i in qa_subset:
            for j in range(i):
                (a, b) = (j, i) if i < j else (i, j)
                self.ytoa[j].yes += self.data[a][b].yes
                self.ytoa[j].no += self.data[a][b].no
        
        return [p.ytoa() for p in self.ytoa]

    def first_question(self):
        self.init_filtered_q()
        if len(self.filtered_q) == 0:
            print("No questions")
            return None

        self.init_filtered_a()
        temp = self.calc_ytoa(self.filtered_a)
        
        q_index = self.filtered_q[0]
        q_dfrom50 = abs(temp[q_index] - 0.5)

        min_list = [q_index]
        for i in self.filtered_q:
            if abs(temp[i] - 0.5) < q_dfrom50:
                q_dfrom50 = abs(temp[i] - 0.5)
                q_index = i
                del(min_list[:])
                min_list.append(q_index)
            elif abs(temp[i] - 0.5) == q_dfrom50:
                min_list.append(i)

        q_index = min_list[self.tie_breaker]
        self.tie_breaker = (self.tie_breaker + 1) % len(min_list)
        return self.order[q_index]

        

    def next_question(self, history):
        if len(history) == 0:
            return self.first_question()

        self.update_filtered_a(history[-1])

        temp = self.calc_ytoa(self.filtered_a)
        if len(self.filtered_a) == 1:
            return self.order[self.filtered_a[0]]
        for i in range(len(temp)):
            temp[i] = abs(temp[i] - 0.5)
        q_index = int(min(temp))

        return self.order[q_index]

    def get_index(self, key):
        return self.keys.get(key)

    def get_text(self, index):
        return self.order[index].text

    def update(self, history):
        #last = history.pop()
        last = history[-1]
        if last.type_ == A:
            i = last.index
            for entry in history:
                j = entry.index

                if i < j:
                    a, b = j, i
                else:
                    a, b = i, j

                if entry.resp == YES:
                    self.data[a][b].yes += 1
                else:
                    self.data[a][b].no += 1
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

    def save(self):
        if self.saved_file is None:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            self.saved_file = "saved-{}.csv".format(timestamp)
        print("Saving file to {}".format(self.saved_file))

    def start(self):
        print("Starting game {}".format(self.saved_file))
        add_more = NO
        while (self.graph.size < 2 or add_more):
            self.add_answer()
            self.add_question()
            add_more = get_ans("Add another question and answer? (y/n) ")
        self.ask_question()
        while (len(self.graph.filtered_a) > 0):
            self.ask_question()
        self.update_graph(self.history)
        print(self.graph.data, self.graph.order)
        self.save()

    def stop(self):
        self.play = False

    def prompt_replay(self):
        ans = input("Replay? (y/n) ")
        while (ans not in ["yes", "no", "y", "n"]):
            print("Input error: enter y/n")
            ans = input("Replay? (y/n) ")
        if (ans in ["no", "n"]):
            game.stop()

if __name__ == "__main__":
    game = Game()
    while (game.play is True):
        game.start()
        game.prompt_replay()
