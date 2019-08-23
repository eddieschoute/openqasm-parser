from pathlib import Path
from typing import NamedTuple, Any, Optional, Union, Tuple, List, Dict
import enum
from enum import Enum
from decimal import Decimal

from lark import Transformer, Discard


class Qubit:
    pass


class Cbit:
    pass


QuantumRegister = Tuple[Qubit, ...]
ClassicalRegister = Tuple[Cbit, ...]


class Reference(NamedTuple):
    id: str
    index: Optional[int]


class OpenQasmTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.qregs: Dict[str, QuantumRegister] = {}
        self.cregs: Dict[str, ClassicalRegister] = {}

    def nninteger(self, t):
        return int(t[0])

    def real(self, t):
        return Decimal(t[0])

    def id(self, t):
        return str(t[0])

    def from_reference(self, ref: Reference):
        if ref.id in self.qregs:
            reg = self.qregs[ref.id]
        else:
            reg = self.cregs[ref.id]
        if ref.index:
            return reg[ref.index]
        return reg

    def argument(self, t):
        return Reference(t[0], t[1])

    def params(self, t):
        return tuple(self.from_reference(ref) for ref in t)

    def args(self, t):
        return tuple(t)

    def idlist(self, t):
        return tuple(t)

    def explist(self, t):
        return tuple(t)

    def qregdecl(self, t):
        qreg = tuple(Qubit() for i in range(t[1]))
        self.qregs[t[0]] = qreg
        return QregDecl(qreg)

    def cregdecl(self, t):
        creg = tuple(Cbit() for i in range(t[1]))
        self.cregs[t[0]] = creg
        return CregDecl(creg)

    def opaque(self, t):
        return Call(*t)

    def gbody(self, t):
        return tuple(t)

    def gatedef(self, t):
        return GateDefinition(*t)

    def qcall(self, t):
        return Call(name=t[0], params=tuple(t[1]) if t[1] else tuple(), args=tuple(t[2]))

    def gcall(self, t):
        return Call(name=t[0],
                    params=tuple(t[1]) if t[1] else tuple(),
                    args=tuple(Reference(name, None) for name in t[2]))

    def measure(self, t):
        return Measure(qubits=t[0], cbits=t[1])

    def ugate(self, t):
        return Call(name='U', params=tuple(t[0]), args=(t[1],))

    def ifstatement(self, t):
        return IfStatement(register=t[0], equals=t[1], qop=t[2])

    def reset(self, t):
        return Call(name="reset", params=tuple(), args=(t[0],))

    def qop(self, t):
        """We lookup references in the qubits and cbits table."""
        if isinstance(t, Measure):
            return Measure(qubits=tuple(self.from_reference(ref) for ref in t.qubits),
                           cbits=tuple(self.from_reference(ref) for ref in t.cbits))
        # Otherwise it has an .args field
        op = t[0]
        return op._replace(args=tuple(self.from_reference(ref) for ref in op.args))

    def cxgate(self, t):
        return Call(name='CX', params=tuple(), args=(t[0], t[1]))

    def barrier(self, t):
        return Call(name='barrier', params=tuple(), args=(t[0]))

    def gbarrier(self, t):
        return Call(name='barrier',
                    params=tuple(),
                    args=tuple(Reference(name, None) for name in t[0]))

    def include(self, t):
        return Include(path=Path(t[0]))

    def add(self, t):
        return Add(*t)

    def sub(self, t):
        return Sub(*t)

    def mul(self, t):
        return Mul(*t)

    def div(self, t):
        return Div(*t)

    def exponent(self, t):
        return Exponent(*t)

    def pi(self, t):
        return Pi()

    def reference(self, t):
        return Reference(t, None)

    def mathfunop(self, t):
        fun = t[0]
        if fun == "sin":
            fun = MathFun.Op.sin
        elif fun == "cos":
            fun = MathFun.Op.cos
        elif fun == "tan":
            fun = MathFun.Op.tan
        elif fun == "exp":
            fun = MathFun.Op.exp
        elif fun == "ln":
            fun = MathFun.Op.ln
        elif fun == "sqrt":
            fun = MathFun.Op.sqrt
        return fun

    def mathfun(self, t):
        return MathFun(*t)

    def neg(self, t):
        return Neg(*t)

    def start(self, t):
        return OpenQasmProgram(version=t[0],
                               statements=tuple(t[1:]),
                               qregs=self.qregs,
                               cregs=self.cregs)


class Exp:
    pass


class QregDecl(NamedTuple):
    qreg: QuantumRegister


class CregDecl(NamedTuple):
    creg: ClassicalRegister


class Call(NamedTuple):
    name: str
    params: Tuple[Exp, ...]
    args: Tuple[Union[QuantumRegister, Qubit], ...]


class GateDefinition(NamedTuple):
    id: str
    params: Tuple[Exp, ...]
    args: Tuple[Qubit, ...]
    body: Tuple[Call, ...]


class Measure(NamedTuple):
    qubits: Union[QuantumRegister, Qubit]
    cbits: Union[QuantumRegister, Qubit]


class IfStatement(NamedTuple):
    register: ClassicalRegister
    equals: int
    qop: Union[Call, Measure]


class Include(NamedTuple):
    path: Path


class Add(Exp, NamedTuple):
    left: Exp
    right: Exp


class Sub(Exp, NamedTuple):
    left: Exp
    right: Exp


class Mul(Exp, NamedTuple):
    left: Exp
    right: Exp


class Div(Exp, NamedTuple):
    numerator: Exp
    denominator: Exp


class Exponent(Exp, NamedTuple):
    base: Exp
    exponent: Exp


class Pi(Exp):
    def __repr__(self):
        return "Pi()"


class Neg(Exp, NamedTuple):
    exp: Exp


class MathFun(Exp, NamedTuple):
    class Op(Enum):
        sin = enum.auto()
        cos = enum.auto()
        tan = enum.auto()
        exp = enum.auto()
        ln = enum.auto()
        sqrt = enum.auto()

    fun: Op
    exp: Exp


class OpenQasmProgram(NamedTuple):
    version: float
    qregs: Dict[str, QuantumRegister]
    cregs: Dict[str, ClassicalRegister]
    statements: Tuple[Union[QregDecl, CregDecl, Call, GateDefinition, Measure], ...]
