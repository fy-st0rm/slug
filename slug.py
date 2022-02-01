import sys
import os

#TODO: [ ] Properly parse the strings
#TODO: [ ] If statements

WORD = "word"
VAR = "variable"

# Data types
INT = "int"
STR = "str"
FLOAT = "float"
DATA_TYPE = "data_type"
data_types = [INT, STR, FLOAT]

# Operators
PLUS  = "+"
MINUS = "-"
MULT  = "*"
DIV   = "/"
EQUAL = "="
OPERATOR = "operator"
operators = [EQUAL, PLUS, MINUS, MULT, DIV]

# Special keywords 
PRINT = "print"
NEW_LINE = ","
KEYWORD = "keyword"
keywords = [PRINT, NEW_LINE]

def error(msg):
	assert False, msg

def is_float(val):
	try:
		float(val)
		return True
	except ValueError:
		return False

class Token:
	def __init__(self, name, value):
		self.name = name
		self.value = value
	
	def __repr__(self):
		return f"TOKEN({self.name}, {self.value})"

def create_token(program, words):
	i = 0
	line = []
	while i < len(words):
		if words[i] in data_types:
			line.append(Token(DATA_TYPE, words[i]))
		elif words[i] in operators:
			line.append(Token(OPERATOR, words[i]))
		elif words[i].isdigit():
			line.append(Token(INT, words[i]))
		elif is_float(words[i]):
			line.append(Token(FLOAT, words[i]))
		elif words[i][0] == "\"" and words[i][-1] == "\"" and len(words[i]) > 1:
			line.append(Token(STR, words[i]))
		elif words[i][0] == "\"":
			word = words[i] 
			i += 1
			word += " " + words[i]
			while word[-1] != "\"":
				i += 1
				word += " " + words[i]
			line.append(Token(STR, word))
		elif words[i] in keywords:
			line.append(Token(KEYWORD, words[i]))
		else:
			line.append(Token(WORD, words[i]))
		i += 1

	program.append(line)

def com_calc_op(op, tok_a, tok_b, is_var):
	seg = ""
	if tok_a.name == tok_b.name:
		if op == PLUS:
			seg += f"    ;; {tok_a.value} + {tok_b.value}\n"
			seg += f"    mov rax, [{tok_a.value}]\n"
			if is_var:
				seg += f"    mov rbx, [{tok_b.value}]\n"
			else:
				seg += f"    mov rbx, {tok_b.value}\n"
			seg += f"    add rax, rbx\n"
			seg += f"    mov [{tok_a.value}], rax\n\n"
			return seg
	else:
		error(f"Cannot perform \"{op}\" operation on \"{tok_a.name}\" and \"{tok_b.name}\"")


def simulate_program(program):
	pass

def compile_program(file_name, program):
	file_name = file_name.strip(".slug") + ".asm"
	obj_file = file_name.strip(".asm") + ".o"
	exe_file = file_name.strip(".asm")
	out_file = open(file_name, "w")

	# String print function
	puts_macro =  "%macro puts 2\n"
	puts_macro += "    mov   eax, 4\n"
	puts_macro += "    mov   ebx, 1\n"
	puts_macro += "    mov   ecx, %1\n"
	puts_macro += "    mov   edx, %2\n"
	puts_macro += "    int   80h\n"
	puts_macro += "%endmacro\n"

	# Function to print integers
	print_func  = "print:\n"
	print_func += "    mov     r9, -3689348814741910323\n"
	print_func += "    sub     rsp, 40\n"
	# print_func += "    mov     BYTE [rsp+31], 10\n"
	print_func += "    lea     rcx, [rsp+30]\n"
	print_func += ".L2:\n"
	print_func += "    mov     rax, rdi     \n"
	print_func += "    lea     r8, [rsp+32]\n"
	print_func += "    mul     r9\n"
	print_func += "    mov     rax, rdi\n"
	print_func += "    sub     r8, rcx\n"   
	print_func += "    shr     rdx, 3\n"    
	print_func += "    lea     rsi, [rdx+rdx*4]\n"
	print_func += "    add     rsi, rsi\n"
	print_func += "    sub     rax, rsi\n"
	print_func += "    add     eax, 48\n"  
	print_func += "    mov     BYTE [rcx], al\n"
	print_func += "    mov     rax, rdi\n"
	print_func += "    mov     rdi, rdx\n"
	print_func += "    mov     rdx, rcx\n"
	print_func += "    sub     rcx, 1\n"
	print_func += "    cmp     rax, 9\n"
	print_func += "    ja      .L2\n"
	print_func += "    lea     rax, [rsp+32]\n"
	print_func += "    mov     edi, 1\n"
	print_func += "    sub     rdx, rax\n"
	print_func += "    xor     eax, eax\n"
	print_func += "    lea     rsi, [rsp+32+rdx]\n"
	print_func += "    mov     rdx, r8\n"
	print_func += "    mov     rax, 1\n"
	print_func += "    syscall\n"
	print_func += "    add     rsp, 40\n"
	print_func += "    mov rax, [rsp + 32 + rdx]\n"
	print_func += "    ret\n"

	data_segment  = "section .data\n"
	data_segment += "    nl dw 10\n"
	bss_segment   = "section .bss\n"

	text_segment  = "section .text\n"
	text_segment += "    global _start\n"
	text_segment += "_start:\n"

	exit_segment  =  "exit:\n"
	exit_segment += "    mov rax, 60\n"
	exit_segment += "    mov rdi, 0\n"
	exit_segment += "    syscall\n"

	pc = 0
	str_cnt = 0
	var_stack = {}
	while pc < len(program):
		line = program[pc]
		lc = 0

		while lc < len(line):
			token = line[lc] 

			# When the token is a data type
			if token.name == DATA_TYPE:
				type = token.value
				var_name = line[lc + 1] 
				lc += 2

				if var_name.name == WORD:
					# Creating a new token for variable and saving it in the stack
					new_token = Token(type, var_name.value)
					var_stack.update({var_name.value: new_token})
					if type == INT or type == FLOAT:
						bss_segment += f"    {var_name.value}: resb 32\n"
					elif type == STR:
						data_segment += f"    {var_name.value}: dw "
				else:
					error(f"Cannot create a variable with \'{var_name.name}\' token.")

			# When the token is operator
			elif token.name == OPERATOR:
				if token.value == EQUAL:
					var_name = line[lc - 1].value
					value    = line[lc + 1:]
					lc = len(line)

					# Checking if variable is declared or not
					if var_name not in var_stack:
						error(f"Variable \"{var_name}\" not defined.")

					if len(value) <= 0:
						error(f"Cannot leave the assignment value empty")

					# Going through the value
					vc = 0
					var = var_stack[var_name]
					while vc < len(value):
						val = value[vc]

						# If assigned value is a variable
						if val.value in var_stack:
							new_val = var_stack[val.value]
							if var.name == new_val.name:
								text_segment += f"    ;; {var_name} = {new_val.value}\n"
								text_segment += f"    mov rax, [{new_val.value}]\n"
								text_segment += f"    mov [{var_name}], rax\n\n"
								vc +=  1
							else:
								error(f"Cannot assign \"{val.name}\" to variable with \"{var.name}\" data type.")

						# If the assigned value is a data
						elif val.name in data_types:
							if var.name == val.name:
								if val.name == INT or val.name == FLOAT:
									text_segment += f"    ;; {var.value} = {val.value}\n"
									text_segment += f"    mov byte [{var.value}], {val.value}\n"
								elif val.name == STR:
									data_segment += f"{val.value}\n"	
									data_segment += f"    {var.value}_len_6969 equ $ - {var.value}\n"
									str_cnt += 1
								vc += 1
							else:
								error(f"Cannot assign \"{val.name}\" to variable with \"{var.name}\" data type.")

						# If there is operators in the values
						elif val.value == PLUS:
							if vc + 1 == len(value):
								error("Plus operator needs operands")
							operand = value[vc + 1]
							vc += 2

							if operand.value in var_stack:
								text_segment += com_calc_op(val.value, var, var_stack[operand.value], True);
							else:
								text_segment += com_calc_op(val.value, var, operand, False);

			elif token.name in KEYWORD:
				if token.value == PRINT:
					params = line[lc+1:]
					lc = len(line)
					param_idx = 0
					
					while param_idx < len(params):
						val = params[param_idx]
						
						if val.name in OPERATOR:
							error("Cannot use operators in print functions")

						elif val.value == NEW_LINE:
							text_segment += f"    ;; Newline\n"
							text_segment += f"    puts nl, 1\n\n"
							param_idx += 1
						elif val.value in var_stack:
							var = var_stack[val.value]
							if var.name == INT or var.name == FLOAT:
								text_segment += f"    ;; print {var.value}\n"
								text_segment += f"    mov rax, [{var.value}]\n"
								text_segment += f"    push rax\n"
								text_segment += f"    pop rdi\n"
								text_segment += f"    call print\n\n"
							elif var.name == STR:
								text_segment += f"    ;; Puts {val.value}\n"
								text_segment += f"    puts {val.value}, {val.value}_len_6969\n\n"
							param_idx += 1
						elif val.name in data_types:
							if val.name == INT or val.name == FLOAT:
								text_segment += f"    ;; print {val.value}\n"
								text_segment += f"    mov rax, {val.value}\n"
								text_segment += f"    push rax\n"
								text_segment += f"    pop rdi\n"
								text_segment += f"    call print\n\n"
							elif val.name == STR:
								data_segment += f"    str_{str_cnt}: dw {val.value}\n"
								data_segment += f"    str_{str_cnt}_len_6969 equ $ - str_{str_cnt}\n"

								text_segment += f"    ;; Puts {val.value}\n"
								text_segment += f"    puts str_{str_cnt}, str_{str_cnt}_len_6969\n\n"

								str_cnt += 1
							param_idx += 1
						else:
							error(f"Unknown word \'{val.value}\'");

		pc += 1
	
	out_file.write(puts_macro)
	out_file.write("\n")
	out_file.write(print_func)
	out_file.write("\n")
	out_file.write(data_segment)
	out_file.write("\n")
	out_file.write(bss_segment)
	out_file.write("\n")
	out_file.write(text_segment)
	out_file.write("\n")
	out_file.write(exit_segment)

	out_file.close()

	# Compiling the program
	os.system(f"nasm -felf64 {file_name}")
	os.system(f"ld -o {exe_file} {obj_file}")
	print(f"nasm -felf64 {file_name}")
	print(f"ld -o {exe_file} {obj_file}")

def usage():
	print("Usage: slug [mode] [file_name]")
	print("mode:  sim   --- simulates program")
	print("       com   --- compiles  program")

if __name__ == "__main__":
	if len(sys.argv) <= 2:
		usage()
		exit(1)

	mode = sys.argv[1]
	file = sys.argv[2]
	with open(file, "r") as f:
		code = f.readlines()
	
	program = []
	for line in code:
		words = line.split()
		create_token(program, words)
	
	if mode == "com":
		compile_program(file, program)
