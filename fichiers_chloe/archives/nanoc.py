from lark import Lark

#Définition de la grammaire
# s: symbole de départ
# IDENTIFIER : explicite à quoi ressemblent les noms de variables
# WS: caractères de retour à la ligne (pratique de les ignorer)
# le | (ou) permet de parser une chaîne de caractères vide
# -> vide / -> vars : nom des règles 

cpt = range(10000000)

g = Lark("""
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9]*/ 
NUMBER: /[1-9][0-9]*/ | "0"
OPBIN: /[+\-*>\/]/
    
liste_var:                           -> vide
    | IDENTIFIER ("," IDENTIFIER)*   -> vars

expression: IDENTIFIER                          -> var
    | expression OPBIN expression               -> opbin
    | NUMBER                                    -> number
    | "(" expression OPBIN expression ")"          -> expression_parenthesee
         
commande: IDENTIFIER "=" expression                                              -> affectation
    | commande (";" commande)*                                                   -> sequence
    | "while" "(" expression ")" "{" commande "}"                                -> while
    | "if" "(" expression ")" "then" "{" commande "}" ("else" "{" commande "}")? -> ite
    | "printf" "(" expression ")"                                                -> print
    | "skip"                                                                     -> skip
programme: "main" "(" liste_var ")" "{" commande "return" "(" expression ")" "}"
         
%import common.WS
%ignore WS 
""", start='programme')

def asm_expression(e):
    if e.data == "var": return f"mov, rax [{e.children[0].value}]"
    elif e.data == "number": return f"mov rax, {e.children[0].value}"
    e_left = e.children[0]
    e_op = e.children[1]
    e_right = e.children[2]
    asm_left = asm_expression(e_left)
    asm_right = asm_expression(e_right)
    return f"""{asm_left}
push rax
{asm_right}
mov rbx, rax
{op2asm[e_op.value]}"""


"""op2asm = """


def asm_commande(c):
    if c.data == "affectation": 
        var = c.children[0]
        exp = c.children[1]
        return f"{asm_expression(exp)}\nmov [{var.value}], rax"
    if c.data == "skip": return "nop"
    if c.data == "print": return f"""{asm_expression(c.children[0])}
mov rsi, fmt
mov rdi, rax
xor rax, rax
call printf"""
    if c.data == "while":
        exp = c.children[0]
        body = c.children[1]
        idx = next(cpt)
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
        return f"{asm_commande(d)}\n{asm_commande(tail)}"
    return("--")

def asm_programme(p):
    with open("moule.asm") as f:
        prog_asm = f.read()
    asm_expression(p.children[2])
    prog_asm = prog_asm.replace("RETOUR", ret)
    init_vars = ""
    decl_vars = ""
    for c in enumerate(p.children[0].children):
        init_vars += f"""mov rbx, [argv]
mov rdi, [rbx + {(i+1)*8}]
call atoi
mov [{c.value}], rax
"""
        decl_vars += f"{c.value}: dq 0\n"
        
    prog_asm = prog_asm.replace("INIT_VARS", init_vars)
    prog_asm = prog_asm.replace("DECL_VARS", decl_vars)
    asm_c = asm_commande(p.children)
    prog_asm = prog_asm.replace("COMMANDE", asm_c)


    return prog_asm

def get_vars_expression(e):
    pass

def get_vars_commande(c):
    pass



def pp_expression(e):
    if e.data in ("var","number"): return f"{e.children[0].value}"
    elif e.data == "expression_parenthesee":
        e_left = e.children[0]
        e_op = e.children[1]
        e_right = e.children[2]
        return f"({pp_expression(e_left)} {e_op.value} {pp_expression(e_right)})"
    e_left = e.children[0]
    e_op = e.children[1]
    e_right = e.children[2]
    return f"{pp_expression(e_left)} {e_op.value} {pp_expression(e_right)}"

def pp_commande(c):
    if c.data == "affectation":
        var = c.children[0]
        exp = c.children[1]
        return f"{var.value} = {pp_expression(exp)};"
    elif c.data == "skip": return "skip"
    elif c.data == "print": return f"printf({pp_expression(c.children[0])})"
    elif c.data == "while":
        exp = c.children[0]
        body = c.children[1]
        return f"while ({pp_expression(exp)}) {{{pp_commande(body)}}}"
    elif c.data == "sequence":
        d = c.children[0]
        tail = c.children[1]
        return f"{pp_commande(d)} ; {pp_commande(tail)}"
    return("--")



# ast = g.parse('kqlqsd, deux, trois')
# print(ast) #'s'
# print(ast.children) #[Token('IDENTIFIER', 'kqlqsd')]
# print(ast.children[0].type) #IDENTIFIER
# print(ast.children[0].value) #'kqlqsd'



if __name__ == "__main__" :
    with open("exemple.c") as f :
        src = f.read()
        ast = g.parse("x = 1")
        print(asm_programme(ast))
