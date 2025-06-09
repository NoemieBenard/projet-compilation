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
mov [rbx], rax
 mov rax, [W] 
push rax
mov rax, 10000
mov rbx, rax
pop rax
add rax, rbx
push rax
mov rbx, X
pop rax
mov [rbx], rax
 mov rax, 6
push rax
mov rbx, [X]
pop rax
mov [rbx], rax
 mov rax, [X]
mov rax, [rax]
push rax
mov rbx, Y
pop rax
mov [rbx], rax
RETOUR:
mov rax, [Y]


mov rdi, fmt_int
mov rsi, rax
xor rax, rax
call printf

pop rbp
ret
