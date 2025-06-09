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
mov rax, 1
push rax
mov rbx, X
pop rax
mov [rbx], rax          ;X vaut 1

 mov rax, X
push rax
mov rbx, Y
pop rax
mov [rbx], rax          ; Y vaut adresse de X

mov rdi, fmt_int
mov rsi, rax
xor rax, rax
call printf

 mov rax, 5             ; push 5 dans la pile
push rax
mov rax, [Y]            
push rax                ; push [Y] dans la pile
mov rax, 3
mov rbx, rax
pop rax                 ; pop
add rax, rbx            ; add [Y] et 3

mov rdi, fmt_int
mov rsi, rax
xor rax, rax
call printf

mov rbx, rax            ; on met le resultat (adresse) dans rbx
pop rax                 ; pop 5

mov rdi, fmt_int
mov rsi, rax
xor rax, rax
call printf

;CEST ICI QUIL Y A UN PB. ON ACCEDE A UN ENDROIT NON AUTHORISE
mov [rbx], rax          ; *(Y+3)=5



 mov rax, [Y] 
push rax                ; push [Y]
mov rax, 3
mov rbx, rax
pop rax                 ; pop
add rax, rbx            ; Y+3 dans rax

mov rax, [rax]          ;*(Y+3) dans rax*

push rax
mov rbx, Z
pop rax

mov [rbx], rax          ; [Z] = *(Y+3)
RETOUR:
mov rax, [Z]


mov rdi, fmt_int
mov rsi, rax
xor rax, rax
call printf

pop rbp
ret
