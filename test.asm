%macro print 2
    mov   eax, 4
    mov   ebx, 1
    mov   ecx, %1
    mov   edx, %2
    int   80h
%endmacro

section .data
    nl dw 10
	a db '10'
	b db '20'
    str_0 dw "B = "

section .bss

section .text
    global _start
_start:
    print str_0, 6
    print b, 2
    print nl, 1

exit:
    mov eax, 1
    mov ebx, 0
    int 80h
