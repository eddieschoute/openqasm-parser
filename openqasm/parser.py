from lark import Lark
from pkg_resources import resource_string

"""The grammar is imported from the openqasm.lark file as a string."""
GRAMMAR = resource_string(__name__, 'openqasm.lark').decode()

text = """OPENQASM 2.0;
include "qelib1.inc";
gate pre q { } // pre-rotation
gate post q { } // post-rotation qreg q[1];
creg c[1];
pre q[0];
barrier q;
h q[0];
barrier q;
post q[0];
measure q[0] -> c[0];
"""

openqasm_parser = Lark(GRAMMAR)
openqasm = openqasm_parser.parse
