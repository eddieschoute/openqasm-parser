from pathlib import Path
from typing import NamedTuple, Any, List, Optional, Union
import enum
from enum import Enum
from decimal import Decimal

from lark import Transformer


class OpenQasmTransformer(Transformer):
    def nninteger(self, t):
        return int(t[0])

    def real(self, t):
        return Decimal(t[0])

    def id(self, t):
        return str(t[0])

    def argument(self, t):
        return Reference(id=t[0], index=t[1])

    def args(self, t):
        return t

    def idlist(self, t):
        return list(t)

    def explist(self, t):
        return list(t)

    def qregdecl(self, t):
        return QregDecl(id=t[0], size=t[1])

    def cregdecl(self, t):
        return CregDecl(id=t[0], size=t[1])

    def opaque(self, t):
        return Call(*t)

    def gbody(self, t):
        return t

    def gatedef(self, t):
        return GateDefinition(*t)

    def qcall(self, t):
        return Call(name=t[0], params=t[1] if t[1] else list(), args=t[2])

    def gcall(self, t):
        return Call(name=t[0], params=t[1] if t[1] else list(), args=[Reference(id=name, index=None) for name in t[2]])

    def measure(self, t):
        return Measure(qubits=t[0], cbits=t[1])

    def ugate(self, t):
        return Call(name='U', params=t[0], args=t[1])

    def ifstatement(self, t):
        return IfStatement(register=t[0], equals=t[1], qop=t[2])

    def cxgate(self, t):
        return Call(name='CX', params=list(), args=[t[0], t[1]])

    def barrier(self, t):
        return Call(name='barrier', params=list(), args=t)

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
        return Reference(id=t, index=None)

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
        return Neg(t)

    def start(self, t):
       return OpenQasmProgram(t[0], t[1:-1])


class Exp:
    pass


class QregDecl(NamedTuple):
    id: str
    size: int


class CregDecl(NamedTuple):
    id: str
    size: int


class Reference(NamedTuple):
    id: str
    index: Optional[int]

class Call(NamedTuple):
    name: str
    params: List[Exp]
    args: List[Reference]

class GateDefinition(NamedTuple):
    id: str
    params: List[Exp]
    args: List[Reference]
    body: List[Call]


class Measure(NamedTuple):
    qubits: Reference
    cbits: Reference


class IfStatement(NamedTuple):
    register: Reference
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
    statements: List[Union[QregDecl,CregDecl,Call, GateDefinition, Measure]]

