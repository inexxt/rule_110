from PIL import Image
import numpy as np
from collections import Counter
from functools import partial
from tqdm import tqdm
from functools import lru_cache

TESTING = False


ORIG_BACKGROUND = 128
ORIG_WHITE = 255
ORIG_BLACK = 0
ORIG_ZERO = 179


NEW_BACKGROUND = 0
NEW_WHITE = 255
NEW_BLACK = 128
NEW_ZERO = 0  # Don't need zero, need only background


change = {
    ORIG_BACKGROUND: NEW_BACKGROUND,
    ORIG_WHITE: NEW_WHITE,
    ORIG_BLACK: NEW_BLACK,
    ORIG_ZERO: NEW_ZERO
}


def change_colors_t(x):
    return change[x]

change_colors = np.vectorize(change_colors_t)


blocks_names = list("ABCDEFGHIJKL")
all_blocks = {
    name: change_colors(np.array(Image.open(f"./blocks/{name}.png"))) for name in blocks_names
}


standard_blocks_names = list("DEFGHIJKL")
standard_blocks = {
    name: change_colors(np.array(Image.open(f"./blocks/{name}.png"))) for name in standard_blocks_names
}


left_block_names = list("AB")


C_block_raw = np.array(Image.open(f"./blocks/C.png"))
zero = None


y, x = np.meshgrid(np.arange(C_block_raw.shape[1]), np.arange(C_block_raw.shape[0]))


zero_locs = set([y for y, x in np.transpose(np.nonzero(np.vectorize(lambda x, y: C_block_raw[x, y] == ORIG_ZERO)(x, y)))])
assert(len(zero_locs) == 1)
zero_loc = list(zero_locs)[0] % 30


def is_tip(img, x, y):
    ydim, xdim = img.shape
    return y != 0 and y != ydim - 1 and            img[y, x] != NEW_BACKGROUND and            img[y - 1, x] == NEW_BACKGROUND and            img[y + 1, x] == NEW_BACKGROUND

def is_left_tip(img, x, y):
    return is_tip(img, x, y) and x != 0 and img[y, x - 1] == NEW_BACKGROUND

def is_right_tip(img, x, y):
    ydim, xdim = img.shape
    return is_tip(img, x, y) and x != xdim - 1 and img[y, x + 1] == NEW_BACKGROUND


CONST_LEFT_PHASE = 7

def get_left_phase(block_name):
    block = all_blocks[block_name]
    ydim, xdim = block.shape
    xmesh, ymesh = np.meshgrid(np.arange(xdim), np.arange(ydim))
    left_tips = np.transpose(np.nonzero(np.vectorize(partial(is_left_tip, block))(xmesh, ymesh)))
    left_phase = set([(x % 8, y % 30) for y, x in left_tips])
    assert(len(left_phase) == 1)
    left = list(left_phase)[0][1]
    assert(left == CONST_LEFT_PHASE)
    return left, left_tips

def get_right_phase(block_name):
    block = all_blocks[block_name]
    ydim, xdim = block.shape
    xmesh, ymesh = np.meshgrid(np.arange(xdim), np.arange(ydim))
    right_tips = np.transpose(np.nonzero(np.vectorize(partial(is_right_tip, block))(xmesh, ymesh)))
    right_phase = set([(x % 8, y % 30) for y, x in right_tips])
    assert(len(right_phase) == 1)
    return list(right_phase)[0][1], right_tips


c_right_phase, _ = get_right_phase("C")
zero_loc, c_right_phase
zero_phase = zero_loc - c_right_phase
assert(zero_phase == 18)

true_right_phases = {
    "D": 21,
    "E": 29,
    "F": 23,
    "G": 4,
    "H": 0,
    "I": 16,
    "J": 22,
    "K": 8,
    "L": 7,
}

if TESTING:
    answers = {}
    for name, img in standard_blocks.items():
        get_left_phase(name) # this calls assert inside
        right, _ = get_right_phase(name)
        answers[name] = right

    assert(answers == true_right_phases)


def change_of_phase(incoming_phase, right_phase):
    return ((CONST_LEFT_PHASE + 1) - right_phase + incoming_phase) % 30


def get_row(img, y):
    row = img[y, :]
    return row[np.vectorize(lambda x: x != NEW_BACKGROUND)(row)]


assert(list(get_row(all_blocks["C"], zero_loc))[:6] == [NEW_BLACK, NEW_WHITE, NEW_WHITE, NEW_BLACK, NEW_BLACK, NEW_WHITE])


def generate_rhs_from_sequence(sequence, zero_phase=None):
    rows = []
    if sequence[0] == "C":
        zero_phase = 18
        rows.append((get_row(all_blocks["C"], zero_loc)))
        sequence = sequence[1:]

    for s in tqdm(sequence):
        assert(s in standard_blocks_names)
        # print(zero_phase)
        right_phase = true_right_phases[s]
        zero_phase = change_of_phase(zero_phase, right_phase)
        rows.append(get_row(all_blocks[s], zero_phase))
    
    row = [x for l in rows for x in l]
    return (row, zero_phase)

if TESTING:
    sequence = list("CEDEDFDEG")
    assert(len(generate_rhs_from_sequence(sequence, zero_phase)[0]) == 2003)
    # len(generate_rhs_from_sequence(sequence, zero_phase)) / len(sequence) # about 200


def generate_lhs_from_sequence(sequence, zero_phase = None):
    change_phase = {
        "B": {
                2: 1,
                0: 2,
                1: 0
        },
        "A": {
                1: 1,
                2: 2,
                0: 0
        }
    }    
    row = []
    
    if sequence[-1] == "C":
        row += list(get_row(all_blocks["C"], zero_loc))
        sequence = sequence[:-1]
        zero_phase = 0
    
    for s in reversed(sequence):
        assert(s in left_block_names)
        zero_phase = change_phase[s][zero_phase]
        row = list(get_row(all_blocks[s], zero_phase)) + row 
    return (row, zero_phase)

if TESTING:
    sequence = ["A"] * 11 + ["B"] + ["A"] * 12 + ["B"] + ["C"]
    assert(len(generate_lhs_from_sequence(sequence)[0]) == 762)
    # len(generate_lhs_from_sequence(sequence)) / len(sequence) # about 30
