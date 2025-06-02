from lark import Lark


g=Lark("""
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9]*/
NUMBER: /[1-9][0-9]*/|"0"
OPBIN: /[+\-*\/>]/
WHILE: "while"
IF: "if"
ELSE: "else"
PRINT: "printf"
SKIP: "skip"
              
liste_var:                              -> vide
       |IDENTIFIER ("," IDENTIFIER)*    -> vars

expression: IDENTIFIER->var
        | expression OPBIN expression -> opbin
        | NUMBER -> number

commande: commande (";" commande)* -> sequence
       | "while" "(" expression ")" "{" commande "}" -> while
       | IDENTIFIER "=" expression -> affect
       | "if" "(" expression ")" "{" commande "}" ("else" "{" commande "}")? -> ite
       | "printf" "(" expression ")" -> print
       | "skip" -> skip

program: "main" "(" liste_var ")" "{" commande "return" "("expression")" "}" -> main

       %import common.WS
         %ignore WS
    """, start='program')



def pp_expression(e):
    if e.data in ["var", "number"]:
        return f"(e.children[0])"
    else:
        return f"({pp_expression(e.children[0])} {e.children[1]} {pp_expression(e.children[2])})"

def pp_command(c):
    if c.data=="affect":
        return f"{c.children[0]}={pp_expression(c.children[1])}"
    elif c.data=="skip":
        return "skip"
    elif c.data=="print":
        return f"print({pp_expression(c.children[0])})"
    elif c.data=="while":
        return f"while({pp_expression(c.children[0])}){{{pp_command(c.children[1])}}}"
    elif c.data=="ite":
        return f"if({pp_expression(c.children[0])}){{{pp_command(c.children[1])}}} else {{{pp_command(c.children[2])}}}"
    elif c.data=="sequence":
        return "; ".join([pp_command(c) for c in c.children])

def pp_program(p):
    return f"main({p.children[0]}){{{pp_command(p.children[1])}}} return {pp_expression(p.children[2])}"

op2asm={"+":"add rax, rbx","-":"sub rax, rbx",}

def asm_expression(e):
    if e.data =="var":return f"mov rax, [{e.children[0].value}]"
    if e.data=="number": return f"mov rax, {e.children[0].value}"
    asm_left=asm_expression(e.children[0])
    asm_right=asm_expression(e.children[2])
    return f"""{asm_left}
push rax
{asm_right}
mov rbx, rax
{op2asm[e.children[1].value]}"""

def asm_command(c):
    if c.data=="affect":
        return f"""
{asm_expression(c.children[1])}
mov {c.children[0]}, rax
"""
    elif c.data=="skip":
        return "nop"
    elif c.data=="print":
        return f"""{asm_expression(c.children[0])}
mov rdi, rax
mov rsi, format
xor rax, rax
call printf
"""
    elif c.data=="while":
        return f"""
debut: {asm_expression(c.children[0])}
cmp rax, 0
jz fin
{asm_command(c.children[1])}
jmp debut
fin: nop
"""
    elif c.data=="ite":
        return f"""
{asm_expression(c.children[0])}
cmp rax, 0
jz else
{asm_command(c.children[1])}
jmp fin
else:
    {asm_command(c.children[2])}
fin: nop
"""
    elif c.data=="sequence":
        return "\n".join([asm_command(c) for c in c.children])

def asm_program(p):
    with open("moule.asm") as f:
        prog_asm = f.read()
    ret=asm_expression(p.children[2])
    prog_asm=prog_asm.replace("RETOUR",ret)
    init_vars=""
    for i,c in enumerate(p.children[0].children):
        init_vars+=f"""mov rbx, [argv]
mov rdi, [rbx+{(i+1)*8}]
call atoi
mov [{c.value}], rax
"""
    prog_asm=prog_asm.replace("INIT_VARS",init_vars)
    return prog_asm


if __name__ == "__main__":
    #ast=g.parse("main() { x=10; y=2; while (x>y) {x=x-1} return (x) }") 
    #ast=g.parse("printf(x+3)")
    #ast=g.parse("if(x){y=y+1}else{y=y-2;x=x+1};x=x+5;printf(x+3)")
    #print(asm_command(ast))
    with open("simple.c") as f:
        src = f.read()
    ast=g.parse(src)
    print(pp_program(ast))
    print(asm_program(ast))
    