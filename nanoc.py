from lark import Lark
from lark import Tree, Token

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
TYPE_INT: "int"

         
type: TYPE_INT                       -> int
    | IDENTIFIER                     -> custom
    
liste_var:                           -> vide
    | IDENTIFIER                     -> var
    | IDENTIFIER "," liste_var       -> vars

liste_att:                           -> vide
    | type IDENTIFIER                -> att
    | type IDENTIFIER ";" liste_att  -> atts
         
liste_struct:                            -> vide
    | struct                             -> struct
    | struct liste_struct                -> structs
    
expression: IDENTIFIER               -> var
    | expression OPBIN expression    -> opbin
    | NUMBER                         -> number
         
lhs: IDENTIFIER                      -> variable
    | IDENTIFIER "." IDENTIFIER      -> acces_attribut 
         

commande: lhs "=" expression                                                    -> affectation
    | commande (";" commande)*                                                  -> sequence
    | "while" "(" expression ")" "{" commande "}"                                -> while
    | "if" "(" expression ")" "then" "{" commande "}" ("else" "{" commande "}")? -> ite
    | "printf" "(" expression ")" ";"                                            -> print
    | "skip"                                                                     -> skip
    | type IDENTIFIER                                                            -> declaration_struct
         
main: "main" "(" liste_var ")" "{" commande "return" "(" expression ")" "}" -> main
         
programme: liste_struct main
         
struct: "typedef struct" "{" liste_att "}" IDENTIFIER ";" -> struct
         
%import common.WS
%ignore WS 
""", start='programme')

op2asm = { '+': "add rax, rbx", 
          '-': "sub rax, rbx"}

# struct_symbol_table = {point: {x: 0, y: 8}, ligne: {p1_x: 0, p1_y: 8, p2_x: 16, p2_y: 24}}
struct_symbol_table = {}
var_symbol_table = {}




###########################################################################
########################      Assembly     ################################
###########################################################################



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




def asm_commande(c, current_offset) :
    if c.data == "affectation" :
        var = c.children[0]
        exp = c.children[1]
        return f"""{asm_expression(exp)}
mov [{var}], rax""", current_offset
    elif c.data == "skip": return ""
    elif c.data == "print":
        exp = c.children[0]
        return f"""{asm_expression(exp)}
mov rdi, rax
xor rax, rax
mov rsi, fmt
call printf""",current_offset
    elif c.data == "while": 
        exp = c.children[0]
        body = c.children[1]
        return f"""at0: {asm_expression(exp)}
cmp rax, 0""",current_offset
    elif c.data == "sequence" :
        d = c.children[0]
        tail = c.children[1]
        return f"""{asm_commande(d, current_offset)[0]}
{asm_commande(tail, current_offset)[0]}""",current_offset 
    elif c.data == "ite" :
        exp = c.children[0]
        body_if = c.children[1]
        body_else = c.children[2]
        # TODO : add ite
    elif c.data == "declaration_struct" :
        type = c.children[0].children[0].value
        size = len(struct_symbol_table[type])*8
        identifier = c.children[1].value
        var_symbol_table[identifier] = {"type": type, "off":current_offset}
        current_offset += size
        return f"""sub rsp, {size}""",current_offset
    return "--",current_offset



def init_atts(body, res, offset, symbol_table) :
    """create a dictionnary with the fields of a struct described by body and their offset from the address of the object of type struct"""
    if body.data == "vide":
        return res
    else:
        type_node = body.children[0]

        identifier = body.children[1]
        tail = body.children[2]

        if type_node.data == "int":
            res[identifier.value] = offset
            offset += 8  #each attribute is an 8-byte int
        else:
            type_name = type_node.children[0].value
            if type_name not in symbol_table:
                raise TypeError(f"type {type_name} undefined")
            else:
                sublayout = symbol_table[type_name]
                for field, suboffset in sublayout.items():
                    res[f"{identifier.value}.{field}"] = offset + suboffset
                offset += max(sublayout.values()) + 8  

        return init_atts(tail, res, offset, symbol_table)


def init_struct(s, symbol_table):
    body = s.children[0]
    name = s.children[1]
    symbol_table[name.value] = init_atts(body, {}, 0, symbol_table)
    return symbol_table
    


def init_struct_symbol_table(liste_structs, symbol_table):
    if liste_structs.data == "vide":
        return symbol_table
    elif liste_structs.data == "struct":
        return init_struct(liste_structs.children[0], symbol_table)
    else:
        tmp = init_struct(liste_structs.children[0], symbol_table)
        return init_struct_symbol_table(liste_structs.children[1], tmp)
    
def init_and_decl_vars(vars, i) :
    """Return the init_vars and decl_vars lists used in asm_programme.
       
       params :
         - vars : Tree representing the variables of main
         - i : current offset to find the address of the variable (x --> 8, y --> 16 , etc.)
    
    """

    if vars.data == "vide" :
        return "",""
    elif vars.data == "var" :
        var = vars.children[0]
        init_vars = f"""mov rbx, [argv]
mov rdi, [rbx + {(i+1)*8}]
call atoi
mov [{var.value}], rax """
        decl_vars = f"{var.value}: dq 0\n"
        return init_vars, decl_vars
    else :
        var = vars.children[0]
        tail = vars.children[1]
        init_vars_tail, decl_vars_tail = init_and_decl_vars(tail,i+1)
        init_vars = f"""mov rbx, [argv]
mov rdi, [rbx + {(i+1)*8}]
call atoi
mov [{var.value}], rax\n""" + init_vars_tail
        decl_vars = f"{var.value}: dq 0\n" + decl_vars_tail
        return init_vars, decl_vars
        

def asm_programme(p):
    # read moule.asm
    with open("moule.asm") as f:
        prog_asm = f.read()

    # separate code
    structs = p.children[0]
    main = p.children[1]

    #initialize struct symbol table
    init_struct_symbol_table(structs, struct_symbol_table)

    # return value 
    ret = asm_expression(main.children[2])
    prog_asm = prog_asm.replace("RETOUR", ret)

    #declare + initialize variables
    init_vars, decl_vars = init_and_decl_vars(main.children[0],0)
    prog_asm = prog_asm.replace("INIT_VARS", init_vars)
    prog_asm = prog_asm.replace("DECL_VARS", decl_vars)

    # assembly for commands
    current_offset = 0
    asm_c, current_offset = asm_commande(main.children[1],current_offset)
    print("heyyyyy : ",current_offset)
    asm_c += f"""\nadd rsp, {current_offset}""" #restore allocated stack space
    prog_asm = prog_asm.replace("COMMANDE", asm_c)

    return prog_asm





###########################################################
############   pretty printer    ##########################
###########################################################


def pp_expression(e) :
    if e.data in ("var", "number") :
        return f"{e.children[0].value}"
    e_left = e.children[0]
    e_op = e.children[1]
    e_right = e.children[2]
    return f"{pp_expression(e_left)} {e_op.value} {pp_expression(e_right)}"

def pp_lhs(lhs) :
    if lhs.data == "variable" :
        return f"{lhs.children[0].value}"
    elif lhs.data == "acces_attribut" :
        return f"{lhs.children[0].value}.{lhs.children[1].value}"

def pp_commande(c) :
    if c.data == "affectation" :
        lhs = c.children[0]
        exp = c.children[1]
        return f"{pp_lhs(lhs)} = {pp_expression(exp)}"
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
    elif c.data == "declaration_struct" :
        type = c.children[0]
        return f"{type.children[0]} {c.children[1].value}"
    return "--"


def pp_liste_vars(l) :
    if l.data == "vide" :
        return f""
    elif l.data == "var" :
        return f"{l.children[0]}"
    else :
        return f"{l.children[0]}, {pp_liste_vars(l.children[1])}"
    
    
def pp_liste_atts(l) :
    if l.data == "vide" :
        return f""
    # elif l.data == "att" :
    #     print(l.children)
    #     return f"{l.children[0]}"
    else :
        type = l.children[0]
        if type.data == "int" :
            identifier = l.children[1]
            tail = l.children[2]
            return f"int {identifier.value};\n{pp_liste_atts(tail)}"
        else :
            identifier = l.children[1]
            tail = l.children[2]
            return f"{type.children[0]} {identifier.value};\n{pp_liste_atts(tail)}"
    

def pp_main(m):
    return f"main({pp_liste_vars(m.children[0])}) {{\n{pp_commande(m.children[1])}\nreturn {pp_expression(m.children[2])}\n}}  "

def pp_struct(s): 
    name = s.children[1]
    body = s.children[0]
    return f"typedef struct {{\n{pp_liste_atts(body)}}} {name};"

def pp_liste_struct(l):
    if l.data == "vide" :
        return f""
    elif l.data == "struct" :
        return f"{pp_struct(l.children[0])}"
    else :
        return f"{pp_struct(l.children[0])}\n\n{pp_liste_struct(l.children[1])}"
    
def pp_programme(p):
    return f"{pp_liste_struct(p.children[0])}\n\n{pp_main(p.children[1])}"


if __name__ == "__main__" :
    with open("simple.c") as f :
        src = f.read()
    ast = g.parse(src)
    #print(ast)
    print("structs : ", f"{ast.children[0]}\n")
    print("main : ", f"{ast.children[1]}\n")
    main = ast.children[1]
    print("vars : ", f"{main.children[0]}\n")
    print("body : ", f"{main.children[1]}\n")
    print("return : ", f"{main.children[2]}\n")
    #print(asm_programme(ast))
    # print("body", ast.children[2])
    # print("return", ast.children[3])
    print(pp_programme(ast))
    
    structs = ast.children[0]
    #structs = Tree('struct', [Tree('struct', [Tree('atts', [Tree('custom', [Token('IDENTIFIER', 'Point')]), Token('IDENTIFIER', 'x'), Tree('atts', [Tree('custom', [Token('IDENTIFIER', 'Point')]), Token('IDENTIFIER', 'y'), Tree('vide', [])])]), Token('IDENTIFIER', 'Ligne')])])
    decl = Tree('declaration_struct', [Tree('custom', [Token('IDENTIFIER', 'Point')]), Token('IDENTIFIER', 'p')])
    init_struct_symbol_table(structs, struct_symbol_table)
    print(struct_symbol_table)
    print(asm_programme(ast))
    print(var_symbol_table)


