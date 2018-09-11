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

    def typical_resp(self):
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
        
    def next_question(self, count):
        return self.order[count]

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

"""
        for entry in history:
            i = self.keys[entry[ENTRY_TEXT_IND]]
            if entry[ENTRY_YN_IND] in ["yes", "y"]:
                data = self.yes
            elif entry[ENTRY_YN_IND] in ["no", "n"]:
                data = self.no
            if data[i] is None:
                data[i] = Node(
                    entry[ENTRY_TYPE_IND], 
                    entry[ENTRY_TEXT_IND],
                    1)
            data[i].weight += 1

    def weight(self, v1, v2):
        return self.yes[v1][v2].weight
"""

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
        count = len(self.history)
        question = self.graph.next_question(count)
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
