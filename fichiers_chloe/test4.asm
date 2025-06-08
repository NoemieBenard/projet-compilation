extern printf, atoi

section .data

DECL_VARS:
X: dq 0
Y: dq 0
p: dq 0
fmt_int: db "%d", 10, 0


global main
section .text

main:
push rbp

INIT_VARS:
COMMANDE:
RETOUR:

loop0:mov rax, [X]
cmp rax, 0
jnz end0
mov rax, [X] 
push rax
mov rax, 1
mov rbx, rax
pop rax
sub rax, rbx
mov rbx, X
mov [rbx], rax

 mov rax, [Y] 
push rax
mov rax, 1
mov rbx, rax
pop rax
add rax, rbx
mov rbx, Y
mov [rbx], rax
jmp loop0
end0: nop



mov rdi, fmt_int
mov rsi, [X]

call printf

mov rdi, fmt_int
mov rsi, [Y]
call printf


pop rbp
ret