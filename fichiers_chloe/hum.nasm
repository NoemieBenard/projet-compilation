
extern printf, atoi
section .data
fmt:db "%d\n",0
hello: db 'h' 'e' "llo world:", 10, "%d", 10, 0
x: dd 42

global main
section .text
main: 
push rbp
mov rbx, [rsi+8]
mov rdi, rbx
call atoi
mov [x], rax

xor rax, rax
mov rdi, hello ; rdi = hello
mov rsi, 12; rsi = 12
mov rsi, [x]
add rsi, 5; rsi += 5
call printf
pop rbp
ret