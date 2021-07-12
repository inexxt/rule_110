# Rule 110

This is a Python implementation of Rule 110 as a universal cellular automata. It is based on Matthew Cook's papers: 
 - Cook, Matthew. (2004). Universality in Elementary Cellular Automata. Complex Systems. 15. [link](https://wpmedia.wolfram.com/uploads/sites/13/2018/02/15-1-1.pdf) 
 - Cook, Matthew. (2009). A Concrete View of Rule 110 Computation. Electronic Proceedings in Theoretical Computer Science. 1. [link](https://arxiv.org/abs/0906.3248)

## What is going on here?

For now - pretty much everything interesting is in the `turing_post.py` file. It first defines a few Turing Machines used as the examples: 
 - `HaltingBracketMachine`, which halts if the input tape contains a correctly matching brackets.
 - `HaltingIs1MachineStartSymbol` which halt if the input tape starts with a symbol `1`
 - `HaltingIs1Machine`, the same as above, but with a slightly different implementation

Then it defines all the required machinery to run Turing Machines and unit-tests these above.

When we're sure that they work, it applies a sequence of transformations, starting from arbitrary TMs and goingh through:
 - TMs over ternary alphabet
 - TMs over binary alphabet
 - Tag systems
 - Cyclic tag systems
 - Cellular automata

The last step uses diagrams exported from Cook's for setting up the tape for CAs. Diagrams are included in the `blocks/` directory.

## Results

Unfortunately, there is an exponential blowup when going from tag systems to cyclic tag systems, which makes it unusable even for such simple machines as `HaltingIs1MachineStartSymbol`. Cook's describes an alternative approach, which does not have this problem, but it is not yet implemented.

To test the correctness, I wrote a simple rule 110 interpreter in C, in `process.c`, but even with its help, I couldn't get the machines to terminate on non-trivial examples.