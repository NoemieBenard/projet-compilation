from lark import Lark

cpt = 0
g = Lark("""
IDENTIFIER: /(?!malloc$)[a-zA-Z_][a-zA-Z0-9]*/
NUMBER: /[1-9][0-9]*/|"0" 
OPBIN: /[+\\-*\\/>]/
MALLOC: /malloc/

liste_var:                            -> vide
    | IDENTIFIER ("," IDENTIFIER)*    -> vars

expression: IDENTIFIER            -> var
    | expression OPBIN expression -> opbin     
    | NUMBER                      -> number                
    | "&"expression               -> adresse
    | "*"expression               -> valeur
    | "*("expression")"           -> valeur_par
        
lhs: IDENTIFIER                   -> var
    | "*"lhs                      -> pointeur
    | "*("expression")"           -> pointeur_par
         
commande: commande (";" commande)*                               -> sequence
    | "while" "(" expression ")" "{" commande "}"                -> while
    | lhs "=" expression                                         -> affectation
    |"if" "(" expression ")" "{" commande "}" "else" "{" commande "}" -> ite
    | "printf" "(" expression ")"                                        -> print
    | "skip"                                                             -> skip
    | lhs "=" rhs                                                  -> memoire
         
rhs: MALLOC"("NUMBER")"                        ->malloc
         
         
program:"main" "(" liste_var ")" "{"commande "return" "("expression")" "}"
         
%import common.WS
%ignore WS
""", start='program')



def get_vars_expression(e):
    pass

def get_vars_commande(c):
    pass

#definition discrete d'une fonction definie sur deux éléments
op2asm = {'+' : 'add rax, rbx', '-': 'sub rax, rbx'}


def asm_rhs(r):#met le résultat dans rax
    arg = r.children[1].value
    return f"""mov edi, {arg}
call malloc"""

def asm_lhs(l): #met l'adresse de ce qu'il faut changer dans rbx
    if l.data == "var": return f"mov rbx, {l.children[0].value}"
    if l.data == "pointeur": 
        compteur = 0 
        var = l.children[0]
        if var.data == "pointeur":
            
            while var.data == "pointeur": #je regarde si var.data est une valeur. le compteur compte toutes les étoiles en plus de la première
                compteur += 1
                var = var.children[0]
            char = f"mov rbx, [{var.children[0].value}]"
            for i in range(compteur):
                char += "\nmov rbx, [rbx]"
            return char
        else: return f"mov rbx, [{var.children[0].value}]"
    if l.data == "pointeur_par":
        return f"""{asm_expression(l.children[0])}
mov rbx, rax"""
   



def asm_expression(e):#met le resultat dans rax
    if e.data == "var": return f"mov rax, [{e.children[0].value}]"
    if e.data == "number": return f"mov rax, {e.children[0].value}"
    if e.data == "adresse":return f"mov rax, {e.children[0].children[0].value}"
    if e.data == "valeur": 
        compteur = 0 
        var = e.children[0]
        if var.data == "valeur":
            
            while var.data == "valeur": #je regarde si var.data est une valeur. le compteur compte toutes les étoiles en plus de la première
                compteur += 1
                var = var.children[0]
            char = f"mov rax, [{var.children[0].value}]\nmov rax, [rax]"
            for i in range(compteur):
                char += "\nmov rax, [rax]"
            return char
        else: return f"mov rax, [{var.children[0].value}]\nmov rax, [rax]"
    if e.data == "valeur_par":
        return f"""{asm_expression(e.children[0])}
mov rax, [rax]"""
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
        return f"""{asm_expression(exp)}
push rax
{asm_lhs(lhs)}
pop rax
mov [rbx], rax"""
    
    if c.data == "skip": return "nop"
    if c.data == "print": return f"""{asm_expression(c.children[0])}
mov rdi, fmt_int
mov rsi, rax
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

    if c.data == "ite":
        cond = c.children[0]  # Condition
        if_body = c.children[1]  # Bloc `if`
        else_body = c.children[2]  # Bloc `else`
        else_label = "else"
        end_label = "end_if"
        asm_else = f"{asm_commande(else_body)}" 
        return f"""
    {asm_expression(cond)}  ; Évalue la condition
    cmp rax, 0
    jz {else_label}
    {asm_commande(if_body)}  ; Bloc `if`
    jmp {end_label}
    {else_label}:
    {asm_else}  ; Bloc `else` (s'il existe)
    {end_label}:"""
    if c.data == "memoire":
        lhs = c.children[0]
        rhs = c.children[1]
        return f"""{asm_lhs(lhs)}
{asm_rhs(rhs)}
mov [rbx], rax"""


    return "e.data n'est pas une des options prévues"
    



def asm_program(p):
    with open("moule.asm") as f:
        prog_asm = f.read()
    ret = asm_expression(p.children[2])
    prog_asm = prog_asm.replace("RETOUR:","RETOUR:\n"+ret)
    init_vars = ""
    decl_vars = ""
    for i, c in enumerate(p.children[0].children):
        init_vars += f"""mov rbx, [argv]
mov rdi, [rbx + {(i+1)*8}]
call atoi
mov [{c.value}], rax
"""
        decl_vars += f"{c.value}: dq 0\n"
    prog_asm = prog_asm.replace("INIT_VARS:", "INIT_VARS:\n"+init_vars)
    prog_asm = prog_asm.replace("DECL_VARS:", "DECL_VARS:\n"+decl_vars)
    asm_c = asm_commande(p.children[1])
    prog_asm = prog_asm.replace("COMMANDE:", "COMMANDE:\n"+asm_c)
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
   with open("simple.c") as f:
        src = f.read()
        ast = g.parse(src)
        print(asm_program(ast))
       
