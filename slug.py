import os
import sys

#TODO: [ ] Properly implement equals operator
#TODO: [ ] Ability to pop things into the stack
#TODO: [ ] IF statements

WORD = "word"

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
ASSIGN = "="
EQUAL = "=="

OPERATOR = "operator"
operators = [ASSIGN, EQUAL, PLUS, MINUS, MULT, DIV, MOD]

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
	print(f"\033[91mError: {token.file}\033[0m:{str(token.row)}:{str(token.col)}: {msg}", file=sys.stderr)
	exit(1)

def is_float(val):
	try:
		float(val)
		return True
	except ValueError:
		return False

class Token:
	def __init__(self, name, value, row, col, file):
		self.name = name
		self.value = value
		self.row = row
		self.col = col
		self.file = file
	
	def __repr__(self):
		return f"TOKEN({self.name}, {self.value})"

def chop_word(line, file):
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
				words.append((row, col, word, file))
				col += len(word) + 1
				word = ""
			else:
				str_start = True

		# Splitting according to the space or tab
		elif (ch == " " or ch == "\t" or ch == "\n") and not str_start:
			if word:
				words.append((row, col, word, file))
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
		file = words[i][3]

		if word in data_types:
			line.append(Token(DATA_TYPE, word, row, col, file))
		elif word in operators:
			line.append(Token(OPERATOR, word, row, col, file))
		elif word.isdigit():
			line.append(Token(INT, word, row, col, file))
		elif is_float(word):
			line.append(Token(FLOAT, word, row, col, file))
		elif word[0] == "\"" and word[-1] == "\"" and len(word) > 1:
			line.append(Token(STR, word, row, col, file))
		elif word in keywords:
			line.append(Token(KEYWORD, word, row, col, file))
		else:
			line.append(Token(WORD, word, row, col, file))
		i += 1

	program.append(line)

class Slug:
	def __init__(self, file, program):
		self.file = file
		self.asm_file = file.strip(".slug") + ".asm"
		self.obj_file = file.strip(".slug") + ".o"
		self.exe_file = file.strip(".slug")
		self.program = program

		# Segments for assembly
		self.text_segment = ""
		self.bss_segment  = ""
		self.data_segment = ""
		self.exit_segment = ""

		# Stacks
		self.var_stack = {}
		self.line = []
		self.assigned_var = None

		# Counters
		self.prog_cnt = 0
		self.str_cnt  = 0
		self.token_cnt = 0
	
	def simulate(self):
		token = Token(None, None, 0, 0, self.file)
		error(token, "Simulation mode is not yet implemented.")

	""" Compilation instructions """
	def __create_var(self, type):
		token = self.line[self.token_cnt]
		variable = Token(type, token.value, token.row, token.col, token.file)

		# Checking if the variable is already declared
		if variable.value in self.var_stack:
			error(variable, f"Variable `{variable.value}` is already defined.")
		if token.name != WORD:
			error(token, f"Cannot create a variable with `{token.name}` token.")

		# Generating assembly
		if type == INT or type == FLOAT:
			self.bss_segment  += f"    {variable.value}: resd 32\n"
		elif type == STR:
			self.data_segment += f"    {variable.value}: dw "

		self.var_stack.update({variable.value: variable})
	
	def __assign_var(self, value):
		if self.assigned_var.name != value.name:
			error(value, f"Cannot assign `{value.name}` to the variable with `{self.assigned_var.name}` type.")
		
		if value.value not in self.var_stack:
			if value.name == INT or value.name == FLOAT:
				self.text_segment += f"    ;; {self.assigned_var.value} = {value.value}\n"
				self.text_segment += f"    mov dword [{self.assigned_var.value}], {value.value}\n"
			elif value.name == STR:
				self.data_segment += f"{value.value}\n"	
				self.data_segment += f"    {value.value}_len_6969 equ $ - {var.value}\n"
				self.str_cnt += 1
		else:
			self.text_segment += f"    ;; {self.assigned_var.value} = {value.value}\n"
			self.text_segment += f"    mov rax, [{value.value}]\n"
			self.text_segment += f"    mov [{self.assigned_var.value}], rax\n"
	
	""" Arthimetic operation """
	def __plus(self, tok_a, tok_b):
		type_a = type_b = None
		self.text_segment += f"    ;; {tok_a.value} + {tok_b.value}\n"

		# Copying the first data into register
		if tok_a.value in self.var_stack:
			self.text_segment += f"    mov rax, [{tok_a.value}]\n"
			type_a = self.var_stack[tok_a.value].name
		elif tok_a.name in data_types:
			self.text_segment += f"    mov rax, {tok_a.value}\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.value}` used for plus operation.")

		# Copying the second data into register
		if tok_b.value in self.var_stack:
			self.text_segment += f"    mov rbx, [{tok_b.value}]\n"
			type_b = self.var_stack[tok_b.value].name
		elif tok_b.name in data_types:
			self.text_segment += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.value}` used for plus operation.")

		# Adding them both
		self.text_segment += f"    add rax, rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.text_segment += f"    mov [{self.assigned_var.value}], rax\n"
		else:
			self.text_segment += f"    push rax\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `+` operation between types `{type_a}` and `{type_b}`.")

	def __minus(self, tok_a, tok_b):
		type_a = type_b = None
		self.text_segment += f"    ;; {tok_a.value} - {tok_b.value}\n"

		# Copying the first data into register
		if tok_a.value in self.var_stack:
			self.text_segment += f"    mov rax, [{tok_a.value}]\n"
			type_a = self.var_stack[tok_a.value].name
		elif tok_a.name in data_types:
			self.text_segment += f"    mov rax, {tok_a.value}\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.value}` used for minus operation.")

		# Copying the second data into register
		if tok_b.value in self.var_stack:
			self.text_segment += f"    mov rbx, [{tok_b.value}]\n"
			type_b = self.var_stack[tok_b.value].name
		elif tok_b.name in data_types:
			self.text_segment += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.value}` used for minus operation.")

		# Adding them both
		self.text_segment += f"    sub rax, rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.text_segment += f"    mov [{self.assigned_var.value}], rax\n"
		else:
			self.text_segment += f"    push rax\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `-` operation between types `{type_a}` and `{type_b}`.")

	def __mult(self, tok_a, tok_b):
		type_a = type_b = None
		self.text_segment += f"    ;; {tok_a.value} * {tok_b.value}\n"

		# Copying the first data into register
		if tok_a.value in self.var_stack:
			self.text_segment += f"    mov rax, [{tok_a.value}]\n"
			type_a = self.var_stack[tok_a.value].name
		elif tok_a.name in data_types:
			self.text_segment += f"    mov rax, {tok_a.value}\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.value}` used for multiply operation.")

		# Copying the second data into register
		if tok_b.value in self.var_stack:
			self.text_segment += f"    mov rbx, [{tok_b.value}]\n"
			type_b = self.var_stack[tok_b.value].name
		elif tok_b.name in data_types:
			self.text_segment += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.value}` used for multiply operation.")

		# Adding them both
		self.text_segment += f"    mul rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.text_segment += f"    mov [{self.assigned_var.value}], rax\n"
		else:
			self.text_segment += f"    push rax\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `*` operation between types `{type_a}` and `{type_b}`.")

	def __div(self, tok_a, tok_b):
		type_a = type_b = None
		self.text_segment += f"    ;; {tok_a.value} / {tok_b.value}\n"

		# Copying the first data into register
		if tok_a.value in self.var_stack:
			self.text_segment += f"    mov rax, [{tok_a.value}]\n"
			type_a = self.var_stack[tok_a.value].name
		elif tok_a.name in data_types:
			self.text_segment += f"    mov rax, {tok_a.value}\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.value}` used for divide operation.")

		# Copying the second data into register
		if tok_b.value in self.var_stack:
			self.text_segment += f"    mov rbx, [{tok_b.value}]\n"
			type_b = self.var_stack[tok_b.value].name
		elif tok_b.name in data_types:
			self.text_segment += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.value}` used for divide operation.")

		# Adding them both
		self.text_segment += f"    div rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.text_segment += f"    mov [{self.assigned_var.value}], rax\n"
		else:
			self.text_segment += f"    push rax\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `/` operation between types `{type_a}` and `{type_b}`.")

	def __mod(self, tok_a, tok_b):
		type_a = type_b = None
		self.text_segment += f"    ;; {tok_a.value} % {tok_b.value}\n"

		# Copying the first data into register
		if tok_a.value in self.var_stack:
			self.text_segment += f"    mov rax, [{tok_a.value}]\n"
			type_a = self.var_stack[tok_a.value].name
		elif tok_a.name in data_types:
			self.text_segment += f"    mov rax, {tok_a.value}\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.value}` used for modular division operation.")

		# Copying the second data into register
		if tok_b.value in self.var_stack:
			self.text_segment += f"    mov rbx, [{tok_b.value}]\n"
			type_b = self.var_stack[tok_b.value].name
		elif tok_b.name in data_types:
			self.text_segment += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.value}` used for modular division operation.")

		# Adding them both
		self.text_segment += f"    div rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.text_segment += f"    mov [{self.assigned_var.value}], rdx\n"
		else:
			self.text_segment += f"    push rdx\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `/` operation between types `{type_a}` and `{type_b}`.")

	def __equal(self, tok_a, tok_b):
		self.text_segment += f"    {tok_a.value} == {tok_b.value}\n"
		self.text_segment += f"    mov rcx, 0\n"
		self.text_segment += f"    mov rdx, 1\n"
		self.text_segment += f"    pop rax\n"
		self.text_segment += f"    pop rbx\n"
		self.text_semgnet += f"    cmp rax, rbx\n"
		self.text_segment += f"    cmove rcx, rdx\n"
		self.text_segment += f"    push rcx\n"
	
	""" Special keywords """
	def __print(self, params):
		param_idx = 0
		while param_idx < len(params):
			val = params[param_idx]
			
			if val.name in OPERATOR:
				error(val, "Cannot use operators in print functions")
			elif val.value == NEW_LINE:
				self.text_segment += f"    ;; Newline\n"
				self.text_segment += f"    puts nl, 1\n\n"
				param_idx += 1
			elif val.value in self.var_stack:
				var = self.var_stack[val.value]
				if var.name == INT or var.name == FLOAT:
					self.text_segment += f"    ;; print {var.value}\n"
					self.text_segment += f"    mov rax, [{var.value}]\n"
					self.text_segment += f"    push rax\n"
					self.text_segment += f"    pop rdi\n"
					self.text_segment += f"    call print\n\n"
				elif var.name == STR:
					self.text_segment += f"    ;; Puts {val.value}\n"
					self.text_segment += f"    puts {val.value}, {val.value}_len_6969\n\n"
				param_idx += 1
			elif val.name in data_types:
				if val.name == INT or val.name == FLOAT:
					self.text_segment += f"    ;; print {val.value}\n"
					self.text_segment += f"    mov rax, {val.value}\n"
					self.text_segment += f"    push rax\n"
					self.text_segment += f"    pop rdi\n"
					self.text_segment += f"    call print\n\n"
				elif val.name == STR:
					self.data_segment += f"    str_{self.str_cnt}: dw {val.value}\n"
					self.data_segment += f"    str_{self.str_cnt}_len_6969 equ $ - str_{self.str_cnt}\n"
	
					self.text_segment += f"    ;; Puts {val.value}\n"
					self.text_segment += f"    puts str_{self.str_cnt}, str_{self.str_cnt}_len_6969\n\n"
	
					self.str_cnt += 1
				param_idx += 1
			else:
				error(val, f"Unknown word \'{val.value}\'");

	def compile(self):
		self.data_segment  = "section .data\n"
		self.data_segment += "    nl dw 10\n"
		self.bss_segment   = "section .bss\n"

		self.text_segment  = "section .text\n"
		self.text_segment += "    global _start\n"
		self.text_segment += "_start:\n"

		self.exit_segment  =  "exit:\n"
		self.exit_segment += "    mov rax, 60\n"
		self.exit_segment += "    mov rdi, 0\n"
		self.exit_segment += "    syscall\n"

		while self.prog_cnt < len(self.program):
			self.line = self.program[self.prog_cnt]
			self.prog_cnt += 1
			self.token_cnt = 0
			self.assigned_var = None

			while self.token_cnt < len(self.line):
				token = self.line[self.token_cnt]

				if token.name == DATA_TYPE:
					self.token_cnt += 1
					self.__create_var(token.value) # Giving the data type to create variable

				elif token.name == WORD:
					self.token_cnt += 1
					if self.assigned_var:
						if token.value in self.var_stack:
							self.__assign_var(self.var_stack[token.value])
						else:
							error(token, f"Invalid syntax.")

				elif token.name in data_types:
					self.token_cnt += 1
					if self.assigned_var:
						self.__assign_var(token)	

				elif token.name == OPERATOR:
					if self.token_cnt + 1 == len(self.line):
						error(token, f"`{token.value}` operater requires two operand.")

					if token.value == ASSIGN:
						self.assigned_var = self.line[self.token_cnt - 1]
						if self.assigned_var.value not in self.var_stack:
							error(self.assigned_var, f"Undefined variable `{self.assigned_var.value}`.")

						self.assigned_var = self.var_stack[self.assigned_var.value]
						self.token_cnt += 1

					elif token.value == PLUS:
						tok_a = self.line[self.token_cnt - 1]
						tok_b = self.line[self.token_cnt + 1]
						self.token_cnt += 2
						if self.assigned_var:
							self.__plus(self.assigned_var, tok_b)
						else:
							self.__plus(tok_a, tok_b)

					elif token.value == MINUS:
						tok_a = self.line[self.token_cnt - 1]
						tok_b = self.line[self.token_cnt + 1]
						self.token_cnt += 2
						if self.assigned_var:
							self.__minus(self.assigned_var, tok_b)
						else:
							self.__minus(tok_a, tok_b)

					elif token.value == MULT:
						tok_a = self.line[self.token_cnt - 1]
						tok_b = self.line[self.token_cnt + 1]
						self.token_cnt += 2
						if self.assigned_var:
							self.__mult(self.assigned_var, tok_b)
						else:
							self.__mult(tok_a, tok_b)

					elif token.value == DIV:
						tok_a = self.line[self.token_cnt - 1]
						tok_b = self.line[self.token_cnt + 1]
						self.token_cnt += 2
						if self.assigned_var:
							self.__div(self.assigned_var, tok_b)
						else:
							self.__div(tok_a, tok_b)

					elif token.value == MOD:
						tok_a = self.line[self.token_cnt - 1]
						tok_b = self.line[self.token_cnt + 1]
						self.token_cnt += 2
						if self.assigned_var:
							self.__mod(self.assigned_var, tok_b)
						else:
							self.__mod(tok_a, tok_b)

					elif token.value == EQUAL:
						self.token_cnt += 1

				elif token.name == KEYWORD:
					print(token)
					if token.value == PRINT:
						params = self.line[self.token_cnt + 1:]
						self.token_cnt = len(self.line)
						self.__print(params)

					elif token.value == IF:
						self.token_cnt += 1

					elif token.value == THEN:
						self.token_cnt += 1

					elif token.value == ELSE:
						self.token_cnt += 1

					elif token.value == END:
						self.token_cnt += 1
		self.__save()
	
	def __save(self):
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

		# Writing into assembly file
		self.out_file = open(self.asm_file, "w")
		self.out_file.write(puts_macro)
		self.out_file.write("\n")
		self.out_file.write(print_func)
		self.out_file.write("\n")
		self.out_file.write(self.data_segment)
		self.out_file.write("\n")
		self.out_file.write(self.bss_segment)
		self.out_file.write("\n")
		self.out_file.write(self.text_segment)
		self.out_file.write("\n")
		self.out_file.write(self.exit_segment)
		self.out_file.close()

		# Compiling the program
		os.system(f"nasm -felf64 {self.asm_file}")
		os.system(f"ld -o {self.exe_file} {self.obj_file}")
		print(f"nasm -felf64 {self.asm_file}")
		print(f"ld -o {self.exe_file} {self.obj_file}")


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
		words = chop_word(line, file) 
		create_token(program, words)
		row += 1
	
	slug = Slug(file, program)
	if mode == "sim":
		slug.simulate()
	elif mode == "com":
		slug.compile()

