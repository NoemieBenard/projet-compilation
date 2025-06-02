extern printf, atoi

section .data

DECL_VARS:
p: dq 0
fmt_int: db "%d", 10, 0


global main
section .text

main:
push rbp

INIT_VARS:
COMMANDE:
RETOUR:


mov rbx, [p]
add rbx, 1
mov [p], rbx




mov rdi, fmt_int
mov rsi, [p]

call printf

pop rbp
ret