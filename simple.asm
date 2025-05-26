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

mov rax, 0
mov [z], rax
mov rax, [x]
push rax
mov rax, [y]
mov rbx, rax
pop rax
add rax, rbx
push rax
mov rax, [z]
mov rbx, rax
pop rax
add rax, rbx

mov rdi, fmt_int
mov rsi, rax
xor rax, rax
call printf


pop rbp
ret