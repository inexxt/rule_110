from collections import deque
import numpy as np
from math import ceil, log2
from typing import NamedTuple, Optional
import itertools

def flatten(ll):
    return [x for l in ll for x in l]

TESTING = False

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
        return ["$", "(", ")", "e", "_"]

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

            ("q_v", "$"): ('q_v', "$", HALT),
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

class HaltingIs1MachineStartSymbol():
    def __init__(self):
        self.ok = ["$1", "$11", "$110"]
        self.notok = ["$0", "$01", "$011"]

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


# This machine checks if the tape starts from 1
class HaltingIs1Machine():
    def __init__(self):
        self.ok = ["1", "10", "110"]
        self.notok = ["0", "00", "011"]

    def start_state(self):
        return "q_s"

    def symbols(self):
        return ["0", "1", "_"]

    def states(self):
        return ["q_r", "q_s"]

    def trans_function(self):
        return {
            ("q_s", "0"): ("q_r", "0", RIGHT),
            ("q_s", "1"): ("q_s", "0", HALT),
            ("q_s", "_"): ("q_r", "0", RIGHT),

            ("q_r", "0"): ("q_r", "0", RIGHT),
            ("q_r", "1"): ("q_r", "0", RIGHT),
            ("q_r", "_"): ("q_r", "0", RIGHT),
        }


def print_state(tape, state, index):
    print(f"STATE: state={state}, index={index}")

    for i in range(index):
        print("    ", end="")

    print("  v")

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
    if direction == HALT and debug_info:
        print("Machine stopped")
    elif direction != HALT and debug_info:
        print("Machine didn't stop")
    return direction


def testing_turing(machine):
    all_in = True
    for state in machine.states():
        for letter in machine.symbols():
            if (state, letter) not in machine.trans_function():
                print(state, letter, " not in transition function")
                all_in = False
    if all_in:
        print(f"OK Testing machine {type(machine).__name__} for transition completeness")

    for e in machine.ok:
        if run_machine(list(e), machine) != HALT:
            print(f"Not ok! {type(machine).__name__} on {e}")
            # run_machine(list(e), machine, debug_info=True)
        else:
            print(f"OK Testing machine {type(machine).__name__} on data {e}")

    for e in machine.notok:
        if run_machine(list(e), machine) == HALT:
            print(f"Not ok! {type(machine).__name__} on {e}")
            # run_machine(list(e), machine, debug_info=True)
        else:
            print(f"OK Testing machine {type(machine).__name__} on data {e}")


if TESTING:
    testing_turing(HaltingBracketMachine())
    testing_turing(HaltingIs1Machine())



def turing_to_ternary_turing(bmachine):
    if len(bmachine.symbols()) <= 3:
        return bmachine

    alphabet = ["0", "1", "_"]

    encoding_len = ceil(log2(len(bmachine.symbols()) - 1)) # we're not coding "_"
    # const-len encoding wastes some space - it would be easier to use e.g. Huffman
    # and, in particular, encode BLANK as just BLANK, not as encoding_len * BLANK
    # but doing so simplifies the design - for example, MoveState can move always the same amount  
    encode = {
        x: f"{{0:0{encoding_len}b}}".format(bmachine.symbols().index(x)) for x in bmachine.symbols()
    }

    encode["_"] = "_" * encoding_len

    decode = {
        v: k for k, v in encode.items()
    }
    decode["_" * encoding_len] = "_"

    encode_tape = lambda tape: "".join(encode[x] for x in tape)
    
    all_letters = ["".join(x) for x in itertools.product(alphabet, repeat=encoding_len)]

    class ReadState(NamedTuple):
        x: str # bmachine_state
        letters: Optional[str]
        remaining: int

    class MoveState(NamedTuple):
        x: str # bmachine_state
        mdir: int
        remaining: int

    class WriteState(NamedTuple):
        x: str # bmachine_state
        letters: str
        mdir: int
        remaining: int

    class BreakState(NamedTuple):
        pass

    class TernaryMachine():        
        def __init__(self):

            self.ok = [encode_tape(x) for x in bmachine.ok]
            self.notok = [encode_tape(x) for x in bmachine.notok]
            
            states = []
            bstates = bmachine.states()
            # xRT means that it's read the first symbol and it was T, just xR means that it starts reading
            
            for x in bstates:
                for letters in encode.values():
                    for remaining in range(1, encoding_len + 1):
                        states.append(ReadState(x=x, letters=letters[:-remaining], remaining=remaining))

            # There are two stages of writing
            # 0 - I transitioned to a new state and the original TM told me to write a symbol in the cell
            #     so, I write the last letter of an encoded symbol and move left       
            # 1 - I am backed up one cell, I write the second letter of the encoded symbol 
            #     and move to a state that tells me which direction to move (I have to remember that through the whole stage)
            
            for x in bstates:
                for mdir in [LEFT, RIGHT, HALT]:
                    for letters in encode.values():
                        for remaining in range(1, encoding_len):
                            states.append(WriteState(x=x, letters=letters[:-remaining], remaining=remaining, mdir=mdir))

            for x in bstates:
                for mdir in [LEFT, RIGHT]:
                    for remaining in range(1, encoding_len):
                        states.append(MoveState(x=x, mdir=mdir, remaining=remaining))
                
                states.append(MoveState(x=x, mdir=HALT, remaining=encoding_len - 1))

            states.append(BreakState())
            self._states = states


            tt = {}

            # States of type Read
            for x in bstates: 
                for letters in all_letters:
                    for remaining in range(1, encoding_len + 1):
                        if ReadState(x=x, letters=letters[:-remaining] + letters[-remaining], remaining=remaining - 1) in self._states:
                            tt[(ReadState(x=x, letters=letters[:-remaining], remaining=remaining), letters[-remaining])] = (
                                ReadState(x=x, letters=letters[:-remaining] + letters[-remaining], remaining=remaining - 1),
                                letters[-remaining],
                                RIGHT
                            )
                        else:
                            tt[(ReadState(x=x, letters=letters[:-remaining], remaining=remaining), letters[-remaining])] = (
                                BreakState(),
                                letters[-remaining],
                                RIGHT
                            )

            # States of type Read with all letters read
            for x in bstates:
                for letters in all_letters:
                    if letters in decode:
                        new_x, write_symbol, mdir = bmachine.trans_function()[(x, decode[letters])] 
                        write_symbol_enc = encode[write_symbol]

                        tt[(ReadState(x=x, letters=letters[:-1], remaining=1), letters[-1])] = (
                            WriteState(x=new_x, letters=write_symbol_enc[:-1], mdir=mdir, remaining=encoding_len - 1),
                            write_symbol_enc[-1], 
                            LEFT
                        )
                    else:
                        tt[(ReadState(x=x, letters=letters[:-1], remaining=1), letters[-1])] = (
                            BreakState(),
                            letters[-1], 
                            RIGHT
                        )

            # states of type xW
            for x in bstates:
                for letters in encode.values():
                    for any_letter in ["0", "1", "_"]:
                        for mdir in [LEFT, RIGHT, HALT]:
                            for remaining in range(2, encoding_len):
                                tt[(WriteState(x=x, letters=letters[:-remaining], mdir=mdir), any_letter)] = (
                                    WriteState(x=x, letters=letters[:-remaining+1], mdir=mdir),
                                    letters[-remaining],
                                    LEFT
                                )
                            tt[(WriteState(x=x, letters=letters[0], remaining=1, mdir=mdir), any_letter)] = (
                                MoveState(x=x, mdir=mdir, remaining=encoding_len - 1),
                                letters[0],
                                mdir
                            )
            
            for x in bstates:
                for any_letter in ["0", "1", "_"]:
                    for mdir in [LEFT, RIGHT]:
                        for remaining in range(1, encoding_len):
                            tt[(MoveState(x=x, mdir=mdir, remaining=remaining), any_letter)] = (
                                MoveState(x=x, mdir=mdir, remaining=remaining - 1),
                                any_letter,
                                mdir
                            )
                        tt[(MoveState(x=x, mdir=mdir, remaining=1), any_letter)] = (
                            ReadState(x=x, letters="", remaining=encoding_len),
                            any_letter,
                            mdir
                        )

                    # Now, the HALT case is easy
                    tt[(MoveState(x=x, mdir=HALT, remaining=encoding_len - 1), any_letter)] = (
                        MoveState(x=x, mdir=HALT, remaining=encoding_len - 1),
                        any_letter,
                        HALT
                    )

            for letter in ["0", "1", "_"]:
                tt[(BreakState(), letter)] = (BreakState(), letter, RIGHT)

            self._trans_function = tt


        def start_state(self):
            return ReadState(x=bmachine.start_state(), letters="", remaining=encoding_len) # it just starts reading

        def symbols(self):
            return ["0", "1", "_"] # B is blank

        def states(self):
            return self._states

        def trans_function(self):
            return self._trans_function


    TernaryMachine.__name__ = f"TernaryMachine({type(bmachine).__name__})"
    return TernaryMachine()


if TESTING:
    testing_turing(turing_to_ternary_turing(HaltingIs1MachineStartSymbol()))
    testing_turing(turing_to_ternary_turing(HaltingBracketMachine()))
    testing_turing(turing_to_ternary_turing(HaltingIs1Machine()))
# machine = turing_to_ternary_turing(HaltingBracketMachine())
# run_machine(list(machine.notok[1]), machine, time_limit=30, debug_info=True)



def ternary_to_binary_turing(bmachine):
    assert(set(bmachine.symbols()) == {"0", "1", "_"})

    encode = {
        "0": "A_",
        "1": "AA",
        "_": "__"
    }

    decode = {
        "A_": "0",
        "AA": "1",
        "__": "_"
    }
    
    encode_tape = lambda tape: "".join(encode[x] for x in tape)


    class ReadState(NamedTuple):
        x: str # bmachine_state
        letter: Optional[str]

    class MoveState(NamedTuple):
        x: str # bmachine_state
        mdir: int
        steps: int

    class WriteState(NamedTuple):
        x: str # bmachine_state
        letter: str
        mdir: int

    class BreakState(NamedTuple):
        # used to loop right forever
        pass

    class BinaryMachine():
        def __init__(self):

            self.ok = [encode_tape(x) for x in bmachine.ok]
            self.notok = [encode_tape(x) for x in bmachine.notok]
            
            states = []
            bstates = bmachine.states()
            # xRT means that it's read the first symbol and it was T, just xR means that it starts reading
            
            for x in bstates:
                for letter in ["A", "_", None]:
                    states.append(ReadState(x=x, letter=letter))
        
            # There are two stages of writing
            # 0 - I transitioned to a new state and the original TM told me to write a symbol in the cell
            #     so, I write the last letter of an encoded symbol and move left       
            # 1 - I am backed up one cell, I write the second letter of the encoded symbol 
            #     and move to a state that tells me which direction to move (I have to remember that through the whole stage)
            
            for x in bstates:
                for mdir in [LEFT, RIGHT, HALT]:
                    for letter in ["A", "_"]:
                        states.append(WriteState(x=x, letter=letter, mdir=mdir))
            
            for x in bstates:
                for mdir in [LEFT, RIGHT]:
                    for steps in [1]:
                        states.append(MoveState(x=x, mdir=mdir, steps=steps))
                    
                states.append(MoveState(x=x, mdir=HALT, steps=1)) # TODO doesnt' really matter

            states.append(BreakState())
            self._states = states


            tt = {}

            # States of type xR
            for x in bstates: 
                for letter in ["A", "_"]:
                    tt[(ReadState(x=x, letter=None), letter)] = (
                        ReadState(x=x, letter=letter),
                        letter,
                        RIGHT
                    )

            # States of type xRT
            for x in bstates:
                for l1 in ["A", "_"]:
                    for l2 in ["A", "_"]:
                        if l2 + l1 not in decode:
                            tt[(ReadState(x=x, letter=l2), l1)] = (
                                BreakState(),
                                l1, 
                                RIGHT
                            )
                        else:
                            new_x, write_symbol, move_direction = bmachine.trans_function()[(x, decode[l2 + l1])] 
                            write_symbol_enc = encode[write_symbol]
                            assert(WriteState(x=new_x, letter=write_symbol_enc[0], mdir=move_direction) in self._states)
                            tt[(ReadState(x=x, letter=l2), l1)] = (
                                WriteState(x=new_x, letter=write_symbol_enc[0], mdir=move_direction),
                                write_symbol_enc[-1], 
                                LEFT
                            )

            # states of type xW
            for x in bstates:
                for l1 in ["A", "_"]:
                    for l2 in ["A", "_"]:
                        for mdir in [LEFT, RIGHT, HALT]:
                            tt[(WriteState(x=x, letter=l2, mdir=mdir), l1)] = (
                                MoveState(x=x, mdir=mdir, steps=1),
                                l2,
                                mdir
                            )
            for x in bstates:
                for l in ["A", "_"]:
                    for mdir in [LEFT, RIGHT]:
                        tt[(MoveState(x=x, mdir=mdir, steps=1), l)] = (
                            ReadState(x=x, letter=None),
                            l,
                            mdir
                        )

                    # Now, the HALT case is easy
                    tt[(MoveState(x=x, mdir=HALT, steps=1), l)] = (
                        MoveState(x=x, mdir=HALT, steps=1),
                        l,
                        HALT
                    )
            for letter in ["A", "_"]:
                tt[(BreakState(), letter)] = (BreakState(), letter, RIGHT)

            self._trans_function = tt


        def start_state(self):
            return ReadState(x=bmachine.start_state(), letter=None) # it just starts reading

        def symbols(self):
            return ["A", "_"] # B is blank

        def states(self):
            return self._states

        def trans_function(self):
            return self._trans_function

    BinaryMachine.__name__ = f"BinaryMachine({type(bmachine).__name__})"

    return BinaryMachine()

if TESTING:
    testing_turing(ternary_to_binary_turing(HaltingIs1Machine()))
    testing_turing(ternary_to_binary_turing(turing_to_ternary_turing(HaltingBracketMachine())))
    testing_turing(ternary_to_binary_turing(turing_to_ternary_turing(HaltingIs1MachineStartSymbol())))

# machine = ternary_to_binary_turing(turing_to_ternary_turing(HaltingIs1MachineStartSymbol()))
# # machine = ternary_to_binary_turing(HaltingIs1Machine())
# run_machine(list(machine.ok[0]), machine, time_limit=30, debug_info=True)


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
    c = alphabet.index(tape[0]) + 1
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

def simulate_tag(tag_system, time_limit=100000000, debug_info=False):
    tape = deque(tag_system.tape)

    if debug_info:
        print("Initial tape length: ", len(tape))
        # print("Tag tape:")
        # print(tag_system.tape)
        # print("Transitions:")
        # print(tag_system.transitions)

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
            # simulate_tag(turing_to_tag(machine, list(e)), debug_info=True)
        else:
            print(f"Testing machine {machine} on data {e}: OK")

    for e in machine.notok:
        if simulate_tag(turing_to_tag(machine, list(e))):
            print(f"Not ok! {e}")
            # simulate_tag(turing_to_tag(machine, list(e)), debug_info=True)
        else:
            print(f"Testing machine {machine} on data {e}: OK")


if TESTING:
    testing_tag(HaltingIs1Machine())
    testing_tag(HaltingBracketMachine())
    testing_tag(ternary_to_binary_turing(HaltingIs1Machine()))
    ternary_to_binary_turing(turing_to_ternary_turing(HaltingIs1MachineStartSymbol()))    
    testing_tag(ternary_to_binary_turing(turing_to_ternary_turing(HaltingBracketMachine())))

# machine = ternary_to_binary_turing(turing_to_ternary_turing(HaltingIs1MachineStartSymbol()))
# print(simulate_tag(turing_to_tag(machine, list(machine.ok[1])), debug_info=True, time_limit=1000000000))


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

def simulate_cyclic(cyclic_system, time_limit=100000000, debug_info=False):
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

if TESTING:
    testing_cyclic(HaltingIs1Machine())
    testing_cyclic(HaltingBracketMachine())
    testing_cyclic(ternary_to_binary_turing(turing_to_ternary_turing(HaltingBracketMachine())))
    testing_cyclic(ternary_to_binary_turing(turing_to_ternary_turing(HaltingIs1MachineStartSymbol())))
    testing_cyclic(ternary_to_binary_turing(HaltingIs1Machine()))

# machine = ternary_to_binary_turing(turing_to_ternary_turing(HaltingIs1MachineStartSymbol()))
# print(simulate_tag(turing_to_tag(machine, list(machine.ok[1])), debug_info=True, time_limit=1000000000))


class CellularAutomaton:
    def __init__(self, rule, tape):
        self.rule = rule
        self.tape = tape


def generate_central_symbols_tape(cyclic_system):
    central_tape = []
    central_tape += ["C"]
    for elem in cyclic_system.tape:
        if elem == 0:
            central_tape += ["E", "D"]
        else:
            central_tape += ["F", "D"]

    assert(central_tape[-1] == "D")
    central_tape[-1] = "G"
    return central_tape


def test_generate_central_symbols_tape():
    cyclic_system = CyclicTagSystem([], [0,0,1,0], 0)
    assert(generate_central_symbols_tape(cyclic_system) == list("CEDEDFDEG"))


if TESTING:
    test_generate_central_symbols_tape()


def generate_rhs_symbols_tape(cyclic_system):
    rhs_tape = []
    for lelem in cyclic_system.transitions:
        current_tape = []
        for elem in lelem:
            if elem == 0:
                current_tape += ["I", "J"]
            else:
                current_tape += ["I", "I"]
        if current_tape:
            assert(current_tape[0] == "I")
            current_tape = ["K", "H"] + current_tape[1:]
        else:
            current_tape = ["L"]

        rhs_tape += current_tape

    assert(rhs_tape[0] == "K")
    rhs_tape = rhs_tape[1:] + ["K"]
    return rhs_tape

def test_generate_rhs_symbols_tape():
    cyclic_system = CyclicTagSystem([[1, 0], [0, 1, 1, 0], [], []], [], 0)
    assert(generate_rhs_symbols_tape(cyclic_system) == list("HIIJKHJIIIIIJLLK"))


if TESTING:
    test_generate_rhs_symbols_tape()


def generate_lhs_symbols_tape(cyclic_system):
    ns = sum(len([t for t in l if t == 0]) for l in cyclic_system.transitions)
    ys = sum(len([t for t in l if t == 1]) for l in cyclic_system.transitions)
    nonempty = len([l for l in cyclic_system.transitions if l])
    empty = len([l for l in cyclic_system.transitions if not l])

    v = 76 * ys + 80 * ns + 60 * nonempty + 43 * empty

    lhs_tape = ["A"] * v + ["B"] + ["A"] * 13 + ["B"] + ["A"] * 11 + ["B"] + ["A"] * 12 + ["B"]

    return lhs_tape


def cyclic_to_symbols_tape(cyclic_system):
    
    if not cyclic_system.tape:
        raise Exception("Converting empty cyclic systems is not possible")

    central = generate_central_symbols_tape(cyclic_system)
    lhs = generate_lhs_symbols_tape(cyclic_system)
    rhs = generate_rhs_symbols_tape(cyclic_system)

    return lhs, central, rhs


if TESTING:
    machine, lhs_num, rhs_num = HaltingBracketMachine(), 1, 1 # 24e6 in case of (1, 1)
    l, c, r = cyclic_to_symbols_tape(tag_to_cyclic(turing_to_tag(machine, list(machine.notok[0]))), lhs_num, rhs_num)

    machine, lhs_num, rhs_num = HaltingIs1Machine(), 100, 100 # 11e9 in case of (150, 150)
    l, c, r = cyclic_to_symbols_tape(tag_to_cyclic(turing_to_tag(machine, list(machine.notok[0]))), lhs_num, rhs_num)


RULE = 110

from symbols_to_bits import generate_rhs_from_sequence, generate_lhs_from_sequence

def cyclic_to_automaton(cyclic_system, lhs_num, rhs_num):
    lhs, central, rhs = cyclic_to_symbols_tape(cyclic_system)
    # Important - zero_phase is 0, because- zero row in C block matches zeroth line in both
    # A and B blocks
    lhs_tape, lhs_zero_phase = generate_lhs_from_sequence(lhs * lhs_num, zero_phase=0)
    central_tape, central_zero_phase = generate_rhs_from_sequence(central)
    rhs_tape, rhs_zero_phase = generate_rhs_from_sequence(rhs * rhs_num, central_zero_phase)

    tape = np.concatenate([lhs_tape, central_tape, rhs_tape], axis=0)
    return CellularAutomaton(RULE, tape)



rep = 2
# machine, lhs_num, rhs_num = HaltingBracketMachine(), 1, 1 # 24e6 in case of (1, 1)
machine, lhs_num, rhs_num = ternary_to_binary_turing(HaltingIs1Machine()), rep, rep # 11e9 in case of (150, 150)
automaton = cyclic_to_automaton(tag_to_cyclic(turing_to_tag(machine, list(machine.ok[0]))), lhs_num, rhs_num)
print(automaton.tape.shape, automaton.tape.dtype, rep)
print(np.sum(automaton.tape))


# with open(f"bigrow{rep}.np", mode='wb') as f:
#     automaton.tape.tofile(f)


# the following sequences appear if and only if the corresponding Turing machine halts:
# spatial: 01101001101000
# time: 110101010111111
