extern printf, atoi, malloc

section .data

DECL_VARS:
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
mov [X], rax
mov rbx, [argv]
mov rdi, [rbx + 16]
call atoi
mov [Y], rax
mov rbx, [argv]
mov rdi, [rbx + 24]
call atoi
mov [Z], rax

COMMANDE:
mov rbx, Y
mov edi, 6
call malloc
mov [rbx], rax
 mov rax, 5
push rax
mov rax, [Y] 
push rax
mov rax, 3
mov rbx, rax
pop rax
add rax, rbx
mov rbx, rax
pop rax
mov [rbx], rax
 mov rax, [Y] 
push rax
mov rax, 3
mov rbx, rax
pop rax
add rax, rbx
mov rax, [rax]
push rax
mov rbx, Z
pop rax
mov [rbx], rax
RETOUR:
mov rax, [Z]


mov rdi, fmt_int
mov rsi, rax
xor rax, rax
call printf

pop rbp
ret
