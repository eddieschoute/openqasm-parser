from lark import Lark
from pkg_resources import resource_string
import logging

from openqasm.transformer import OpenQasmTransformer

logging.basicConfig(level=logging.DEBUG)

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

openqasm_parser = Lark(GRAMMAR, parser='lalr', maybe_placeholders=True, transformer=OpenQasmTransformer())
openqasm = openqasm_parser.parse

text = """
OPENQASM 2.0;
include "qelib\\".inc";
qreg q[3];
creg c0[1];
creg c1[1];
creg c2[1];
reset q;
// optional post-rotation for state tomography gate post q { }
u3(0.3,0.2,0.1) q[0];
h q[1];
CX q[1],q[2];
barrier q;
cx q[0],q[1];
h q[0];
measure q[0] -> c0[0];
measure q[1] -> c1[0];
if(c0==1) z q[2];
if(c1==1) x q[2];
post q[2];
measure q[2] -> c2[0];
U(2 * - sin(3)) q;
"""

# with open('../highmem.qasm') as f:
#     big_text = f.read()
# res = openqasm(big_text)
# res = openqasm(text)
# print(res)
# print(res.pretty())
# input('bla')
