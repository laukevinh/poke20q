from datetime import datetime

Q = 0
A = 1
ENTRY_TEXT_IND = 0
ENTRY_TYPE_IND = 1
ENTRY_YN_IND = 2
    
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
        return round(self.yes / (self.yes+self.no))

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
        self.filtered_q = None
        self.filtered_a = None
        
    def init_filtered_q(self):
        self.filtered_q = []
        for i in range(self.size):
            if self.order[i].type_ == Q:
                self.filtered_q.append(i)

    def init_filtered_a(self):
        self.filtered_a = []
        for i in range(self.size):
            if self.order[i].type_ == A:
                self.filtered_a.append(i)

    def update_filtered_q(self, entry):
        updated_filtered_q = []
        if entry.type_ == Q:
            for i in self.filtered_a:
                resp = 1 if entry.resp in ["y"] else 0
                if self.data[i][entry.index].typical_resp == resp:
                    updated_filtered_q.append(i)
        self.filtered_q = updated_filtered_q

    def update_filtered_a(self, entry):
        updated_filtered_a = []
        if entry.type_ == A:
            for i in self.filtered_q:
                if self.order[i].typical_resp in [entry.resp]:
                    updated_filtered_a.append(i)
        self.filtered_a = updated_filtered_a
        
    def calc_ytoa(self, filtered_q=None):
        self.ytoa = [Point(0,0) for i in range(self.size)]
        if filtered_q is None:
            filtered_q = range(self.size)
        for i in filtered_q:
            for j in range(i):
                (a, b) = (j, i) if i < j else (i, j)
                self.ytoa[j].yes += self.data[a][b].yes
                self.ytoa[j].no += self.data[a][b].no
        
        return [p.ytoa() for p in self.ytoa]

    def first_question(self):
        self.init_filtered_q()
        self.init_filtered_a()
        self.calc_ytoa(self.filtered_a)
        print(self.ytoa)
        if len(self.filtered_q) == 0:
            print("No questions")
            return None
        
        q_index = self.filtered_q[0]
        q_dfrom50 = abs(self.ytoa[q_index].ytoa() - 0.5)

        for i in self.filtered_q:
            value = self.ytoa[i].ytoa() - 0.5
            print(q_index, q_dfrom50)
            print(i, value)

            if abs(value) < q_dfrom50:
                q_dfrom50 = abs(value)
                q_index = i

        return self.order[q_index]

        

    def next_question(self, history):
        if len(history) == 0:
            return self.first_question()

        self.update_filtered_q(history[-1])
        for i in filtered_q:
            if self.order[i].type_ == Q:
                next_q_index = i
                break
        if next_q_index == len(filtered_q) - 1 and order[next_q_index].type_ == A:
            return None
        min_question = abs(self.ytoa[next_q_index].ytoa() - 0.5)

        for i in filtered_q:
            if self.order[i].type_ == Q:
                value = self.ytoa[i].ytoa() - 0.5
                min_question = min(abs(value), min_question)
                next_q_index = i

        return self.order[next_q_index]

    def get_index(self, key):
        return self.keys.get(key)

    def get_text(self, index):
        return self.order[index].text

    def update(self, key, history):
        i = self.get_index(key)
        for entry in history:
            j = entry.index

            if i < j:
                a, b = j, i
            else:
                a, b = i, j

            if entry.resp in ["y"]:
                self.data[a][b].yes += 1
            else:
                self.data[a][b].no += 1

    def add(self, type_, text, history):
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
        self.graph.add(Q, resp, self.history)

    def ask_question(self):
        question = self.graph.next_question(self.history, self.filtered_q)
        if question is None:
            print("No more questions to ask")
        else:
            resp = input("{}?".format(question.text))
            self.track_resp(count, Q, resp)

    def add_answer(self):
        resp = input("Enter the name of the pokemon you are thinking of: ");
        self.graph.add(A, resp, self.history)

    def update_graph(self, key, history):
        print("Updating graph")
        self.graph.update(key, history)

    def save(self):
        if self.saved_file is None:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            self.saved_file = "saved-{}.csv".format(timestamp)
        print("Saving file to {}".format(self.saved_file))

    def start(self):
        print("Starting game {}".format(self.saved_file))
        self.add_answer()
        self.add_question()
        self.ask_question()
        self.ask_question()
        self.update_graph(self.graph.get_text(self.history[-1].index), self.history)
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
