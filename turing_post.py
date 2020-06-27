LEFT = -1
RIGHT = 1


# class BracketMachine:
#     def __init__(self):
#         pass

#     def start_state(self):
#         return "q_)"

#     def acc_state(self):
#         return "q_a"

#     def rej_state(self):
#         return "q_r"

#     def symbols(self):
#         return ["$", "(", ")", "_", "e"]

#     def states(self):
#         return ["q_)", "q_a", "q_r", "q_b", "q_)"]

#     def trans_function(self, state, symbol):
#         if state == "q_)":
#             if symbol == "$":
#                 return (state, symbol, RIGHT)

#             if symbol == "(":
#                 return (state, symbol, RIGHT)

#             if symbol == "e":
#                 return (state, symbol, RIGHT)
        
#             if symbol == ")":
#                 return ("q_(", "e", LEFT)

#             if symbol == "_":
#                 return ("q_v", "_", LEFT)


#         if state == "q_(":
#             if symbol == ")":
#                 return ("q_r", "_", LEFT)

#             if symbol == "$":
#                 return ("q_r", "_", LEFT)
        
#             if symbol == "e":
#                 return (state, symbol, LEFT)
        
#             if symbol == "(":
#                 return ("q_b", "e", LEFT)

#             if symbol == "_":
#                 raise Exception(f"State {state}, symbol {symbol} shouldn't happen!")

#         if state == "q_b":
#             if symbol == "_":
#                 raise Exception(f"State {state}, symbol {symbol} shouldn't happen!")

#             if symbol == "$":
#                 return ("q_)", symbol, RIGHT)
#             else:
#                 return (state, symbol, LEFT)

#         if state == "q_v":
#             if symbol == "$":
#                 return ("q_a", symbol, RIGHT)

#             if symbol == "(":
#                 return ("q_r", symbol, RIGHT)

#             if symbol == "e":
#                 return (state, symbol, LEFT)
        
#         raise Exception(f"State {state}, symbol {symbol} shouldn't happen!")


class BracketMachine:
    def __init__(self):
        pass

    def start_state(self):
        return "q_)"

    def acc_state(self):
        return "q_a"

    def rej_state(self):
        return "q_r"

    def symbols(self):
        return ["$", "(", ")", "_", "e"]

    def states(self):
        return ["q_)", "q_a", "q_r", "q_b", "q_)"]

    def trans_function(self):
        return {
            ("q_)", "$"): ("q_)", "$", RIGHT),
            ("q_)", "("): ("q_)", "(", RIGHT),
            ("q_)", "e"): ("q_)", "e", RIGHT),
            ("q_)", ")"): ("q_(", "e", LEFT),
            ("q_)", "_"): ("q_v", "_", LEFT),

            ("q_(", ")"): ("q_r", "_", LEFT),
            ("q_(", "$"): ("q_r", "_", LEFT),
            ("q_(", "e"): ("q_(", "e", LEFT),
            ("q_(", "("): ("q_b", "e", LEFT),
            ("q_(", "_"): ("_", "q_rej", LEFT),

            ("q_b", "_"): ("q_r", "_", LEFT),
            ("q_b", "$"): ("q_)", "$", RIGHT),
            ("q_b", ")"): ("q_b", ")", LEFT),
            ("q_b", "e"): ("q_b", "e", LEFT),
            ("q_b", "("): ("q_b", "(", LEFT),

            ("q_v", "$"): ("q_a", "$", RIGHT),
            ("q_v", "("): ("q_r", "(", RIGHT),
            ("q_v", "e"): ("q_v", "e", LEFT),
            ("q_v", ")"): ("q_r", "e", LEFT),
            ("q_v", "_"): ("q_r", "e", LEFT),
        }

def print_state(tape, state, index):
    print(f"STATE: state={state}, index={index}")

    for i in range(index):
        print("    ", end="")

    print("", state)

    for t in tape:
        print("-----", end="")
    print()

    print("| ", end="")
    for t in tape:
        print(t, "| ", end="")
    print()
    
    for t in tape:
        print("-----", end="")
    print()
    

def run_machine(tape, machine, ps=False):
    state = machine.start_state()
    trans = machine.trans_function()
    i = 0
    while state not in [machine.acc_state(), machine.rej_state()]:
        if ps:
            print_state(tape, state, i)
        state, symbol, direction = trans[(state, tape[i])]
        tape[i] = symbol
        i += direction
        if i >= len(tape):
            tape.append("_")
        if i < 0:
            raise Exception("Machine went to -1")

    return state


ok = [
"$((()(())))",
"$(((((())))))",
"$()()()()",
"$()",
"$()(())"
]

notok = [
"$(((((((()",
"$((("
]


for e in ok:
    if run_machine(list(e), BracketMachine()) != BracketMachine().acc_state():
        print(f"Not ok! {e}")
        run_machine(list(e), BracketMachine(), True)

for e in notok:
    if run_machine(list(e), BracketMachine()) != BracketMachine().rej_state():
        print(f"Not ok! {e}")
        run_machine(list(e), BracketMachine(), True)


def turing_to_post(machine):
    states = []
    for s in machine.states():
        states += [
            f"L-{s}",
            f"L-{s}0",
            f"L-{s}1",
            f"R-{s}",
            f"R-{s}0",
            f"R-{s}1",
            f"R-{s}*",
            f"H-{s}",
            f"H-{s}0",
            f"H-{s}1"
        ]
    
