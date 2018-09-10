from datetime import datetime

Q = 0
A = 1
ENTRY_TEXT_IND = 0
ENTRY_TYPE_IND = 1
ENTRY_YN_IND = 2
    
class Node:

    def __init__(self, type_=Q, text="", weight=0):
        self.type_ = type_
        self.weight = weight
        self.text = text
        self.next = None

    def inc(self, n=1):
        if (self.weight + n >= 0):
            self.weight += n
        else:
            eprint("Cannot decrease weight below 0")

class Graph:

    def __init__(self):
        self.keys = dict()
        self.yes = []
        self.no = []
        self.size = 0
        
    def get(self, key):
        return self.keys.get(key)

    def add(self, type_, text, history):
        
        for i in range(self.size):
            self.yes[i].append(None)
            self.no[i].append(None)
        self.size += 1
        self.keys[text] = self.size - 1
        self.yes.append([None]*self.size)
        self.no.append([None]*self.size)

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

class Game:

    def __init__(self, saved_file=None):
        self.saved_file = saved_file
        self.graph = Graph()
        self.history = []
        self.play = True
        
    def add_question(self):
        resp = input("Please enter a question associated with the pokemon you are thinking of: ")
        node = self.graph.get(resp)
        if node is None:
            self.graph.add(Q, resp)
        else:
            eprint("This pokemon already exists")

    def ask_question(self):
        q = self.graph.get_question(self.history)
        ans = input(q)


    def add_answer(self):
        ans = input("Enter the name of the pokemon you are thinking of: ");
        node = self.graph.get(resp)
        if node is None:
            self.graph.add(A, resp)
        else:
            eprint("This pokemon already exists")

    def save(self):
        if self.saved_file is None:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            self.saved_file = "saved-{}.csv".format(timestamp)
        print("Saving file to {}".format(self.saved_file))

    def update_graph(self):
        print("Updating graph")

    def start(self):
        print("Starting game {}".format(self.saved_file))
        self.add_answer()
        self.add_question()
        self.update_graph()
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
