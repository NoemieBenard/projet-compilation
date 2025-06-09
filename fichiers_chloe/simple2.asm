extern printf, atoi, malloc

section .data

DECL_VARS:
W: dq 0
X: dq 0
Y: dq 0
Z: dq 0

argv: dq 0
fmt_int: db "%d", 10, 0

global main
section .text

main:
push rbp
mov [argv], rsi

INIT_VARS:
mov rbx, [argv]
mov rdi, [rbx + 8]
call atoi
mov [W], rax
mov rbx, [argv]
mov rdi, [rbx + 16]
call atoi
mov [X], rax
mov rbx, [argv]
mov rdi, [rbx + 24]
call atoi
mov [Y], rax
mov rbx, [argv]
mov rdi, [rbx + 32]
call atoi
mov [Z], rax

COMMANDE:
mov rbx, W
mov edi, 8
call malloc
mov [rbx], rax      ;la valeur de W c'est l'adresse du malloc

 mov rax, [W] 
push rax            ; adresse du malloc dans la pile
mov rax, 10000
mov rbx, rax
pop rax
add rax, rbx        ; adresse + 1000

mov rbx, X
mov [rbx], rax      ; X prend cette valeur

 mov rax, 6
mov rbx, [X]        ; rbx contient adresse+1000

mov [rbx], rax      ; cette adresse pointe maintenant vers 6

 mov rax, [X]       ; rax contient adresse+1000
mov rax, [rax]      ; rax contient 6
mov rbx, Y
mov [rbx], rax      ; valeur de Y = 6
RETOUR:
mov rax, [Y]


mov rdi, fmt_int
mov rsi, rax
xor rax, rax
call printf

pop rbp
ret
