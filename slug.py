#!/bin/python
import os
import sys

#TODO: [ ] Introduce arrays
#TODO: [ ] Introduce the characters and make strings as like it does in the C
#TODO: [ ] Deal with strings ( Assignment, Join strings, read characters, remove characters, comparable )
#TODO: [ ] Deal with floating point numbers

WORD = "word"
COMMENT = "#"

# Data types
INT = "int"
INT_ARR = "int*"
STR = "str"
FLOAT = "float"
CHAR = "char"
VOID = "void"
DATA_TYPE = "data_type"
data_types = [INT, STR, FLOAT, VOID]

# Operators
PLUS     = "+"
MINUS    = "-"
MULT     = "*"
DIV      = "/"
MOD      = "%"
ASSIGN   = "="
PLUS_EQ  = "+="
MINUS_EQ = "-="
MULT_EQ  = "*="
DIV_EQ   = "/="
MOD_EQ   = "%="
INC      = "++"
DEC		 = "--"

OPERATOR = "operator"
operators = [ASSIGN, PLUS, MINUS, MULT, DIV, MOD, PLUS_EQ, MINUS_EQ, MULT_EQ, DIV_EQ, MOD_EQ, INC, DEC]

# Conditions
LT     = "<"
GT     = ">"
EQUAL  = "=="
LTE    = "<="
GTE    = ">="
NT     = "!="

CONDITION = "condition"
conditions = [LT, GT, EQUAL, LTE, GTE, NT]

# Special keywords 
NEW_LINE = ","
IF       = "if"
THEN     = "then"
ELSE     = "else"
END      = "end"
WHILE	 = "while"
DO		 = "do"
FUNC     = "func"
IN       = "in"
PARAM    = ":"
RET_TYPE = "->"
RETURN   = "return"
BRACK_OPEN = "("
BRACK_CLOSE = ")"
KEYWORD  = "keyword"
keywords = [NEW_LINE, IF, THEN, ELSE, END, WHILE, DO, FUNC, IN, PARAM, RET_TYPE, RETURN, BRACK_OPEN, BRACK_CLOSE]

# Intrinsics
PRINT      = "print"
DEFINE     = "%define"
INCLUDE    = "include"
SYSCALL1   = "syscall1"
SYSCALL2   = "syscall2"
SYSCALL3   = "syscall3"
SYSCALL4   = "syscall4"
SYSCALL5   = "syscall5"
SYSCALL6   = "syscall6"
SYSCALL7   = "syscall7"
INTRINSIC  = "intrinsic"
intrinsics = [PRINT, DEFINE, INCLUDE, SYSCALL1, SYSCALL2, SYSCALL3, SYSCALL4, SYSCALL5, SYSCALL6, SYSCALL7]


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
	def __init__(self, name, id, value, row, col, file):
		self.name = name		# Type of the token eg (WORD, DATATYPE, KEYWORD, INT, STR)
		self.id = id			# Name of the token especially variables defined by the user
		self.value = value		# Name of the token especially variables in assembly space
		self.row = row
		self.col = col
		self.file = file

	def __repr__(self):
		return f"TOKEN({self.name}, {self.value})"

class Scope:
	def __init__(self, id, start, end):
		self.id = id			# Index of the scope in a scope stack
		self.start = start		# Start flag of the scope
		self.end = end			# End flag of the scope
		self.vars = []			# Variables declared inside of this scope (Variable names)
	
	def __repr__(self):
		return f"Scope: {self.id}"

class Addr:
	def __init__(self, type, name, id, start, end):
		self.type = type		# Types like (FUNC, IF, WHILE)
		self.name = name		# Name of the address
		self.id = id			# index in the addr stack
		self.start = start		# Start flag of the addr
		self.end = end			# End flag of the addr
	
	def __repr__(self):
		return f"Addr({self.type}: {self.id}, {self.start}, {self.end})"

class Func:
	def __init__(self, name, id, params, ret_type, row, col, file):
		self.name = name			# Name of the function defined by the user and is used to store in func_stack
		self.id = id				# Actual identity of the function in assembly level
		self.params = params		# List of tokens of the types that is used in the parameter
		self.ret_type = ret_type	# Datatype to be returned by this function
		self.ret_var = None			# Used when this function returns a value to a variable
		self.row = row
		self.col = col
		self.file = file
	
	def __repr__(self):
		return f"Func: {self.name} : {self.params} -> {self.ret_type}"

def chop_word(line, file):
	word = ""
	words = []

	str_start = False

	row = line[0] + 1
	col = 1
	line = line[1] 

	# Delimeter to chop the word from apart from spaces and tabs
	i = 0
	delim = [BRACK_OPEN, BRACK_CLOSE, COMMENT]
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
		elif (ch == " " or ch == "\t" or ch == "\n" ) and not str_start:
			if word:
				words.append((row, col, word, file))
			col += len(word) + 1
			word = ""

		# Splitting according to the delimeter
		elif ch in delim and not str_start:
			if word:
				words.append((row, col, word, file))
			col += len(word)
			words.append((row, col, ch, file))
			col += 1
			word = ""

		# Adding the character
		else:
			word += ch
		i += 1

	return words

def create_token(program, words):
	i = 0
	line = []
	cmt_start = False

	# Removing the free spaces
	words = list(filter(bool, words))
	while i < len(words):
		row  = words[i][0]
		col  = words[i][1]
		word = words[i][2]
		file = words[i][3]

		if cmt_start:
			line.append(Token(COMMENT, word, word, row, col, file))
		elif word in data_types:
			line.append(Token(DATA_TYPE, word, word, row, col, file))
		elif word in operators:
			line.append(Token(OPERATOR, word, word, row, col, file))
		elif word in conditions:
			line.append(Token(CONDITION, word, word, row, col, file))
		elif word.isdigit():
			line.append(Token(INT, word, word, row, col, file))
		elif is_float(word):
			line.append(Token(FLOAT, word, word, row, col, file))
		elif word[0] == "\"" and word[-1] == "\"" and len(word) > 1:
			line.append(Token(STR, word, word, row, col, file))
		elif word in keywords:
			line.append(Token(KEYWORD, word, word, row, col, file))
		elif word in intrinsics:
			line.append(Token(INTRINSIC, word, word, row, col, file))
		elif word == COMMENT:
			line.append(Token(COMMENT, word, word, row, col, file))
			cmt_start = True
		else:
			line.append(Token(WORD, word, word, row, col, file))
		i += 1

	program.append(line)

def lex_file(file):
	with open(file, "r") as f:
		code = list(enumerate(f.readlines()))
	
	program = []
	row = 1
	for line in code:
		words = chop_word(line, file) 
		create_token(program, words)
		row += 1
	return program


class Slug:
	def __init__(self, file, program):
		# File names
		self.file = os.path.abspath(file)
		self.asm_file = file.strip(".slug") + ".asm"
		self.obj_file = file.strip(".slug") + ".o"
		self.exe_file = file.strip(".slug")

		# Stores the tokens of the program
		self.program = program

		# Segments for assembly
		self.segments = {
				"text"  : "", 
				"bss"   : "", 
				"data"  : "", 
				"exit"  : "", 
				"func"  : "", 
				"define": ""
		}
		self.curr_segment = ["text"]

		# Stacks
		self.scopes        = []				# Scope stack
		self.line		   = []				# Holds the tokens of the current line
		self.addr_stack    = []				# Address stack
		self.called_func   = []				# Holds the function that was called
		self.curr_func     = []				# Holds the current function addr 
		self.var_stack     = {}				# Variable stack
		self.func_stack    = {}				# Function stack
		self.include_files = [self.file]	# Included files stack
		self.ret_stack = 0					# Counts the values that were returned by a function

		# Flags
		self.assigned_var = None			# Stores the variable that was in a assigned state i.e a = 10 where a is a assigned var
		self.con_var      = None			# Points to the variable that stores the values from the condition 
		self.operation    = None			# It stores a function pointer of an operation to be conducted

		# Counters
		self.prog_cnt  = 0					# Points to the current position in the program (NOTE: program is an 2D array that means prog_cnt can also be called line_cnt)
		self.str_cnt   = 0					# Counts the total number of strings that were used in the program
		self.token_cnt = 0					# Current index of token in a current line
		self.addr_cnt  = -1					# Holds the current address we are on
		self.local_var_cnt = 0				# Holds memory offset of local variables
	
	def simulate(self):
		token = Token(None, None, None, 0, 0, self.file)
		error(token, "Simulation mode is not implemented yet.")

	""" Compilation instructions """
	def __start_scope(self):
		new_scope = Scope(len(self.scopes), True, False)
		self.scopes.append(new_scope)
		self.curr_scope = new_scope

	def __end_scope(self):
		self.curr_scope.end = True
		self.local_var_cnt -= len(self.curr_scope.vars) * 8
		if self.local_var_cnt < 0: self.local_var_cnt = 0

		for i in self.curr_scope.vars:
			self.var_stack.pop(i)

		for i in range(self.ret_stack):
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		self.ret_stack = 0

		# Gives the previous scope
		for i in range(len(self.scopes) - 1, -1, -1):
			self.curr_scope = self.scopes[i]
			if not self.curr_scope.end:
				break

	def __create_var(self, type):
		token = self.line[self.token_cnt]
		self.token_cnt += 1

		variable = Token(type, token.value, token.value, token.row, token.col, token.file)
		variable.id = token.value

		# Checking if the variable is already declared
		if variable.value in self.var_stack:
			error(variable, f"Variable `{variable.value}` is already defined.")
		if token.name != WORD:
			error(token, f"Cannot create a variable with `{token.value}` token.")

		# Generating assembly
		if self.curr_scope.id == 0:
			if type == INT or type == FLOAT:
				self.segments["bss"]  += f"    __{variable.value}__: resd 32\n"
				variable.value = f"[__{variable.value}__]"
			elif type == STR:
				self.segments["data"] += f"    __{variable.value}__: dw "
				variable.value = f"__{variable.value}__"
		else:
			if type == INT or type == FLOAT:
				variable.value = f"[rbp - {self.local_var_cnt + 8}]"
				self.local_var_cnt += 8
			elif type == STR:
				variable.value = f"str_{self.str_cnt}"
			self.curr_scope.vars.append(variable.id)
		
		self.var_stack.update({variable.id : variable})
	
	def __assign_var(self, value):
		# If the assigned value is itself then return
		if self.assigned_var.name == value.value:
			return 

		if self.assigned_var.name != value.name:
			error(value, f"Cannot assign `{value.id}` to the variable with `{self.assigned_var.id}` type.")

		if value.id not in self.var_stack:
			if value.name == INT or value.name == FLOAT:
				self.segments[self.curr_segment[-1]] += f"    ;; {self.assigned_var.id} = {value.id}\n"
				self.segments[self.curr_segment[-1]] += f"    mov dword {self.assigned_var.value}, {value.value}\n"
			elif value.name == STR:
				if self.curr_scope.id == 0:
					self.segments["data"] += f"{value.value}\n"	
					self.segments["data"] += f"    {self.assigned_var.id}_len  equ $ - __{self.assigned_var.id}__\n"
				else:
					self.segments["data"] += f"    str_{self.str_cnt}: dw {value.value}\n"
					self.segments["data"] += f"    str_{self.str_cnt}_len  equ $ - str_{self.str_cnt}\n"
					self.str_cnt += 1
		else:
			self.segments[self.curr_segment[-1]] += f"    ;; {self.assigned_var.id} = {value.id}\n"
			self.segments[self.curr_segment[-1]] += f"    mov rax, {value.value}\n"
			self.segments[self.curr_segment[-1]] += f"    mov {self.assigned_var.value}, rax\n"
	
	""" Arthimetic operation """
	def __plus(self, tok_a, tok_b):
		if tok_a.name == STR:
			error(tok_a, f"`+` operation not supported for strings.")
		type_a = type_b = None
		self.segments[self.curr_segment[-1]] += f"    ;; {tok_a.id} + {tok_b.id}\n"

		# Copying the first data into register
		# Getting the type of first token
		if tok_a.value in self.var_stack:
			if self.assigned_var:
				self.segments[self.curr_segment[-1]] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			type_a = self.var_stack[tok_a.id].name
		elif tok_a.name in data_types:
			if self.assigned_var:
				self.segments[self.curr_segment[-1]] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.id}` used for plus operation.")

		# Copying the second data into register
		# Getting the type of second token
		if tok_b.value in self.var_stack:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {self.var_stack[tok_b.id].value}\n"
			type_b = self.var_stack[tok_b.id].name
		elif tok_b.name in data_types:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.id}` used for plus operation.")

		# Adding them both
		self.segments[self.curr_segment[-1]] += f"    add rax, rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.segments[self.curr_segment[-1]] += f"    mov {self.var_stack[self.assigned_var.id].value}, rax\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    push rax\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `+` operation between types `{type_a}` and `{type_b}`.")

	def __minus(self, tok_a, tok_b):
		if tok_a.name == STR:
			error(tok_a, f"`+` operation not supported for strings.")
		type_a = type_b = None
		self.segments[self.curr_segment[-1]] += f"    ;; {tok_a.id} - {tok_b.id}\n"

		# Copying the first data into register
		# Getting the type of the first token
		if tok_a.value in self.var_stack:
			if self.assigned_var:
				self.segments[self.curr_segment[-1]] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			type_a = self.var_stack[tok_a.id].name
		elif tok_a.name in data_types:
			if self.assigned_var:
				self.segments[self.curr_segment[-1]] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.id}` used for minus operation.")

		# Copying the second data into register
		# Getting the type of sencond token
		if tok_b.value in self.var_stack:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {self.var_stack[tok_b.id].value}\n"
			type_b = self.var_stack[tok_b.id].name
		elif tok_b.name in data_types:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.id}` used for minus operation.")

		self.segments[self.curr_segment[-1]] += f"    sub rax, rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.segments[self.curr_segment[-1]] += f"    mov {self.var_stack[self.assigned_var.id].value}, rax\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    push rax\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `-` operation between types `{type_a}` and `{type_b}`.")

	def __mult(self, tok_a, tok_b):
		if tok_a.name == STR:
			error(tok_a, f"`+` operation not supported for strings.")
		type_a = type_b = None
		self.segments[self.curr_segment[-1]] += f"    ;; {tok_a.id} * {tok_b.id}\n"

		# Copying the first data into register
		# Getting the type of first token
		if tok_a.value in self.var_stack:
			if self.assigned_var:
				self.segments[self.curr_segment[-1]] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			type_a = self.var_stack[tok_a.id].name
		elif tok_a.name in data_types:
			if self.assigned_var:
				self.segments[self.curr_segment[-1]] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.id}` used for multiply operation.")

		# Copying the second data into register
		# Getting the type of second token
		if tok_b.value in self.var_stack:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {self.var_stack[tok_b.id].value}\n"
			type_b = self.var_stack[tok_b.id].name
		elif tok_b.name in data_types:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.id}` used for multiply operation.")

		self.segments[self.curr_segment[-1]] += f"    mul rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.segments[self.curr_segment[-1]] += f"    mov {self.var_stack[self.assigned_var.id].value}, rax\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    push rax\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `*` operation between types `{type_a}` and `{type_b}`.")

	def __div(self, tok_a, tok_b):
		if tok_a.name == STR:
			error(tok_a, f"`+` operation not supported for strings.")
		type_a = type_b = None
		self.segments[self.curr_segment[-1]] += f"    ;; {tok_a.id} / {tok_b.id}\n"

		# Copying the first data into register
		# Getting the type of the first token
		if tok_a.value in self.var_stack:
			if self.assigned_var:
				self.segments[self.curr_segment[-1]] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			type_a = self.var_stack[tok_a.id].name
		elif tok_a.name in data_types:
			if self.assigned_var:
				self.segments[self.curr_segment[-1]] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.id}` used for divide operation.")

		# Copying the second data into register
		# Getting the type of the second token
		if tok_b.value in self.var_stack:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {self.var_stack[tok_b.id].value}\n"
			type_b = self.var_stack[tok_b.id].name
		elif tok_b.name in data_types:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.id}` used for divide operation.")

		# Adding them both
		self.segments[self.curr_segment[-1]] += f"    xor rdx, rdx\n"
		self.segments[self.curr_segment[-1]] += f"    div rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.segments[self.curr_segment[-1]] += f"    mov {self.var_stack[self.assigned_var.id].value}, rax\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    push rax\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `/` operation between types `{type_a}` and `{type_b}`.")

	def __mod(self, tok_a, tok_b):
		if tok_a.name == STR:
			error(tok_a, f"`+` operation not supported for strings.")
		type_a = type_b = None
		self.segments[self.curr_segment[-1]] += f"    ;; {tok_a.id} % {tok_b.id}\n"

		# Copying the first data into register
		# Getting the type of first token
		if tok_a.value in self.var_stack:
			if self.assigned_var:
				self.segments[self.curr_segment[-1]] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			type_a = self.var_stack[tok_a.id].name
		elif tok_a.name in data_types:
			if self.assigned_var:
				self.segments[self.curr_segment[-1]] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.id}` used for modular division operation.")

		# Copying the second data into register
		# Getting the type of second token
		if tok_b.value in self.var_stack:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {self.var_stack[tok_b.id].value}\n"
			type_b = self.var_stack[tok_b.id].name
		elif tok_b.name in data_types:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.id}` used for modular division operation.")

		# Adding them both
		self.segments[self.curr_segment[-1]] += f"    xor rdx, rdx\n"
		self.segments[self.curr_segment[-1]] += f"    div rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.segments[self.curr_segment[-1]] += f"    mov {self.var_stack[self.assigned_var.id].value}, rdx\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    push rdx\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `/` operation between types `{type_a}` and `{type_b}`.")

	""" Conditions """
	def __equal(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Equals\n"
		self.segments[self.curr_segment[-1]] += f"    mov rcx, 0\n"
		self.segments[self.curr_segment[-1]] += f"    mov rdx, 1\n"

		if self.con_var:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {self.con_var.value}\n"
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			self.segments[self.curr_segment[-1]] += f"    pop rbx\n"

		self.segments[self.curr_segment[-1]] += f"    cmp rbx, rax\n"
		self.segments[self.curr_segment[-1]] += f"    cmove rcx, rdx\n"

		if self.con_var:
			self.segments[self.curr_segment[-1]] += f"    mov {self.con_var.value}, rcx\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    push rcx\n"
	
		self.operation = None

	def __less_than(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Less than\n"
		self.segments[self.curr_segment[-1]] += f"    mov rcx, 0\n"
		self.segments[self.curr_segment[-1]] += f"    mov rdx, 1\n"

		if self.con_var:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {self.con_var.value}\n"
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			self.segments[self.curr_segment[-1]] += f"    pop rbx\n"

		self.segments[self.curr_segment[-1]] += f"    cmp rbx, rax\n"
		self.segments[self.curr_segment[-1]] += f"    cmovl rcx, rdx\n"

		if self.con_var:
			self.segments[self.curr_segment[-1]] += f"    mov {self.con_var.value}, rcx\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    push rcx\n"
	
		self.operation = None

	def __greater_than(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Greater than\n"
		self.segments[self.curr_segment[-1]] += f"    mov rcx, 0\n"
		self.segments[self.curr_segment[-1]] += f"    mov rdx, 1\n"

		if self.con_var:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {self.con_var.value}\n"
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			self.segments[self.curr_segment[-1]] += f"    pop rbx\n"

		self.segments[self.curr_segment[-1]] += f"    cmp rbx, rax\n"
		self.segments[self.curr_segment[-1]] += f"    cmovg rcx, rdx\n"

		if self.con_var:
			self.segments[self.curr_segment[-1]] += f"    mov {self.con_var.value}, rcx\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    push rcx\n"
	
		self.operation = None

	def __less_than_equal(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Less than equal\n"
		self.segments[self.curr_segment[-1]] += f"    mov rcx, 0\n"
		self.segments[self.curr_segment[-1]] += f"    mov rdx, 1\n"

		if self.con_var:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {self.con_var.value}\n"
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			self.segments[self.curr_segment[-1]] += f"    pop rbx\n"

		self.segments[self.curr_segment[-1]] += f"    cmp rbx, rax\n"
		self.segments[self.curr_segment[-1]] += f"    cmovle rcx, rdx\n"

		if self.con_var:
			self.segments[self.curr_segment[-1]] += f"    mov {self.con_var.value}, rcx\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    push rcx\n"
	
		self.operation = None

	def __greater_than_equal(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Greater than equal\n"
		self.segments[self.curr_segment[-1]] += f"    mov rcx, 0\n"
		self.segments[self.curr_segment[-1]] += f"    mov rdx, 1\n"

		if self.con_var:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {self.con_var.value}\n"
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			self.segments[self.curr_segment[-1]] += f"    pop rbx\n"

		self.segments[self.curr_segment[-1]] += f"    cmp rbx, rax\n"
		self.segments[self.curr_segment[-1]] += f"    cmovge rcx, rdx\n"

		if self.con_var:
			self.segments[self.curr_segment[-1]] += f"    mov {self.con_var.value}, rcx\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    push rcx\n"
	
		self.operation = None
	
	def __not_equal(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Not equal\n"
		self.segments[self.curr_segment[-1]] += f"    mov rcx, 0\n"
		self.segments[self.curr_segment[-1]] += f"    mov rdx, 1\n"

		if self.con_var:
			self.segments[self.curr_segment[-1]] += f"    mov rbx, {self.con_var.value}\n"
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    pop rax\n"
			self.segments[self.curr_segment[-1]] += f"    pop rbx\n"

		self.segments[self.curr_segment[-1]] += f"    cmp rbx, rax\n"
		self.segments[self.curr_segment[-1]] += f"    cmovne rcx, rdx\n"

		if self.con_var:
			self.segments[self.curr_segment[-1]] += f"    mov {self.con_var.value}, rcx\n"
		else:
			self.segments[self.curr_segment[-1]] += f"    push rcx\n"
	
		self.operation = None

	""" INTRINSICS """
	def __print(self, params):
		param_idx = 0
		while param_idx < len(params):
			val = params[param_idx]
			
			if val.name in OPERATOR:
				error(val, "Cannot use operators in print functions")
			elif val.id == NEW_LINE:
				self.segments[self.curr_segment[-1]] += f"    ;; Newline\n"
				self.segments[self.curr_segment[-1]] += f"    puts nl, 1\n\n"
				param_idx += 1
			elif val.id in self.var_stack:
				var = self.var_stack[val.value]
				if var.name == INT or var.name == FLOAT:
					self.segments[self.curr_segment[-1]] += f"    ;; print {var.id}\n"
					self.segments[self.curr_segment[-1]] += f"    mov rdi, {var.value}\n"
					self.segments[self.curr_segment[-1]] += f"    call print\n\n"
				elif var.name == STR:
					self.segments[self.curr_segment[-1]] += f"    ;; Puts {val.id}\n"
					self.segments[self.curr_segment[-1]] += f"    puts __{val.id}__, {val.id}_len \n\n"
				param_idx += 1
			elif val.name in data_types:
				if val.name == INT or val.name == FLOAT:
					self.segments[self.curr_segment[-1]] += f"    ;; print {val.value}\n"
					self.segments[self.curr_segment[-1]] += f"    mov rdi, {val.value}\n"
					self.segments[self.curr_segment[-1]] += f"    call print\n\n"
				elif val.name == STR:
					self.segments["data"] += f"    str_{self.str_cnt}: dw {val.value}\n"
					self.segments["data"] += f"    str_{self.str_cnt}_len  equ $ - str_{self.str_cnt}\n"
	
					self.segments[self.curr_segment[-1]] += f"    ;; Puts {val.value}\n"
					self.segments[self.curr_segment[-1]] += f"    puts str_{self.str_cnt}, str_{self.str_cnt}_len \n\n"
	
					self.str_cnt += 1
				param_idx += 1
			else:
				error(val, f"Unknown word \'{val.value}\'");
	
	def __syscall1(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Syscall 1\n"
		self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		self.segments[self.curr_segment[-1]] += f"    syscall\n"
		self.operation = None

	def __syscall2(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Syscall 2\n"
		self.segments[self.curr_segment[-1]] += f"    pop rdi\n"
		self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		self.segments[self.curr_segment[-1]] += f"    syscall\n"
		self.operation = None
		
	def __syscall3(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Syscall 3\n"
		self.segments[self.curr_segment[-1]] += f"    pop rsi\n"
		self.segments[self.curr_segment[-1]] += f"    pop rdi\n"
		self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		self.segments[self.curr_segment[-1]] += f"    syscall\n"
		self.operation = None

	def __syscall4(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Syscall 4\n"
		self.segments[self.curr_segment[-1]] += f"    pop rdx\n"
		self.segments[self.curr_segment[-1]] += f"    pop rsi\n"
		self.segments[self.curr_segment[-1]] += f"    pop rdi\n"
		self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		self.segments[self.curr_segment[-1]] += f"    syscall\n"
		self.operation = None

	def __syscall5(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Syscall 5\n"
		self.segments[self.curr_segment[-1]] += f"    pop r10\n"
		self.segments[self.curr_segment[-1]] += f"    pop rdx\n"
		self.segments[self.curr_segment[-1]] += f"    pop rsi\n"
		self.segments[self.curr_segment[-1]] += f"    pop rdi\n"
		self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		self.segments[self.curr_segment[-1]] += f"    syscall\n"
		self.operation = None

	def __syscall6(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Syscall 6\n"
		self.segments[self.curr_segment[-1]] += f"    pop r8\n"
		self.segments[self.curr_segment[-1]] += f"    pop r10\n"
		self.segments[self.curr_segment[-1]] += f"    pop rdx\n"
		self.segments[self.curr_segment[-1]] += f"    pop rsi\n"
		self.segments[self.curr_segment[-1]] += f"    pop rdi\n"
		self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		self.segments[self.curr_segment[-1]] += f"    syscall\n"
		self.operation = None

	def __syscall7(self):
		self.segments[self.curr_segment[-1]] += f"    ;; Syscall 7\n"
		self.segments[self.curr_segment[-1]] += f"    pop r9\n"
		self.segments[self.curr_segment[-1]] += f"    pop r8\n"
		self.segments[self.curr_segment[-1]] += f"    pop r10\n"
		self.segments[self.curr_segment[-1]] += f"    pop rdx\n"
		self.segments[self.curr_segment[-1]] += f"    pop rsi\n"
		self.segments[self.curr_segment[-1]] += f"    pop rdi\n"
		self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		self.segments[self.curr_segment[-1]] += f"    syscall\n"
		self.operation = None
	
	""" Keywords """
	def __return(self):
		self.segments[self.curr_segment[-1]] += f"    pop rax\n"
		self.segments[self.curr_segment[-1]] += f"    mov rbp, rsp\n"
		self.segments[self.curr_segment[-1]] += f"    pop rbp\n"
		self.segments[self.curr_segment[-1]] += f"    ret\n"
		self.operation = None
	
	""" Helper functions """
	def __get_assigned_var(self):
		self.assigned_var = self.line[self.token_cnt - 1]
		if self.assigned_var.value not in self.var_stack:
			error(self.assigned_var, f"Undefined variable `{self.assigned_var.value}`.")
		self.assigned_var = self.var_stack[self.assigned_var.value]

	def compile(self):
		self.segments["data"]  = "section .data\n"
		self.segments["data"] += "    nl: dw 10\n"
		self.segments["bss"]   = "section .bss\n"

		self.segments["text"]  = "section .text\n"
		self.segments["text"] += "    global _start\n"
		self.segments["text"] += "_start:\n"
		self.segments["text"] += "    push rbp\n"
		self.segments["text"] += "    mov rbp, rsp\n"

		self.segments["exit"]  =  "exit:\n"
		self.segments["exit"] += "    mov rax, 60\n"
		self.segments["exit"] += "    mov rdi, 0\n"
		self.segments["exit"] += "    syscall\n"

		self.__start_scope()

		while self.prog_cnt < len(self.program):
			self.line = self.program[self.prog_cnt]
			self.prog_cnt += 1
			self.token_cnt = 0
			self.assigned_var = None
			self.con_var = None

			while self.token_cnt < len(self.line):
				token = self.line[self.token_cnt]

				if token.name == DATA_TYPE:
					self.token_cnt += 1
					self.__create_var(token.value) # Giving the data type to create variable

				elif token.name == WORD:
					self.token_cnt += 1

					if token.value in self.var_stack:
						variable = self.var_stack[token.value]
						if self.assigned_var:
							self.__assign_var(variable)
						else:
							if self.token_cnt < len(self.line):
								black_lst = [ASSIGN, PLUS_EQ, MINUS_EQ, MULT_EQ, DIV_EQ, MOD_EQ]
								if self.line[self.token_cnt].value not in black_lst:
									# Pushing onto the stack
									self.segments[self.curr_segment[-1]] += f"    ;; Pushing {variable.id}\n"
									if variable.name == INT or variable.name == FLOAT:
										self.segments[self.curr_segment[-1]] += f"    mov rax, {variable.value}\n"
									elif variable.name == STR:
										#TODO: Create a proper way for pusing strings onto the stack (sometimes it needs `[]` sometimes it doesnt
										self.segments[self.curr_segment[-1]] += f"    mov rax, {variable.value}\n"
									self.segments[self.curr_segment[-1]] += f"    push rax\n"
							else:
								# Pushing onto the stack
								self.segments[self.curr_segment[-1]] += f"    ;; Pushing {variable.id}\n"
								if variable.name == INT or variable.name == FLOAT:
									self.segments[self.curr_segment[-1]] += f"    mov rax, {variable.value}\n"
								elif variable.name == STR:
									#TODO: Create a proper way for pusing strings onto the stack (sometimes it needs `[]` sometimes it doesnt
									self.segments[self.curr_segment[-1]] += f"    mov rax, {variable.value}\n"
								self.segments[self.curr_segment[-1]] += f"    push rax\n"
								self.token_cnt += 1

					elif token.value in self.func_stack:
						if self.assigned_var:
							self.func_stack[token.value].ret_var = self.assigned_var
							self.assigned_var = None

						self.called_func.append(token.value)
						nxt = self.line[self.token_cnt]
						if nxt.value != BRACK_OPEN:
							error(nxt, f"Expected a bracket open `(` but got `{nxt.value}`.")
					else:
						error(token, f"Undefined reference to `{token.value}`.")

				elif token.name in data_types:
					self.token_cnt += 1
					if self.assigned_var:
						self.__assign_var(token)	
					else:
						# Pusing into the stack
						if token.name == INT or token.name == FLOAT:
							self.segments[self.curr_segment[-1]] += f"    ;; Pushing {token.value}\n"
							self.segments[self.curr_segment[-1]] += f"    push {token.value}\n"
						elif token.name == STR:
							self.segments["data"] += f"    str_{self.str_cnt}: dw {token.value}\n"
							self.segments["data"] += f"    str_{self.str_cnt}_len  equ $ - str_{self.str_cnt}\n"
			
							self.segments[self.curr_segment[-1]] += f"    ;; Pusing {token.value}\n"
							self.segments[self.curr_segment[-1]] += f"    push str_{self.str_cnt}\n"
			
							self.str_cnt += 1

				elif token.name == OPERATOR:
					if token.value == ASSIGN:
						if self.token_cnt + 1 == len(self.line):
							error(token, f"`{token.value}` operater requires two operand.")
						self.__get_assigned_var()
						self.token_cnt += 1

					elif token.value == PLUS:
						if self.token_cnt + 1 == len(self.line):
							error(token, f"`{token.value}` operater requires two operand.")
						tok_a = self.line[self.token_cnt - 1]
						tok_b = self.line[self.token_cnt + 1]
						self.token_cnt += 2
						if self.assigned_var:
							self.__plus(self.assigned_var, tok_b)
						else:
							self.__plus(tok_a, tok_b)

					elif token.value == MINUS:
						if self.token_cnt + 1 == len(self.line):
							error(token, f"`{token.value}` operater requires two operand.")
						tok_a = self.line[self.token_cnt - 1]
						tok_b = self.line[self.token_cnt + 1]
						self.token_cnt += 2
						if self.assigned_var:
							self.__minus(self.assigned_var, tok_b)
						else:
							self.__minus(tok_a, tok_b)

					elif token.value == MULT:
						if self.token_cnt + 1 == len(self.line):
							error(token, f"`{token.value}` operater requires two operand.")
						tok_a = self.line[self.token_cnt - 1]
						tok_b = self.line[self.token_cnt + 1]
						self.token_cnt += 2
						if self.assigned_var:
							self.__mult(self.assigned_var, tok_b)
						else:
							self.__mult(tok_a, tok_b)

					elif token.value == DIV:
						if self.token_cnt + 1 == len(self.line):
							error(token, f"`{token.value}` operater requires two operand.")
						tok_a = self.line[self.token_cnt - 1]
						tok_b = self.line[self.token_cnt + 1]
						self.token_cnt += 2
						if self.assigned_var:
							self.__div(self.assigned_var, tok_b)
						else:
							self.__div(tok_a, tok_b)

					elif token.value == MOD:
						if self.token_cnt + 1 == len(self.line):
							error(token, f"`{token.value}` operater requires two operand.")
						tok_a = self.line[self.token_cnt - 1]
						tok_b = self.line[self.token_cnt + 1]
						self.token_cnt += 2
						if self.assigned_var:
							self.__mod(self.assigned_var, tok_b)
						else:
							self.__mod(tok_a, tok_b)

					elif token.value == PLUS_EQ:
						if self.token_cnt + 1 == len(self.line):
							error(token, f"`{token.value}` operater requires two operand.")
						self.__get_assigned_var()
						tok_b = self.line[self.token_cnt + 1]
						self.__plus(self.assigned_var, tok_b)
						self.token_cnt += 2
					
					elif token.value == MINUS_EQ:
						if self.token_cnt + 1 == len(self.line):
							error(token, f"`{token.value}` operater requires two operand.")
						self.__get_assigned_var()
						tok_b = self.line[self.token_cnt + 1]
						self.__minus(self.assigned_var, tok_b)
						self.token_cnt += 2

					elif token.value == MULT_EQ:
						if self.token_cnt + 1 == len(self.line):
							error(token, f"`{token.value}` operater requires two operand.")
						self.__get_assigned_var()
						tok_b = self.line[self.token_cnt + 1]
						self.__mult(self.assigned_var, tok_b)
						self.token_cnt += 2
					
					elif token.value == DIV_EQ:
						if self.token_cnt + 1 == len(self.line):
							error(token, f"`{token.value}` operater requires two operand.")
						self.__get_assigned_var()
						tok_b = self.line[self.token_cnt + 1]
						self.__div(self.assigned_var, tok_b)
						self.token_cnt += 2

					elif token.value == MOD_EQ:
						if self.token_cnt + 1 == len(self.line):
							error(token, f"`{token.value}` operater requires two operand.")
						self.__get_assigned_var()
						tok_b = self.line[self.token_cnt + 1]
						self.__mod(self.assigned_var, tok_b)
						self.token_cnt += 2

					elif token.value == INC:
						var = self.line[self.token_cnt - 1]
						if self.token_cnt == 0:
							error(var, f"Token `{var.value}` requires one operand.")
						if var.value not in self.var_stack:
							error(var, f"Undefined reference to word `{var.value}`.")
						
						var = self.var_stack[var.value]
						self.segments[self.curr_segment[-1]] += f"    ;; {var.id}++\n"
						self.segments[self.curr_segment[-1]] += f"    pop rax\n"
						self.segments[self.curr_segment[-1]] += f"    inc rax\n"
						self.segments[self.curr_segment[-1]] += f"    mov {var.value}, rax\n"
						self.token_cnt += 1

					elif token.value == DEC:
						var = self.line[self.token_cnt - 1]
						if self.token_cnt == 0:
							error(var, f"Token `{var.value}` requires one operand.")
						if var.value not in self.var_stack:
							error(var, f"Undefined reference to word `{var.value}`.")

						var = self.var_stack[var.value]
						self.segments[self.curr_segment[-1]] += f"    ;; {var.id}--\n"
						self.segments[self.curr_segment[-1]] += f"    pop rax\n"
						self.segments[self.curr_segment[-1]] += f"    dec rax\n"
						self.segments[self.curr_segment[-1]] += f"    mov {var.value}, rax\n"
						self.token_cnt += 1

				elif token.name == CONDITION:

					if token.value == EQUAL:
						self.token_cnt += 1

						if self.operation:
							self.operation()

						# Copying the assigned variable to the equal variable for comparision and resetting it to make other value push in the stack
						if self.assigned_var:
							 self.con_var = self.assigned_var
						self.assigned_var = None

						# Putting the function pointer
						self.operation = self.__equal
					
					elif token.value == LT:
						self.token_cnt += 1
						
						if self.operation:
							self.operation()

						# Copying the assigned variable to the equal variable for comparision and resetting it to make other value push in the stack
						if self.assigned_var:
							 self.con_var = self.assigned_var
						self.assigned_var = None

						# Putting the function pointer
						self.operation = self.__less_than

					elif token.value == GT:
						self.token_cnt += 1

						if self.operation:
							self.operation()

						# Copying the assigned variable to the equal variable for comparision and resetting it to make other value push in the stack
						if self.assigned_var:
							 self.con_var = self.assigned_var
						self.assigned_var = None

						# Putting the function pointer
						self.operation = self.__greater_than
					
					elif token.value == LTE:
						self.token_cnt += 1

						if self.operation:
							self.operation()

						# Copying the assigned variable to the equal variable for comparision and resetting it to make other value push in the stack
						if self.assigned_var:
							 self.con_var = self.assigned_var
						self.assigned_var = None

						# Putting the function pointer
						self.operation = self.__less_than_equal
					
					elif token.value == GTE:
						self.token_cnt += 1

						if self.operation:
							self.operation()

						# Copying the assigned variable to the equal variable for comparision and resetting it to make other value push in the stack
						if self.assigned_var:
							 self.con_var = self.assigned_var
						self.assigned_var = None

						# Putting the function pointer
						self.operation = self.__greater_than_equal
					
					elif token.value == NT:
						self.token_cnt += 1

						if self.operation:
							self.operation()

						# Copying the assigned variable to the equal variable for comparision and resetting it to make other value push in the stack
						if self.assigned_var:
							 self.con_var = self.assigned_var
						self.assigned_var = None

						# Putting the function pointer
						self.operation = self.__not_equal

				elif token.name == INTRINSIC:
					if token.value == PRINT:
						params = self.line[self.token_cnt + 1:]
						self.token_cnt = len(self.line)
						self.__print(params)

					elif token.value == INCLUDE:
						self.token_cnt += 1
						if self.token_cnt >= len(self.line):
							error(token, f"Include token expected a path to the file but got nothing.")

						file = self.line[self.token_cnt]
						self.token_cnt += 1
						if file.name != STR:
							error(file, f"File path should be `str` but got `{file.name}`.")

						# Converting to the absolute path
						file_path = file.value[1:len(file.value)-1:]
						file_path = os.path.abspath(file_path)
						if file_path in self.include_files:
							error(file, f"Multiple inclusion of file `{file_path}`.")

						if not os.path.isfile(file_path):
							error(file, f"Cannot find file `{file_path}`.")

						# Adding the path in the included files
						self.include_files.append(file_path)

						# Generating the tokens of the new file and pushing it into the original program
						new_program = list(reversed(lex_file(file_path)))
						for i in new_program:
							self.program.insert(self.prog_cnt, i)

					elif token.value == DEFINE:
						params = self.line[self.token_cnt + 1:]
						self.token_cnt = len(self.line)
						if len(params) != 2:
							error(token, f"`%define` keyword accpets only two argument: [name] [value] but recevied `{len(params)}`.")

						name = params[0]
						if name.name != WORD:
							error(name, f"`%define` keyword only accept `word` as a name but got `{name.name}`.")
						value = params[1]
						if value.name not in data_types:
							error(value, f"`%define` keyword only accept data types as a value but got `{value.name}`.")
						if name.value in self.var_stack:
							error(name, f"Name `{name.value}` has already been defined.")

						variable = Token(value.name, name.value, name.value, token.row, token.col, token.file)
						if value.name == INT or value.name == FLOAT:
							self.segments["define"] += f"%define __{variable.id}__ {value.value}\n"
							variable.value = f"__{variable.id}__"
						elif value.name == STR:
							self.segments["define"] += f"%define __{variable.id}__ {value.value}\n"
							self.segments["define"] += f"%define {variable.id}_len equ $ - __{variable.id}__\n"
							variable.value = f"__{variable.id}__"
						else:
							error(variable, f"`{value.name}` type cant be used for definations.")

						self.var_stack.update({variable.id: variable})

					elif token.value == SYSCALL1:
						self.token_cnt += 1
						if self.operation:
							self.operation()
						self.operation = self.__syscall1

					elif token.value == SYSCALL2:
						self.token_cnt += 1
						if self.operation:
							self.operation()
						self.operation = self.__syscall2
						
					elif token.value == SYSCALL3:
						self.token_cnt += 1
						if self.operation:
							self.operation()
						self.operation = self.__syscall3

					elif token.value == SYSCALL4:
						self.token_cnt += 1
						if self.operation:
							self.operation()
						self.operation = self.__syscall4

					elif token.value == SYSCALL5:
						self.token_cnt += 1
						if self.operation:
							self.operation()
						self.operation = self.__syscall5

					elif token.value == SYSCALL6:
						self.token_cnt += 1
						if self.operation:
							self.operation()
						self.operation = self.__syscall6

					elif token.value == SYSCALL7:
						self.token_cnt += 1
						if self.operation:
							self.operation()
						self.operation = self.__syscall7
						
				elif token.name == KEYWORD:
					if token.value == IF:
						self.token_cnt += 1
						self.addr_cnt = len(self.addr_stack)

						new_addr = Addr(IF, None, self.addr_cnt, False, False)
						self.addr_stack.append(new_addr)
						self.segments[self.curr_segment[-1]] += f"    ;; If\n"
						self.segments[self.curr_segment[-1]] += f"addr_{self.addr_stack[self.addr_cnt].id}_if:\n"
						self.segments.update({f"addr_{self.addr_stack[self.addr_cnt].id}_if": ""})
						self.__start_scope()

					elif token.value == THEN:
						self.__end_scope()
						self.__start_scope()
						self.token_cnt += 1

						if self.addr_cnt < 0:
							error(token, "then without if.")
						if self.addr_stack[self.addr_cnt].start:
							error(token, "then without if.")

						self.addr_stack[self.addr_cnt].start = True

						if self.operation:
							self.operation()

						if self.ret_stack: self.ret_stack -= 1
						self.segments[f"addr_{self.addr_stack[self.addr_cnt].id}_if"] += f"    ;; Then\n"
						self.segments[f"addr_{self.addr_stack[self.addr_cnt].id}_if"] += f"    pop rax\n"
						self.segments[f"addr_{self.addr_stack[self.addr_cnt].id}_if"] += f"    cmp rax, 1\n"
						self.segments[f"addr_{self.addr_stack[self.addr_cnt].id}_if"] += f"    je  addr_{self.addr_stack[self.addr_cnt].id}_then\n"

						self.curr_segment.append(f"addr_{self.addr_stack[self.addr_cnt].id}_then")
						self.segments.update({f"addr_{self.addr_stack[self.addr_cnt].id}_then": ""})

						self.segments[self.curr_segment[-1]] += f"addr_{self.addr_stack[self.addr_cnt].id}_then:\n"

					elif token.value == ELSE:
						self.__end_scope()
						self.__start_scope()

						addr = self.addr_stack[self.addr_cnt]
						if addr.end:
							error(token, f"Else without if.")

						self.token_cnt += 1
						self.segments.update({f"addr_{self.addr_stack[self.addr_cnt].id}_else": ""})
						self.segments[f"addr_{self.addr_stack[self.addr_cnt].id}_if"] += f"    jne addr_{self.addr_stack[self.addr_cnt].id}_else\n"
						self.segments[f"addr_{self.addr_stack[self.addr_cnt].id}_else"] += f"    jmp addr_{self.addr_stack[self.addr_cnt].id}_end\n"
						self.segments[f"addr_{self.addr_stack[self.addr_cnt].id}_else"] += f"addr_{self.addr_stack[self.addr_cnt].id}_else:\n"
						self.curr_segment.pop()
						self.curr_segment.append(f"addr_{self.addr_stack[self.addr_cnt].id}_else")

					elif token.value == END:
						self.__end_scope()

						self.token_cnt += 1
						addr = self.addr_stack[self.addr_cnt]

						if addr.end:
							error(token, f"Cannot find the entry point to then `end`.")

						if addr.type == IF:
							self.curr_segment.pop()
							self.segments[self.curr_segment[-1]] += self.segments[f"addr_{self.addr_stack[self.addr_cnt].id}_if"]
							self.segments[self.curr_segment[-1]] += self.segments[f"addr_{self.addr_stack[self.addr_cnt].id}_then"]

							if f"addr_{self.addr_stack[self.addr_cnt].id}_else" in self.segments:
								self.segments[self.curr_segment[-1]] += self.segments[f"addr_{self.addr_stack[self.addr_cnt].id}_else"]

							self.segments[self.curr_segment[-1]] += f"    jmp addr_{addr.id}_end\n"
							self.segments[self.curr_segment[-1]] += f"addr_{addr.id}_end:\n"
							self.segments.pop(f"addr_{self.addr_stack[self.addr_cnt].id}_if")
							self.segments.pop(f"addr_{self.addr_stack[self.addr_cnt].id}_then")
							if f"addr_{self.addr_stack[self.addr_cnt].id}_else" in self.segments:
								self.segments.pop(f"addr_{self.addr_stack[self.addr_cnt].id}_else")

						elif addr.type == WHILE:
							self.segments[self.curr_segment[-1]] += f"    jmp addr_{addr.id}_while\n"
							self.segments[self.curr_segment[-1]] += f"addr_{addr.id}_end:\n"
						elif addr.type == FUNC:
							if not addr.start:
								error(self.func_stack[addr.name], f"Missing `in` token in function `{addr.name}`.")
							func = self.func_stack[addr.name]
							if func.ret_type.value == INT or func.ret_type.value == FLOAT:
								self.segments[self.curr_segment[-1]] += f"    push 0\n"
								self.segments[self.curr_segment[-1]] += f"    pop rax\n"
							self.segments[self.curr_segment[-1]] += f"    mov rbp, rsp\n"
							self.segments[self.curr_segment[-1]] += f"    pop rbp\n"
							self.segments[self.curr_segment[-1]] += f"    ret\n"

							if self.curr_segment:
								self.curr_segment.pop()
							if self.curr_func:
								self.curr_func.pop()

						# Telling that this address has ended
						self.addr_stack[self.addr_cnt].end = True

						# Finding the previous address that hasnt been ended
						while self.addr_stack[self.addr_cnt].end:
							self.addr_cnt -= 1
							if self.addr_cnt < 0:
								self.addr_cnt = 0
								break

					elif token.value == WHILE:
						self.__end_scope()
						self.__start_scope()
						self.token_cnt += 1
						self.addr_cnt = len(self.addr_stack)

						new_addr = Addr(WHILE, None, self.addr_cnt, False, False)
						self.addr_stack.append(new_addr)
						self.segments[self.curr_segment[-1]] += f"    ;; While\n"
						self.segments[self.curr_segment[-1]] += f"addr_{self.addr_stack[self.addr_cnt].id}_while:\n"

					elif token.value == DO:
						self.__start_scope()

						self.token_cnt += 1

						if self.addr_cnt < 0:
							error(token, "do without while.")
						if self.addr_stack[self.addr_cnt].start:
							error(token, "do without while.")

						self.addr_stack[self.addr_cnt].start = True

						if self.operation:
							self.operation()

						if self.ret_stack: self.ret_stack -= 1
						self.segments[self.curr_segment[-1]] += f"    ;; Do\n"
						self.segments[self.curr_segment[-1]] += f"    pop rax\n"
						self.segments[self.curr_segment[-1]] += f"    cmp rax, 1\n"
						self.segments[self.curr_segment[-1]] += f"    je  addr_{self.addr_stack[self.addr_cnt].id}_do\n"
						self.segments[self.curr_segment[-1]] += f"    jne addr_{self.addr_stack[self.addr_cnt].id}_end\n"

						self.segments[self.curr_segment[-1]] += f"addr_{self.addr_stack[self.addr_cnt].id}_do:\n"

					elif token.value == FUNC:
						self.__start_scope()

						# Telling the compiler we encountered a function
						self.curr_segment.append("func")

						name = self.line[self.token_cnt + 1]
						self.token_cnt += 2

						if self.line[self.token_cnt].value != PARAM:
							error(self.line[self.token_cnt], f"Expected a param token `:` but got `{self.line[self.token_cnt].value}`.")

						if name.name != WORD:
							error(name, f"Function name is expected to be a `word` but got `{name.name}`.")
						if name.value in self.func_stack:
							error(name, f"Function with name `{name.value}` is already defined.")

						self.addr_cnt = len(self.addr_stack)
						new_addr = Addr(FUNC, name.value, self.addr_cnt, False, False)
						self.addr_stack.append(new_addr)

						new_func = Func(name.value, f"func_{self.addr_stack[self.addr_cnt].id}_{name.value}", [], None, name.row, name.col, name.file)
						self.curr_func.append(new_func.name)

						self.segments[self.curr_segment[-1]] += f";; {new_func.name}\n"
						self.segments[self.curr_segment[-1]] += new_func.id + ":\n" 
						self.segments[self.curr_segment[-1]] += f"    push rbp\n"
						self.segments[self.curr_segment[-1]] += f"    mov rbp, rsp\n"

						# Saving it in the function stack
						self.func_stack.update({name.value : new_func})

					elif token.value == PARAM:
						self.token_cnt += 1

						if self.addr_cnt < 0:
							error(token, f"Cannot use param token `:` outside of function.")
						if self.addr_stack[self.addr_cnt].start:
							error(token, f"Cannot use param token `:` outside of function.")

						# Getting the params
						tokens = []
						while self.line[self.token_cnt].value != RET_TYPE:
							token = self.line[self.token_cnt]
							if token.name == DATA_TYPE or token.name == WORD:
								tokens.append(token)
							else:
								error(token, f"Expected return type keyword `->` but got token `{token.value}`.")
							self.token_cnt += 1
						
						# Parsing the params

						# Calculating the index for the first param and pushing it in a revered order
						i = 0
						var_idx = 8
						while i < len(tokens):
							token = tokens[i]
							i += 1
							if token.name == WORD:
								var_idx += 8
						
						i = 0
						while i < len(tokens):
							token = tokens[i]
							if token.name == DATA_TYPE:
								i += 1
								if i >= len(tokens):
									error(token, f"Did not get the variable name.")
								var = tokens[i]
								i += 1

								if var.id in self.var_stack:
									error(var, f"Variable `{var.value}` is already defined.")
								if var.name != WORD:
									error(var, f"Cannot create a variable with `{var.value}` token.")
								var = Token(token.value, var.id, var.value, var.row, var.col, var.file)
								var.value = f"[rbp + {var_idx}]"
								var_idx -= 8

								self.func_stack[self.addr_stack[self.addr_cnt].name].params.append(var)
								self.curr_scope.vars.append(var.id)
								self.var_stack.update({var.id: var})

							elif token.name == WORD:
								error(token, f"Undefined type for the creation of variable `{token.value}`.")

					elif token.value == RET_TYPE:
						if self.addr_cnt < 0:
							error(token, f"Cannot use return type token `->` outside of function.")
						if self.addr_stack[self.addr_cnt].start:
							error(token, f"Cannot use return type token `->` outside of function.")

						self.token_cnt += 1
						type = self.line[self.token_cnt]
						self.token_cnt += 1

						if type.name != DATA_TYPE:
							error(type, f"Return type can only be a data type.")
						
						type.name = type.value
						self.func_stack[self.addr_stack[self.addr_cnt].name].ret_type = type

					elif token.value == IN:
						if self.addr_cnt < 0:
							error(token, f"Cannot use `in` token without declaration of function.")
						if self.addr_stack[self.addr_cnt].start:
							error(token, f"Cannot use `in` token without declaration of function.")
						self.addr_stack[self.addr_cnt].start = True

						self.token_cnt += 1

					elif token.value == RETURN:
						self.token_cnt += 1

						# Type checking of return 
						func = self.func_stack[self.curr_func[-1]]
						if self.token_cnt < len(self.line):
							token = self.line[self.token_cnt]
							type = None

							if token.value in self.var_stack:
								type = self.var_stack[token.value].name
							elif token.name in data_types:
								type = token.name
							elif token.value in self.func_stack:
								type = self.func_stack[token.value].ret_type.value
							
							if type:
								if func.ret_type.value != type:
									error(token, f"Function `{func.name}` returns `{func.ret_type.value}` but got `{type}`.")
							else:
								error(token, f"Unknown token used for return `{token.value}`.")
						else:
							error(token, f"Function `{func.name}` returns `{func.ret_type.value}` but got nothing.") 

						self.operation = self.__return

					elif token.value == BRACK_OPEN:
						if self.token_cnt == 0:
							error(token, f"Use of brackets without the function name.")

						if self.line[self.token_cnt - 1].name != WORD:
							error(token, f"Use of brackets without the function name.")

						self.token_cnt += 1

						# Checking the types of the params
						tokens = []
						types  = []
						i = self.token_cnt
						while self.line[i].value != BRACK_CLOSE:
							new_token = self.line[i]
							if new_token.value == BRACK_OPEN:
								while self.line[i].value != BRACK_CLOSE:
									i += 1
							else:
								tokens.append(new_token)
							i += 1

						i = 0
						while i < len(tokens):
							new_token = tokens[i]
							i += 1

							if new_token.value in self.var_stack:
								var = self.var_stack[new_token.value]
								types.append(var)
							elif new_token.value in self.func_stack:
								func = self.func_stack[new_token.value]
								types.append(func.ret_type)
							elif new_token.name in data_types:
								types.append(new_token)
							elif new_token.name == WORD:
								error(new_token, f"Use of undeclared variable `{new_token.value}`.")
							else:
								error(new_token, f"Cannot use token `{new_token.value}` inside of the function parameter.")

						# Checking the length of the given parameters
						func = self.func_stack[self.called_func[-1]]
						if len(types) != len(func.params):
							error(token, f"Function `{func.name}` requires `{len(func.params)}` parameters but got `{len(types)}`.")
					
						# Checking the types of the parameters
						for i in range(len(func.params)):
							if func.params[i].name != types[i].name:
								error(types[i], f"Required type `{func.params[i].name}` but got `{types[i].name}`.")

					elif token.value == BRACK_CLOSE:
						self.token_cnt += 1
						
						self.assigned_var = self.func_stack[self.called_func[-1]].ret_var 
						self.func_stack[self.called_func[-1]].ret_var = None


						self.segments[self.curr_segment[-1]] += f"    ;; Call {self.called_func[-1]}\n"
						self.segments[self.curr_segment[-1]] += f"    call {self.func_stack[self.called_func[-1]].id}\n"

						# Poping the parameters of the function
						for i in range(len(self.func_stack[self.called_func[-1]].params)):
							self.segments[self.curr_segment[-1]] += f"    pop rbx\n"

						if self.assigned_var:
							self.segments[self.curr_segment[-1]] += f"    mov {self.assigned_var.value}, rax\n"
						else:
							self.segments[self.curr_segment[-1]] += f"    push rax\n"
							self.ret_stack += 1

						self.called_func.pop()

					elif token.value == NEW_LINE:
						self.token_cnt += 1
						self.segments[self.curr_segment[-1]] += f"    push nl\n"

					else:
						error(token, "Invalid syntax.")

				elif token.name == COMMENT:
					self.token_cnt += 1

			if self.operation:
				self.operation()

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
		print_func += "    mov     rax, 1\n"
		print_func += "    mov     rdi, 1\n"
		print_func += "    syscall\n"
		print_func += "    nop\n"
		print_func += "    leave\n"
		print_func += "    ret\n"

		# Writing into assembly file
		self.out_file = open(self.asm_file, "w")
		self.out_file.write(self.segments["define"])
		self.out_file.write("\n")
		self.out_file.write(puts_macro)
		self.out_file.write("\n")
		self.out_file.write(print_func)
		self.out_file.write("\n")
		self.out_file.write(self.segments["func"])
		self.out_file.write("\n")
		self.out_file.write(self.segments["data"])
		self.out_file.write("\n")
		self.out_file.write(self.segments["bss"])
		self.out_file.write("\n")
		self.out_file.write(self.segments["text"])
		self.out_file.write("\n")
		self.out_file.write(self.segments["exit"])
		self.out_file.close()

		# Compiling the program
		os.system(f"nasm -felf64 {self.asm_file}")
		os.system(f"ld -o {self.exe_file} {self.obj_file}")
		print(f"nasm -felf64 {self.asm_file}")
		print(f"ld -o {self.exe_file} {self.obj_file}")


def usage():
	print("Usage: slug [mode] [file_name]")
	print("mode:  sim   --- simulates program (Not implemented)")
	print("       com   --- compiles  program")

if __name__ == "__main__":
	if len(sys.argv) <= 2:
		usage()
		exit(1)

	mode = sys.argv[1]
	file = sys.argv[2]

	program = lex_file(file)
	
	slug = Slug(file, program)
	if mode == "sim":
		slug.simulate()
	elif mode == "com":
		slug.compile()
