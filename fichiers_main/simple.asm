extern printf, atoi

section .data

x: dq 0
y: dq 0

argv: dq 0
fmt_int:db "%d", 10, 0

global main
section .text

main:
push rbp 
mov [argv], rsi

mov rbx, [argv]
mov rdi, [rbx + 8]
call atoi
mov [x], rax
mov rbx, [argv]
mov rdi, [rbx + 16]
call atoi
mov [y], rax

at0: mov rax, [x]
cmp rax, 0
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
