from collections import deque

LEFT = -1
RIGHT = 1
HALT = 0

class HaltingBracketMachine():
    def __init__(self):
        self.ok = [
            "$()",
            "$()()",
            "$(())",
            "$()(())"
        ]

        self.notok = [
            "$(",
            "$)",
            "$)("
            "$((",
            "$))",
            "$()((",   
        ]


    def start_state(self):
        return "q_)"

    def symbols(self):
        return ["$", "(", ")", "_", "e"]

    def states(self):
        return ["q_)", "q_b", "q_(", "q_v", "q_r"]

    def trans_function(self):
        return {
            ("q_)", "$"): ("q_)", "$", RIGHT),
            ("q_)", "("): ("q_)", "(", RIGHT),
            ("q_)", "e"): ("q_)", "e", RIGHT),
            ("q_)", ")"): ("q_(", "e", LEFT),
            ("q_)", "_"): ("q_v", "_", LEFT),

            ("q_(", ")"): ("q_r", "_", LEFT),
            ("q_(", "$"): ("q_r", "_", RIGHT),
            ("q_(", "e"): ("q_(", "e", LEFT),
            ("q_(", "("): ("q_b", "e", LEFT),
            ("q_(", "_"): ("q_r", "_", LEFT),

            ("q_b", "_"): ("q_r", "_", LEFT),
            ("q_b", "$"): ("q_)", "$", RIGHT),
            ("q_b", ")"): ("q_b", ")", LEFT),
            ("q_b", "e"): ("q_b", "e", LEFT),
            ("q_b", "("): ("q_b", "(", LEFT),

            ("q_v", "$"): (None, None, HALT),
            ("q_v", "("): ("q_r", "(", RIGHT),
            ("q_v", "e"): ("q_v", "e", LEFT),
            ("q_v", ")"): ("q_r", "e", LEFT),
            ("q_v", "_"): ("q_r", "e", LEFT),
            
            ("q_r", "_"): ("q_r", "_", RIGHT),
            ("q_r", "$"): ("q_r", "$", RIGHT),
            ("q_r", ")"): ("q_r", ")", RIGHT),
            ("q_r", "e"): ("q_r", "e", RIGHT),
            ("q_r", "("): ("q_r", "(", RIGHT)
        }

class HaltingIs1Machine():
    def __init__(self):
        self.ok = ["$1", "$110"]
        self.notok = ["$0", "$011"]

    def start_state(self):
        return "q_s"

    def symbols(self):
        return ["$", "0", "1", "_"]

    def states(self):
        return ["q_r", "q_s"]

    def trans_function(self):
        return {
            ("q_s", "0"): ("q_r", "0", RIGHT),
            ("q_s", "1"): ("q_s", "0", HALT),
            ("q_s", "$"): ("q_s", "0", RIGHT),
            ("q_s", "_"): ("q_r", "0", RIGHT),

            ("q_r", "0"): ("q_r", "0", RIGHT),
            ("q_r", "1"): ("q_r", "0", RIGHT),
            ("q_r", "$"): ("q_r", "0", RIGHT),
            ("q_r", "_"): ("q_r", "0", RIGHT),
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

def run_machine(tape, machine, time_limit=10000, debug_info=False):
    orig_tape = tape.copy()

    state = machine.start_state()
    trans = machine.trans_function()
    direction = LEFT
    i = 0
    while direction != HALT and time_limit > 0:
        if debug_info:
            print_state(tape, state, i)
        state, symbol, direction = trans[(state, tape[i])]
        tape[i] = symbol
        i += direction
        if i >= len(tape):
            tape.append("_")
        if i < 0:
            if debug_info:
                print(orig_tape)
            raise Exception("Machine went to -1")

        time_limit -= 1

    return direction


def testing_turing(machine):
    for e in machine.ok:
        if run_machine(list(e), machine) != HALT:
            print(f"Not ok! {e}")
            run_machine(list(e), machine, True)
        else:
            print(f"Testing machine {machine} on data {e}: OK")

    for e in machine.notok:
        if run_machine(list(e), machine) == HALT:
            print(f"Not ok! {e}")
            run_machine(list(e), machine, True)
        else:
            print(f"Testing machine {machine} on data {e}: OK")


# testing_turing(HaltingBracketMachine())
# testing_turing(HaltingIs1Machine())


class TagSystem:
    def __init__(self, symbols, transitions, tape, s):
        self.s = s
        self.symbols = symbols
        self.transitions = transitions
        self.tape = tape


def turing_to_tag(machine, tape):
    states = []
    alphabet = machine.symbols()
    # used to mark the left and right end of the central non-periodic tape
    alphabet += ["sigmaL", "sigmaR"]
    s = len(alphabet)

    start_state = machine.start_state()

    # we are always assuming the tape is of the following form
    # [empty tape] [head on 0, first symbol on 0] [second symbol on 1] ... [n-th symbol on n-1] _ _ _ ...
    # the symbol under the head
    c = alphabet.index("$") + 1
    # the length of non-empty region on the left of the tape
    x = 0
    # this region itself
    b = []
    # the length of repeating region on the left and on the right
    w = 1
    z = 1
    # the region on the left (numbering starting from 0, that's why)
    a = [None, alphabet.index("_") + 1]
    e = [None, alphabet.index("_") + 1]

    # the length of the non-empty region on the right of the tape
    y = len(tape) - 1 # because we already counted the "$"
    d = [None] + [alphabet.index(el) + 1 for el in tape[1:]]

    transitions = {}

    for st in machine.states():
        states += [
            ("H", st),
            ("L", st),
            ("R", st),
            ("R", st, "*"),
        ]

        transitions[("H", st)] = [("H", st, sigma) for sigma in alphabet]
        transitions[("L", st)] = [("L", st, sigma) for sigma in alphabet]
        transitions[("R", st)] = [("R", st, sigma) for sigma in alphabet]
        transitions[("R", st, "*")] = [("R", st)] * s

    for st in machine.states():
        for sigma in alphabet:
            states += [
                ("H", st, sigma),
                ("L", st, sigma),
                ("R", st, sigma),
            ]
            if sigma not in ["sigmaL", "sigmaR"]:
                new_state, new_letter, direction = machine.trans_function()[st, sigma]
                if direction == LEFT:
                    transitions[("H", st, sigma)] = [("R", new_state, "*")] * (s * (s - (alphabet.index(new_letter) + 1))) + \
                                                    [("H", new_state)] * (alphabet.index(sigma) + 1)
                    
                    transitions[("L", st, sigma)] = [("L", new_state)]
                    transitions[("R", st, sigma)] = [("R", new_state)] * s**2

                    
                if direction == RIGHT:
                    transitions[("H", st, sigma)] = [("H", new_state)] * (alphabet.index(sigma) + 1) + \
                                                    [("L", new_state)] * (s * (s - (alphabet.index(new_letter) + 1)))
                    
                    transitions[("L", st, sigma)] = [("L", new_state)] * s**2
                    transitions[("R", st, sigma)] = [("R", new_state)]

                if direction == HALT:   
                    transitions[("H", st, sigma)] = []
                    transitions[("L", st, sigma)] = []
                    transitions[("R", st, sigma)] = []


        transitions[("H", st, "sigmaL")] = [("H", st)] * (len(alphabet) - 1 + s - a[1]) + \
                                           [("L", st)] * (s**w + sum((s - a[k]) * s**(k-1) for k in range(2, w+1)))

        transitions[("H", st, "sigmaR")] = [("R", st, "*")] * sum((s - e[k]) * s**(k-1) for k in range(2, z+1)) + \
                                           [("H", st)] * (s + s - e[1])

        transitions[("L", st, "sigmaL")] = [("L", st)] * s
        transitions[("L", st, "sigmaR")] = [("L", st)] * s
        
        transitions[("R", st, "sigmaL")] = [("R", st)] * s
        transitions[("R", st, "sigmaR")] = [("R", st)] * s
        
    
    tag_tape = [("H", start_state)] * (1 + s - c) + \
               [("L", start_state)] * (s**(x+1) + sum((s - b[k]) * s**k for k in range(1, x+1))) + \
               [("R", start_state)] * sum((s - d[k]) * s**k for k in range(1, y+1))

    return TagSystem(states, transitions, tag_tape, s)

def simulate_tag(tag_system, time_limit=10000000, debug_info=False):
    tape = deque(tag_system.tape)

    if debug_info:
        print("Initial tape length: ", len(tape))
        print("Tag tape:")
        print(tag_system.tape)
        print("Transitions:")
        print(tag_system.transitions)

    while len(tape) != 0 and time_limit > 0:
        first = tape.popleft()
        
        for _ in range(tag_system.s - 1):
            tape.popleft()

        extension = tag_system.transitions[first]
        # TODO should'nt I just check if the tape is non-empty?
        if not extension:
            return True
        tape.extend(extension)

        time_limit -= 1

        if time_limit % 10000 == 0 and debug_info:
            print(first, len(tape))

    return False
    
def testing_tag(machine):
    for e in machine.ok:
        if not simulate_tag(turing_to_tag(machine, list(e))):
            print(f"Not ok! {e}")
            simulate_tag(turing_to_tag(machine, list(e)), debug_info=True)
        else:
            print(f"Testing machine {machine} on data {e}: OK")

    for e in machine.notok:
        if simulate_tag(turing_to_tag(machine, list(e))):
            print(f"Not ok! {e}")
            simulate_tag(turing_to_tag(machine, list(e)), debug_info=True)
        else:
            print(f"Testing machine {machine} on data {e}: OK")


# testing_tag(HaltingIs1Machine())
# testing_tag(HaltingBracketMachine())


class CyclicTagSystem():
    def __init__(self, transitions, tape, halting_index):
        self.transitions = transitions
        self.tape = tape
        self.halting_index = halting_index


def tag_to_cyclic(tag_system):
    symbols = tag_system.symbols.copy()
    transitions = tag_system.transitions.copy()

    for idx in range(len(tag_system.symbols) % 6):
        # we append D-ummy symbols to get the overall number of symbols be of multiple of 6
        symbols.append(("D", idx))
        # TODO won't this screw up the stop condition?
        transitions[("D", idx)] = []
    encode = lambda x: list([0] * symbols.index(x) + [1] + [0] * (len(symbols) - (symbols.index(x) + 1)))

    new_tape = []
    for t in tag_system.tape:
        new_tape += encode(t)


    halting_index = set()
    new_transitions = []
    for e, symbol in enumerate(symbols):
        new_transitions.append([])
        for e in transitions[symbol]:
            new_transitions[-1] += encode(e)
        if not transitions[symbol] and symbol[0] != "D":
            halting_index.add(e)

    for _ in range((tag_system.s - 1) * len(symbols)):
        new_transitions.append([])

    # print(halting_index)
    # for e in halting_index:
    #     print(tag_system.symbols[e])
    # print(len(tag_system.symbols))

    return CyclicTagSystem(new_transitions, new_tape, halting_index)

def simulate_cyclic(cyclic_system, time_limit=10000000, debug_info=False):
    tape = deque(cyclic_system.tape)

    # if debug_info:
    #     print("Initial tape length: ", len(tape))
    #     print("Tag tape:")
    #     print("".join(cyclic_system.tape))
    #     print("Transitions:")
    #     print(["".join(x) for x in cyclic_system.transitions])

    extension_idx = 0
    while len(tape) != 0 and time_limit > 0:
        first = tape.popleft()
        extension_idx = extension_idx % len(cyclic_system.transitions)

        if first == 1:
            if extension_idx in cyclic_system.halting_index:
                return True

            tape.extend(cyclic_system.transitions[extension_idx])

        extension_idx += 1
        time_limit -= 1

        if time_limit % 1000000 == 0 and debug_info:
            print(first, len(tape), time_limit)

    return len(tape) == 0


def testing_cyclic(machine):
    for e in machine.ok:
        if not simulate_cyclic(tag_to_cyclic(turing_to_tag(machine, list(e)))):
            print(f"Not ok! {e}")
            simulate_cyclic(tag_to_cyclic(turing_to_tag(machine, list(e))), debug_info=False)
        else:
            print(f"Testing machine {machine} on data {e}: OK")

    for e in machine.notok:
        if simulate_cyclic(tag_to_cyclic(turing_to_tag(machine, list(e)))):
            print(f"Not ok! {e}")
            simulate_cyclic(tag_to_cyclic(turing_to_tag(machine, list(e))), debug_info=False)
        else:
            print(f"Testing machine {machine} on data {e}: OK")

# testing_cyclic(HaltingIs1Machine())
# testing_cyclic(HaltingBracketMachine())

machine = HaltingBracketMachine()
print(simulate_cyclic(tag_to_cyclic(turing_to_tag(machine, list(machine.notok[0]))), time_limit=1000000000, debug_info=True))
