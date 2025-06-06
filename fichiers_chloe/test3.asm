extern printf, atoi

section .data

DECL_VARS:
X: dq 0
p: dq 0
fmt_int: db "%d", 10, 0


global main
section .text

main:
push rbp

INIT_VARS:
COMMANDE:
RETOUR:


mov rax, 32
mov [X], rax
mov rax, X
mov [p], rax
mov rax, 3
mov rbx, [p]
mov [rbx], rax



mov rdi, fmt_int
mov rsi, [X]

call printf

pop rbp
ret