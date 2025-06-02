from lark import Lark

cpt = 0
g = Lark("""
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9]*/
NUMBER: /[1-9][0-9]*/|"0" 
OPBIN: /[+\\-*\\/>]/

liste_var:                            -> vide
    | IDENTIFIER ("," IDENTIFIER)*    -> vars

expression: IDENTIFIER            -> var
    | expression OPBIN expression -> opbin     
    | NUMBER                      -> number                
    | "&"expression               -> adresse
    | "*"expression               -> valeur
lhs: IDENTIFIER                   -> var
    | "*"lhs                      -> pointeur
commande: commande (";" commande)*                -> sequence
    | "while" "(" expression ")" "{" commande "}" -> while
    | lhs "=" expression                   -> affectation
    |"if" "(" expression ")" "{" commande "}" ("else" "{" commande "}")? -> ite
    | "printf" "(" expression ")"                                        -> print
    | "skip"                                                             -> skip
program:"main" "(" liste_var ")" "{"commande"return" "("expression")" "}"
%import common.WS
%ignore WS
""", start='expression')


def get_vars_expression(e):
    pass

def get_vars_commande(c):
    pass

#definition discrete d'une fonction definie sur deux éléments
op2asm = {'+' : 'add rax, rbx', '-': 'sub rax, rbx'}



def asm_lhs(l):
    if l.data == "var": return f"mov rax, [{l.children[0].value}]"

    return    



def asm_expression(e):
    if e.data == "var": return f"mov rax, [{e.children[0].value}]"
    if e.data == "number": return f"mov rax, {e.children[0].value}"
    if e.data == "adresse":
        var = e.children[0]
        return f"lea rax, {var.children[0].value}"
    if e.data == "valeur": 
        var = e.children[0]
        return f"mov rax, [{var.children[0].value}]"

    e_left = e.children[0]
    e_op = e.children[1]
    e_right = e.children[2]
    asm_left = asm_expression(e_left)
    asm_right = asm_expression(e_right)
    #on suppose qu'a la fin de asm_left, le résultat est dans rax
    #on suppose qu'a la fin de asm_right, le resultat est dans rax
    return f"""{asm_left} 
push rax
{asm_right}
mov rbx, rax
pop rax
{op2asm[e_op.value]}"""



def asm_commande(c):
    global cpt
    if c.data == "affectation": 
        lhs = c.children[0]
        exp = c.children[1]
        return f"{asm_expression(exp)}\nmov [{lhs.value}], rax" #avant lhs c'était var
    if c.data == "skip": return "nop"
    if c.data == "print": return f"""{asm_expression(c.children[0])}
mov rsi, fmt
mov rdi, rax
xor rax, rax
call printf
"""
    if c.data == "while":
        exp = c.children[0]
        body = c.children[1]
        idx = cpt
        cpt += 1
        return f"""loop{idx}:{asm_expression(exp)}
cmp rax, 0
jz end{idx}
{asm_commande(body)}
jmp loop{idx}
end{idx}: nop
"""
    if c.data == "sequence":
        d = c.children[0]
        tail = c.children[1]
        return f"{asm_commande(d)}\n {asm_commande(tail)}"




def asm_program(p):
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


def pp_lhs(l):
    if l.data == "var": return f"{pp_expression(l)}"
    return f"*{pp_lhs(l.children[0])}"

def pp_expression(e):
    if e.data in ("var","number"): return f"{e.children[0].value}"
    if e.data == "valeur": return f"*{pp_expression(e.children[0])}"
    if e.data == "adresse": return f"&{pp_expression(e.children[0])}"
    e_left = e.children[0]
    e_op = e.children[1]
    e_right = e.children[2]
    return f"{pp_expression(e_left)} {e_op.value} {pp_expression(e_right)}" 

def pp_commande(c):
    if c.data == "affectation": 
        lhs = c.children[0]
        exp = c.children[1]
        return f"{pp_lhs(lhs)} = {pp_expression(exp)}"
    if c.data == "skip": return "skip"
    if c.data == "print": return f"printf({pp_expression(c.children[0])})"
    if c.data == "while":
        exp = c.children[0]
        body = c.children[1]
        return f"while ( {pp_expression(exp)} ) {{{pp_commande(body)}}}"
    if c.data == "sequence":
        d = c.children[0]
        tail = c.children[1]
        return f"{pp_commande(d)} ; {pp_commande(tail)}"
    
    
def pp_liste_vars(l) :
    return f"{l.children[0]}, {l.children[1]}"
    
def pp_programme(p):
    vars = p.children[0]
    return f"main({pp_liste_vars(vars)}) {{\n{pp_commande(p.children[1])}\nreturn {pp_expression(p.children[2])}\n}}  "
    



if __name__ == "__main__":
   # with open("simple.c") as f:
        #src = f.read()
    ast = g.parse("**p")
    #print(ast)
    print(asm_expression(ast))
    #print(pp_expression(ast))
    #print(pp_commande(ast))
    #print(pp_lhs(ast))
#print(ast.children)
#print(ast.children[0].type)
#print(ast.children[0].value)