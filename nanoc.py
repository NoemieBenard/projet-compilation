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
FONCTION_NAME: /[a-zA-Z_][a-zA-Z0-9]*/
NUMBER: /[1-9][0-9]*/|"0" 
OPBIN: /[+\\-*\\/>]/
liste_var:                            -> vide
    | IDENTIFIER                      -> var
    | IDENTIFIER "," liste_var        -> vars
         
liste_expression:                     -> vide 
    | expression                      -> expression
    | expression "," liste_expression  -> expressions   
         
expression: IDENTIFIER            -> var
    | FONCTION_NAME "(" liste_expression ")"      -> appel
    | expression OPBIN expression -> opbin
    | NUMBER                      -> number
         
commande: commande (";" commande)*   -> sequence
    | "while" "(" expression ")" "{" commande "}" -> while
    | IDENTIFIER "=" expression              -> affectation   
    | "if" "(" expression ")" "{" commande "}" ("else" "{" commande "}")? -> ite
    | "printf" "(" expression ")"                -> print
    | "skip"                                  -> skip
         
fonction: FONCTION_NAME "(" liste_var ")" "{" commande "return" "(" expression ")" "}" -> fonction
         
program: "main" "(" liste_var ")" "{"commande "return" "("expression")" "}"  ->main
    | fonction program -> declar_fonction

%import common.WS
%ignore WS
         

""", start='program')

label_counter = 0

def new_label(base="label"):
    global label_counter
    label = f"{base}_{label_counter}"
    label_counter += 1
    return label

variables_counter = 0
def new_variable():
    global variables_counter
    variables_counter += 1
    return variables_counter


op2asm = { '+': "add rax, rbx", 
          '-': "sub rax, rbx"}

#Assembly
def asm_expression(e) :
    if e.data == "var": return f"mov rax, [{e.children[0].value}]"
    if e.data == "number":  return f"mov rax, {e.children[0].value}"
    if e.data == "opbin":
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
    if e.data == "appel":
        name = e.children[0].value
        args = e.children[1]
        ret = asm_liste_expression(args)
        ret += f"""call {name}
pop rax
"""
        return ret
            
def asm_liste_expression(l) :
    if l.data == "vide" : return ""
    if l.data == "expression" : 
        return f"{asm_expression(l.children[0])}\npush rax"
    if l.data == "expressions" :
        return f"""{asm_expression(l.children[0])}
{asm_liste_expression(l.children[1])}
push rax"""

def asm_commande(c) :

    if c.data == "affectation" :
        var = c.children[0]
        exp = c.children[1]
        return f"""{asm_expression(exp)}
mov [{var.value}], rax"""
    
    elif c.data == "skip": return "nop"

    elif c.data == "print":
        exp = c.children[0]
        return f"""{asm_expression(exp)}
mov rsi, fmt
mov rdi, rax
xor rax, rax
call printf
"""
    
    elif c.data == "while":
        cond = c.children[0]  # Condition
        body = c.children[1]  # Corps de la boucle
        start_label = new_label("while_start")
        end_label = new_label("while_end")
        return f"""{start_label}:{asm_expression(cond)}  ; Évalue la condition
cmp rax, 0
jz {end_label}
{asm_commande(body)}  ; Corps de la boucle
jmp {start_label}
{end_label}: nop
"""
    
    elif c.data == "sequence" :
        d = c.children[0]
        tail = c.children[1]
        return f"""{asm_commande(d)}
{asm_commande(tail)}"""
    
    elif c.data == "ite":
        cond = c.children[0]  # Condition
        if_body = c.children[1]  # Bloc `if`
        else_body = c.children[2] if len(c.children) > 2 else None  # Bloc `else`
        else_label = new_label("else")
        end_label = new_label("end_if")
        asm_else = f"{asm_commande(else_body)}" if else_body else ""
        return f"""
{asm_expression(cond)}  ; Évalue la condition
cmp rax, 0
je {else_label}
{asm_commande(if_body)}  ; Bloc `if`
jmp {end_label}
{else_label}:
{asm_else}  ; Bloc `else` (s'il existe)
{end_label}:
"""    
    return "--"

def asm_fonction(f):
    name = f.children[0].value  # Nom de la fonction
    args = f.children[1]  # Liste des arguments
    body = f.children[2]  # Corps de la fonction
    ret_expr = f.children[3]  # Expression de retour

    # Gérer les arguments
    arg_init = ""
    for i, arg in enumerate(args.children):
        reg = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"][i]
        arg_init += f"mov [{arg.value}], {reg}\n"

    return f"""
{name}:
push rbp
mov rbp, rsp
{arg_init}
{asm_commande(body)}
{asm_expression(ret_expr)}
mov rsp, rbp
pop rbp
ret
"""

def asm_liste_vars(l):

    init_vars = ""
    decl_vars = ""        

    if l.data == "vide": return ""

    else : 
        
        c = l.children[0]
        init_vars = f"""
mov rbx, [argv]
mov rdi, [rbx + {new_variable()*8}]
call atoi
mov [{c.value}], rax
"""
        decl_vars = f"{c.value}: dq 0\n"
        if l.data == "vars":
            # l.children[0] est une variable, l.children[1] est la liste des variables suivantes
            list_vars = l.children[1]
            temp_init, temp_decl = asm_liste_vars(list_vars)
            init_vars += temp_init
            decl_vars += temp_decl
    
    return init_vars, decl_vars

def asm_programme(p):

    with open("moule.asm") as f:
        prog_asm = f.read()

    init_vars, decl_vars = asm_liste_vars(p.children[0])

    commande = asm_commande(p.children[1])
    ret = asm_expression(p.children[2])

    prog_asm = prog_asm.replace("RETOUR", ret)
    prog_asm = prog_asm.replace("INIT_VARS", init_vars)
    prog_asm = prog_asm.replace("DECL_VARS", decl_vars)
    prog_asm = prog_asm.replace("COMMANDE", commande)

    return prog_asm


#pretty printer 
def pp_liste_expression(l) :
    if l.data == "vide" : return ""
    if l.data == "expression" : 
        return f"{pp_expression(l.children[0])}"
    if l.data == "expressions" :
        return f"{pp_expression(l.children[0])}, {pp_liste_expression(l.children[1])}"

def pp_expression(e) :
    if e.data in ("var", "number") :
            return f"{e.children[0].value}"
    if e.data == "appel" :
        name = e.children[0]
        args = e.children[1]
        return f"{name}({pp_liste_expression(args)})"
    if e.data == "opbin":
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
        d = c.children[0]
        tail = c.children[1]
        return f"{pp_commande(d)};\n{pp_commande(tail)}"
    elif c.data == "ite" :
        exp = c.children[0]
        body_if = c.children[1]
        body_else = c.children[2]
        return f"if ({pp_expression(exp)}) then {{\n{pp_commande(body_if)}\n}} else {{\n{pp_commande(body_else)}\n}}"
    return "--"

def pp_liste_vars(l) :
    if l.data == "vide" : return ""
    if l.data == "var" : 
        return f"{l.children[0].value}"
    if l.data == "vars" :
        return f"{l.children[0].value}, {pp_liste_vars(l.children[1])}"
       


def pp_fonction(f) :
    name = f.children[0]
    vars = f.children[1]
    commande = f.children[2]
    expression = f.children[3]
    return f"{name}({pp_liste_vars(vars)}) {{\n{pp_commande(commande)}\nreturn({pp_expression(expression)})\n}}"

def pp_programme(p):
    if p.data == "declar_fonction" :
        return f"{pp_fonction(p.children[0])}\n{pp_programme(p.children[1])}"
    if p.data == "main" :
        vars = p.children[0]
        commande = p.children[1]
        expression = p.children[2]
        return f"main({pp_liste_vars(vars)}) {{\n{pp_commande(commande)}\nreturn({pp_expression(expression)})\n}}"


if __name__ == "__main__" :
    with open("simple.c") as f :
        src = f.read()
    ast = g.parse(src)
    print(ast)

    asm_code = asm_programme(ast)
    print(asm_code)
    with open("simple.asm", "w") as f:
        f.write(asm_code)
    #print(pp_programme(ast))
    # ast = g.parse('while (x>2) {y = 3 - x}')
    # print(ast)
    # print(pp_commande(ast))
