from lark import Lark
from lark import Tree

#Définition de la grammaire
# s: symbole de départ
# IDENTIFIER : explicite à quoi ressemblent les noms de variables
# WS: caractères de retour à la ligne (pratique de les ignorer)
# le | (ou) permet de parser une chaîne de caractères vide
# -> vide / -> vars : nom des règles 

g = Lark("""
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9]*/ 
NUMBER: /[1-9][0-9]*/ | "0"
OPBIN: /[+\\-*><\\/]/ | "==" | "!="
    
liste_var:                           -> vide
    | IDENTIFIER ("," IDENTIFIER)*   -> vars

expression: IDENTIFIER               -> var
    | expression OPBIN expression    -> opbin
    | NUMBER                         -> number
         
commande: IDENTIFIER "=" expression                                          -> affectation
    | commande (";" commande)*                                                  -> sequence
    | "while" "(" expression ")" "{" commande "}"                                -> while
    | "if" "(" expression ")" "then" "{" commande "}" ("else" "{" commande "}")? -> ite
    | "printf" "(" expression ")" ";"                                            -> print
    | "skip"                                                                     -> skip
programme: "main" "(" liste_var ")" "{" commande "return" "(" expression ")" "}"
         
struct: "struct" IDENTIFIER "{" IDENTIFIER (";" IDENTIFIER)* "}" ";" -> struct
         
%import common.WS
%ignore WS 
""", start='struct')

op2asm = { '+': "add rax, rbx", 
          '-': "sub rax, rbx"}

#Assembly
def asm_expression(e) :
    if e.data == "var": return f"mov rax, [{e.children[0].value}]"
    if e.data == "number":  return f"mov rax, {e.children[0].value}"

    e_left = e.children[0]
    e_op = e.children[1]
    e_right = e.children[2]

    asm_left = asm_expression(e_left)
    asm_right = asm_expression(e_right)

    return f"""{asm_left}
push rax
{asm_right}
mov rbx, rax
pop rax
{op2asm[e_op.value]}"""

def asm_commande(c) :
    if c.data == "affectation" :
        var = c.children[0]
        exp = c.children[1]
        return f"""{asm_expression(exp)}
mov [{var}], rax"""
    elif c.data == "skip": return ""
    elif c.data == "print":
        exp = c.children[0]
        return f"""{asm_expression(exp)}
mov rdi, rax
xor rax, rax
mov rsi, fmt
call printf"""
    elif c.data == "while": 
        exp = c.children[0]
        body = c.children[1]
        return f"""at0: {asm_expression(exp)}
cmp rax, 0"""
    elif c.data == "sequence" :
        d = c.children[0]
        tail = c.children[1]
        return f"""{asm_commande(d)}
{asm_commande(tail)}"""
    elif c.data == "ite" :
        exp = c.children[0]
        body_if = c.children[1]
        body_else = c.children[2]
        return f"if ({pp_expression(exp)}) then {{\n{pp_commande(body_if)}}} \n else {{\n{pp_commande(body_else)}}}"
    return "--"

def asm_programme(p):
    with open("moule.asm") as f:
        prog_asm = f.read()
    ret = asm_expression(p.children[2])
    prog_asm = prog_asm.replace("RETOUR", ret)
    init_vars = ""
    decl_vars = ""
    for i, c in enumerate(p.children[0].children):
        init_vars += f"""mov rbx, [argv]
mov rdi, [rbx + {(i+1)*8}]
call atoi
mov [{c.value}], rax
"""
        decl_vars += f"{c.value}: dq 0\n"
    prog_asm = prog_asm.replace("INIT_VARS", init_vars)
    prog_asm = prog_asm.replace("DECL_VARS", decl_vars)
    asm_c = asm_commande(p.children[1])
    prog_asm = prog_asm.replace("COMMANDE", asm_c)
    return prog_asm


#pretty printer 

def pp_expression(e) :
    if e.data in ("var", "number") :
            return f"{e.children[0].value}"
    e_left = e.children[0]
    e_op = e.children[1]
    e_right = e.children[2]
    return f"{pp_expression(e_left)} {e_op.value} {pp_expression(e_right)}"

def pp_commande(c) :
    if c.data == "affectation" :
        var = c.children[0]
        exp = c.children[1]
        return f"{var.value} = {pp_expression(exp)}"
    elif c.data == "skip": return "skip"
    elif c.data == "print": return f"printf({pp_expression(c.children[0])})"
    elif c.data == "while": 
        exp = c.children[0]
        body = c.children[1]
        return f"while ({pp_expression(exp)}) {{\n{pp_commande(body)}\n}}"
    elif c.data == "sequence" :
        print('ok')
        d = c.children[0]
        print("d : ",d)
        tail = c.children[1]
        print("tail : ",tail)
        return f"{pp_commande(d)};\n{pp_commande(tail)}"
    elif c.data == "ite" :
        exp = c.children[0]
        body_if = c.children[1]
        body_else = c.children[2]
        return f"if ({pp_expression(exp)}) then {{\n{pp_commande(body_if)}\n}} else {{\n{pp_commande(body_else)}\n}}"
    return "--"

def pp_liste_vars(l) :
    res = f""
    for i in range(len(l.children)-1) :
        res += f"{l.children[i]},"
    res += f"{l.children[-1]}"
    return res


def pp_programme(p):
    vars = p.children[0]
    return f"main({pp_liste_vars(vars)}) {{\n{pp_commande(p.children[1])}\nreturn {pp_expression(p.children[2])}\n}}  "

def pp_struct(s): 
    name = s.children[0]
    return f"struct {name} {{\n }}"

if __name__ == "__main__" :
    with open("simple.c") as f :
        src = f.read()
    # ast = g.parse(src)
    # print(asm_programme(ast))
    ast = g.parse('struct point {x;y;z};')
    print(ast)
    print(pp_struct(ast))

