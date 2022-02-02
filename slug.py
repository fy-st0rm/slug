import sys
import os

#TODO: [X] Create a proper parser
#TODO: [X] Proper error handling
#TODO: [ ] If statements
#TODO: [ ] implement functions 

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
MOD   = "%"
EQUAL = "="
OPERATOR = "operator"
operators = [EQUAL, PLUS, MINUS, MULT, DIV, MOD]

# Special keywords 
PRINT    = "print"
NEW_LINE = ","
IF       = "if"
THEN     = "then"
ELSE     = "else"
END      = "end"
KEYWORD  = "keyword"
keywords = [PRINT, NEW_LINE, IF, THEN, ELSE, END]

def error(token, msg):
	print(f"\033[91mError: {file}\033[0m:{str(token.row)}:{str(token.col)}: {msg}", file=sys.stderr)
	exit(1)

def is_float(val):
	try:
		float(val)
		return True
	except ValueError:
		return False

class Token:
	def __init__(self, name, value, row, col):
		self.name = name
		self.value = value
		self.row = row
		self.col = col
	
	def __repr__(self):
		return f"TOKEN({self.name}, {self.value})"

def split_by_delim(line):
	word = ""
	words = []
	i = 0
	col = 0
	str_start = False

	row = line[0] + 1
	line = line[1] 
	while i < len(line):
		ch = line[i]

		# Parsing the stings
		if ch == "\"":
			word += ch
			if str_start:
				str_start = False
				words.append((row, col, word))
				col += len(word) + 1
				word = ""
			else:
				str_start = True

		# Splitting according to the space or tab
		elif (ch == " " or ch == "\t" or ch == "\n") and not str_start:
			if word:
				words.append((row, col, word))
			col += len(word) + 1
			word = ""

		# Adding the character
		else:
			word += ch
		i += 1

	return words

def create_token(program, words):
	i = 0
	line = []

	# Removing the free spaces
	words = list(filter(bool, words))
	while i < len(words):
		row = words[i][0]
		col = words[i][1]
		word = words[i][2]

		if word in data_types:
			line.append(Token(DATA_TYPE, word, row, col))
		elif word in operators:
			line.append(Token(OPERATOR, word, row, col))
		elif word.isdigit():
			line.append(Token(INT, word, row, col))
		elif is_float(word):
			line.append(Token(FLOAT, word, row, col))
		elif word[0] == "\"" and word[-1] == "\"" and len(word) > 1:
			line.append(Token(STR, word, row, col))
		elif word in keywords:
			line.append(Token(KEYWORD, word, row, col))
		else:
			line.append(Token(WORD, word, row, col))
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
		elif op == MINUS:
			seg += f"    ;; {tok_a.value} - {tok_b.value}\n"
			seg += f"    mov rax, [{tok_a.value}]\n"
			if is_var:
				seg += f"    mov rbx, [{tok_b.value}]\n"
			else:
				seg += f"    mov rbx, {tok_b.value}\n"
			seg += f"    sub rax, rbx\n"
			seg += f"    mov [{tok_a.value}], rax\n\n"
			return seg
		elif op == MULT:
			seg += f"    ;; {tok_a.value} * {tok_b.value}\n"
			seg += f"    mov rax, [{tok_a.value}]\n"
			if is_var:
				seg += f"    mov rbx, [{tok_b.value}]\n"
			else:
				seg += f"    mov rbx, {tok_b.value}\n"
			seg += f"    mul rbx\n"
			seg += f"    mov [{tok_a.value}], rax\n\n"
			return seg
		elif op == DIV:
			seg += f"    ;; {tok_a.value} / {tok_b.value}\n"
			seg += f"    mov rax, [{tok_a.value}]\n"
			if is_var:
				seg += f"    mov rbx, [{tok_b.value}]\n"
			else:
				seg += f"    mov rbx, {tok_b.value}\n"
			seg += f"    div rbx\n"
			seg += f"    mov [{tok_a.value}], rax\n\n"
			return seg
		elif op == MOD:
			seg += f"    ;; {tok_a.value} % {tok_b.value}\n"
			seg += f"    mov rax, [{tok_a.value}]\n"
			if is_var:
				seg += f"    mov rbx, [{tok_b.value}]\n"
			else:
				seg += f"    mov rbx, {tok_b.value}\n"
			seg += f"    div rbx\n"
			seg += f"    mov [{tok_a.value}], rdx\n\n"
			return seg
	else:
		error(tok_a, f"Cannot perform \"{op}\" operation on \"{tok_a.name}\" and \"{tok_b.name}\"")
	return seg

def simulate_program(program):
	token = Token(None, None, 0, 0)
	error(token, "Simulation mode is not yet implemented.")
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
	print_func += "    push    rbp\n"
	print_func += "    mov     rbp, rsp\n"
	print_func += "    sub     rsp, 64\n"
	print_func += "    mov     DWORD   [rbp-52], edi\n"
	print_func += "    mov     QWORD   [rbp-8], 0\n"
	# print_func += "    mov     BYTE   [rbp-17], 10\n"
	print_func += "    mov     eax, DWORD   [rbp-52]\n"
	print_func += "    mov     DWORD   [rbp-12], eax\n"
	print_func += "    cmp     DWORD   [rbp-52], 0\n"
	print_func += "    jns     .L3\n"
	print_func += "    neg     DWORD   [rbp-52]\n"
	print_func += ".L3:\n"
	print_func += "    mov     edx, DWORD   [rbp-52]\n"
	print_func += "    movsx   rax, edx\n"
	print_func += "    imul    rax, rax, 1717986919\n"
	print_func += "    shr     rax, 32\n"
	print_func += "    sar     eax, 2\n"
	print_func += "    mov     esi, edx\n"
	print_func += "    sar     esi, 31\n"
	print_func += "    sub     eax, esi\n"
	print_func += "    mov     ecx, eax\n"
	print_func += "    mov     eax, ecx\n"
	print_func += "    sal     eax, 2\n"
	print_func += "    add     eax, ecx\n"
	print_func += "    add     eax, eax\n"
	print_func += "    mov     ecx, edx\n"
	print_func += "    sub     ecx, eax\n"
	print_func += "    mov     eax, ecx\n"
	print_func += "    lea     edx, [rax+48]\n"
	print_func += "    mov     eax, 31\n"
	print_func += "    sub     rax, QWORD   [rbp-8]\n"
	print_func += "    mov     BYTE   [rbp-48+rax], dl\n"
	print_func += "    mov     eax, DWORD   [rbp-52]\n"
	print_func += "    movsx   rdx, eax\n"
	print_func += "    imul    rdx, rdx, 1717986919\n"
	print_func += "    shr     rdx, 32\n"
	print_func += "    sar     edx, 2\n"
	print_func += "    sar     eax, 31\n"
	print_func += "    mov     ecx, eax\n"
	print_func += "    mov     eax, edx\n"
	print_func += "    sub     eax, ecx\n"
	print_func += "    mov     DWORD   [rbp-52], eax\n"
	print_func += "    add     QWORD   [rbp-8], 1\n"
	print_func += "    cmp     DWORD   [rbp-52], 0\n"
	print_func += "    jne     .L3\n"
	print_func += "    cmp     DWORD   [rbp-12], 0\n"
	print_func += "    jns     .L4\n"
	print_func += "    mov     eax, 31\n"
	print_func += "    sub     rax, QWORD   [rbp-8]\n"
	print_func += "    mov     BYTE   [rbp-48+rax], 45\n"
	print_func += "    add     QWORD   [rbp-8], 1\n"
	print_func += ".L4:\n"
	print_func += "    mov     eax, 32\n"
	print_func += "    sub     rax, QWORD   [rbp-8]\n"
	print_func += "    lea     rdx, [rbp-48]\n"
	print_func += "    lea     rcx, [rdx+rax]\n"
	print_func += "    mov     rax, QWORD   [rbp-8]\n"
	print_func += "    mov     rdx, rax\n"
	print_func += "    mov     rsi, rcx\n"
	print_func += "	   mov     rax, 1\n"
	print_func += "	   mov	   rdi, 1\n"
	print_func += "    syscall\n"
	print_func += "    nop\n"
	print_func += "    leave\n"
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
					if var_name.value not in var_stack:
						# Creating a new token for variable and saving it in the stack
						new_token = Token(type, var_name.value, token.row, token.col)
						var_stack.update({var_name.value: new_token})
						if type == INT or type == FLOAT:
							bss_segment += f"    {var_name.value}: resd 32\n"
						elif type == STR:
							data_segment += f"    {var_name.value}: dw "
					else:
						error(var_name, f"Redeclaration of variable \'{var_name.value}\'")
				else:
					error(var_name, f"Cannot create a variable with \'{var_name.name}\' token.")

			# When the token is operator
			elif token.name == OPERATOR:
				if token.value == EQUAL:
					var_name = line[lc - 1].value
					value    = line[lc + 1:]
					lc = len(line)

					# Checking if variable is declared or not
					if var_name not in var_stack:
						error(token, f"Variable \"{var_name}\" not defined.")

					if len(value) <= 0:
						error(token, f"Cannot leave the assignment value empty")

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
								error(val, f"Cannot assign \"{val.name}\" to variable with \"{var.name}\" data type.")

						# If the assigned value is a data
						elif val.name in data_types:
							if var.name == val.name:
								if val.name == INT or val.name == FLOAT:
									text_segment += f"    ;; {var.value} = {val.value}\n"
									text_segment += f"    mov dword [{var.value}], {val.value}\n"
								elif val.name == STR:
									data_segment += f"{val.value}\n"	
									data_segment += f"    {var.value}_len_6969 equ $ - {var.value}\n"
									str_cnt += 1
								vc += 1
							else:
								error(val, f"Cannot assign \"{val.name}\" to variable with \"{var.name}\" data type.")

						# If there is operators in the values
						elif val.value in operators:
							if vc + 1 == len(value) or vc == 0:
								error(val, f"\'{val.value}\' operator needs two operands")

							operand = value[vc + 1]
							vc += 2

							if operand.value in var_stack:
								text_segment += com_calc_op(val.value, var, var_stack[operand.value], True);
							else:
								text_segment += com_calc_op(val.value, var, operand, False);

			elif token.name == WORD:
				lc += 1

				if token.value not in var_stack:
					error(token, f"Undefined token \'{token.value}\'")

			elif token.name in KEYWORD:
				if token.value == PRINT:
					params = line[lc+1:]
					lc = len(line)
					param_idx = 0
					
					while param_idx < len(params):
						val = params[param_idx]
						
						if val.name in OPERATOR:
							error(val, "Cannot use operators in print functions")

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
							error(val, f"Unknown word \'{val.value}\'");
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
		code = list(enumerate(f.readlines()))
	
	program = []
	row = 1
	for line in code:
		words = split_by_delim(line) 
		create_token(program, words)
		row += 1
	
	print(program)
	if mode == "sim":
		simulate_program(program)
	elif mode == "com":
		compile_program(file, program)
