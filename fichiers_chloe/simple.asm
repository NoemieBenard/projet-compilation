extern printf, atoi

section .data

DECL_VARS:
x: dq 0
y: dq 0

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
mov [x], rax
mov rbx, [argv]
mov rdi, [rbx + 16]
call atoi
mov [y], rax

COMMANDE:
loop0:mov rax, [x]
cmp rax, 0
jz end0
mov rax, [x] 
push rax
mov rax, 1
mov rbx, rax
pop rax
sub rax, rbx
mov rbx, x
mov [rbx], rax
 mov rax, [y] 
push rax
mov rax, 1
mov rbx, rax
pop rax
add rax, rbx
mov rbx, y
mov [rbx], rax
jmp loop0
end0: nop

RETOUR:
mov rax, [y] 
push rax
mov rax, 1
mov rbx, rax
pop rax
add rax, rbx
mov rdi, fmt_int
mov rsi, rax
xor rax, rax
call printf

pop rbp
ret
