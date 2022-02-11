#!/bin/python
import os
import sys

#TODO: [ ] Some variable names are not allowed to create due to registers name conflict (FIX THAT)
#TODO: [ ] Add support for if without else
#TODO: [X] Introduce scopes
#TODO: [X] Implement functions

WORD = "word"
COMMENT = "#"

# Data types
INT = "int"
STR = "str"
FLOAT = "float"
DATA_TYPE = "data_type"
data_types = [INT, STR, FLOAT]

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
PRINT    = "print"
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
keywords = [PRINT, NEW_LINE, IF, THEN, ELSE, END, WHILE, DO, FUNC, IN, PARAM, RET_TYPE, RETURN, BRACK_OPEN, BRACK_CLOSE]

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
		self.name = name
		self.id = id
		self.value = value
		self.row = row
		self.col = col
		self.file = file

	def __repr__(self):
		return f"TOKEN({self.name}, {self.value})"

class Scope:
	def __init__(self, id, start, end):
		self.id = id
		self.start = start
		self.end = end
		self.vars = []
	
	def __repr__(self):
		return f"Scope: {self.id}"

class Addr:
	def __init__(self, type, name, id, start, end):
		self.type = type
		self.name = name
		self.id = id
		self.start = start
		self.end = end
	
	def __repr__(self):
		return f"Addr({self.type}: {self.id}, {self.start}, {self.end})"

class Func:
	def __init__(self, name, id, params, ret_type, row, col, file):
		self.name = name
		self.id = id
		self.params = params
		self.ret_type = ret_type
		self.row = row
		self.col = col
		self.file = file
		self.ret_var = None
	
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
	delim = []
	delim.append(BRACK_OPEN)
	delim.append(BRACK_CLOSE)
	delim.append(COMMENT)

	i = 0
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
		self.func_segment = ""
		self.segments = {
				"text": self.text_segment,
				"bss" : self.bss_segment,
				"data": self.data_segment,
				"exit": self.exit_segment,
				"func": self.func_segment
		}
		self.curr_segment = "text"

		# Stacks
		self.scopes = []
		self.line = []
		self.addr_stack = []
		self.var_stack = {}
		self.func_stack = {}
		self.called_func  = []
		self.curr_func    = []
		self.ret_stack = 0

		# Flags
		self.assigned_var = None
		self.con_var      = None
		self.func_ret_var = None
		self.operation    = None

		# Counters
		self.prog_cnt  = 0
		self.str_cnt   = 0
		self.token_cnt = 0
		self.addr_cnt  = -1
		self.local_var_cnt = 0
	
	def simulate(self):
		token = Token(None, None, None, 0, 0, self.file)
		error(token, "Simulation mode is not yet implemented.")

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
			self.segments[self.curr_segment] += f"    pop rax\n"
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
				self.segments["bss"]  += f"    {variable.value}: resd 32\n"
			elif type == STR:
				self.segments["data"] += f"    {variable.value}: dw "
			variable.value = f"[{variable.value}]"
		else:
			variable.value = f"[rbp - {self.local_var_cnt + 8}]"
			self.local_var_cnt += 8
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
				self.segments[self.curr_segment] += f"    ;; {self.assigned_var.id} = {value.id}\n"
				self.segments[self.curr_segment] += f"    mov dword {self.assigned_var.value}, {value.value}\n"
			elif value.name == STR:
				self.segments["data"] += f"{value.value}\n"	
				self.segments["data"] += f"    {self.assigned_var.id}_len_6969 equ $ - {self.assigned_var.id}\n"
				self.str_cnt += 1
		else:
			self.segments[self.curr_segment] += f"    ;; {self.assigned_var.id} = {value.id}\n"
			self.segments[self.curr_segment] += f"    mov rax, {value.value}\n"
			self.segments[self.curr_segment] += f"    mov {self.assigned_var.value}, rax\n"
	
	""" Arthimetic operation """
	def __plus(self, tok_a, tok_b):
		type_a = type_b = None
		self.segments[self.curr_segment] += f"    ;; {tok_a.id} + {tok_b.id}\n"

		# Copying the first data into register
		# Getting the type of first token
		if tok_a.value in self.var_stack:
			if self.assigned_var:
				self.segments[self.curr_segment] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment] += f"    pop rax\n"
			type_a = self.var_stack[tok_a.id].name
		elif tok_a.name in data_types:
			if self.assigned_var:
				self.segments[self.curr_segment] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment] += f"    pop rax\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.id}` used for plus operation.")

		# Copying the second data into register
		# Getting the type of second token
		if tok_b.value in self.var_stack:
			self.segments[self.curr_segment] += f"    mov rbx, {self.var_stack[tok_b.id].value}\n"
			type_b = self.var_stack[tok_b.id].name
		elif tok_b.name in data_types:
			self.segments[self.curr_segment] += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.id}` used for plus operation.")

		# Adding them both
		self.segments[self.curr_segment] += f"    add rax, rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.segments[self.curr_segment] += f"    mov {self.var_stack[self.assigned_var.id].value}, rax\n"
		else:
			self.segments[self.curr_segment] += f"    push rax\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `+` operation between types `{type_a}` and `{type_b}`.")

	def __minus(self, tok_a, tok_b):
		type_a = type_b = None
		self.segments[self.curr_segment] += f"    ;; {tok_a.id} - {tok_b.id}\n"

		# Copying the first data into register
		# Getting the type of the first token
		if tok_a.value in self.var_stack:
			if self.assigned_var:
				self.segments[self.curr_segment] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment] += f"    pop rax\n"
			type_a = self.var_stack[tok_a.id].name
		elif tok_a.name in data_types:
			if self.assigned_var:
				self.segments[self.curr_segment] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment] += f"    pop rax\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.id}` used for minus operation.")

		# Copying the second data into register
		# Getting the type of sencond token
		if tok_b.value in self.var_stack:
			self.segments[self.curr_segment] += f"    mov rbx, {self.var_stack[tok_b.id].value}\n"
			type_b = self.var_stack[tok_b.id].name
		elif tok_b.name in data_types:
			self.segments[self.curr_segment] += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.id}` used for minus operation.")

		self.segments[self.curr_segment] += f"    sub rax, rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.segments[self.curr_segment] += f"    mov {self.var_stack[self.assigned_var.id].value}, rax\n"
		else:
			self.segments[self.curr_segment] += f"    push rax\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `-` operation between types `{type_a}` and `{type_b}`.")

	def __mult(self, tok_a, tok_b):
		type_a = type_b = None
		self.segments[self.curr_segment] += f"    ;; {tok_a.id} * {tok_b.id}\n"

		# Copying the first data into register
		# Getting the type of first token
		if tok_a.value in self.var_stack:
			if self.assigned_var:
				self.segments[self.curr_segment] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment] += f"    pop rax\n"
			type_a = self.var_stack[tok_a.id].name
		elif tok_a.name in data_types:
			if self.assigned_var:
				self.segments[self.curr_segment] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment] += f"    pop rax\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.id}` used for multiply operation.")

		# Copying the second data into register
		# Getting the type of second token
		if tok_b.value in self.var_stack:
			self.segments[self.curr_segment] += f"    mov rbx, {self.var_stack[tok_b.id].value}\n"
			type_b = self.var_stack[tok_b.id].name
		elif tok_b.name in data_types:
			self.segments[self.curr_segment] += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.id}` used for multiply operation.")

		self.segments[self.curr_segment] += f"    mul rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.segments[self.curr_segment] += f"    mov {self.var_stack[self.assigned_var.id].value}, rax\n"
		else:
			self.segments[self.curr_segment] += f"    push rax\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `*` operation between types `{type_a}` and `{type_b}`.")

	def __div(self, tok_a, tok_b):
		type_a = type_b = None
		self.segments[self.curr_segment] += f"    ;; {tok_a.id} / {tok_b.id}\n"

		# Copying the first data into register
		# Getting the type of the first token
		if tok_a.value in self.var_stack:
			if self.assigned_var:
				self.segments[self.curr_segment] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment] += f"    pop rax\n"
			type_a = self.var_stack[tok_a.id].name
		elif tok_a.name in data_types:
			if self.assigned_var:
				self.segments[self.curr_segment] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment] += f"    pop rax\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.id}` used for divide operation.")

		# Copying the second data into register
		# Getting the type of the second token
		if tok_b.value in self.var_stack:
			self.segments[self.curr_segment] += f"    mov rbx, {self.var_stack[tok_b.id].value}\n"
			type_b = self.var_stack[tok_b.id].name
		elif tok_b.name in data_types:
			self.segments[self.curr_segment] += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.id}` used for divide operation.")

		# Adding them both
		self.segments[self.curr_segment] += f"    xor rdx, rdx\n"
		self.segments[self.curr_segment] += f"    div rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.segments[self.curr_segment] += f"    mov {self.var_stack[self.assigned_var.id].value}, rax\n"
		else:
			self.segments[self.curr_segment] += f"    push rax\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `/` operation between types `{type_a}` and `{type_b}`.")

	def __mod(self, tok_a, tok_b):
		type_a = type_b = None
		self.segments[self.curr_segment] += f"    ;; {tok_a.id} % {tok_b.id}\n"

		# Copying the first data into register
		# Getting the type of first token
		if tok_a.value in self.var_stack:
			if self.assigned_var:
				self.segments[self.curr_segment] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment] += f"    pop rax\n"
			type_a = self.var_stack[tok_a.id].name
		elif tok_a.name in data_types:
			if self.assigned_var:
				self.segments[self.curr_segment] += f"    mov rax, {self.var_stack[tok_a.id].value}\n"
			else:
				self.segments[self.curr_segment] += f"    pop rax\n"
			type_a = tok_a.name
		else:
			error(tok_a, f"Unknown word `{tok_a.id}` used for modular division operation.")

		# Copying the second data into register
		# Getting the type of second token
		if tok_b.value in self.var_stack:
			self.segments[self.curr_segment] += f"    mov rbx, {self.var_stack[tok_b.id].value}\n"
			type_b = self.var_stack[tok_b.id].name
		elif tok_b.name in data_types:
			self.segments[self.curr_segment] += f"    mov rbx, {tok_b.value}\n"
			type_b = tok_b.name
		else:
			error(tok_b, f"Unknown word `{tok_b.id}` used for modular division operation.")

		# Adding them both
		self.segments[self.curr_segment] += f"    xor rdx, rdx\n"
		self.segments[self.curr_segment] += f"    div rbx\n"
		
		# If there is a assigned variable then storing in that else pushing it into stack
		if self.assigned_var:
			self.segments[self.curr_segment] += f"    mov {self.var_stack[self.assigned_var.id].value}, rdx\n"
		else:
			self.segments[self.curr_segment] += f"    push rdx\n"

		# Type checking
		if type_a != type_b:
			error(tok_b, f"Cannot use `/` operation between types `{type_a}` and `{type_b}`.")

	""" Conditions """
	def __equal(self):
		self.segments[self.curr_segment] += f"    ;; Equals\n"
		self.segments[self.curr_segment] += f"    mov rcx, 0\n"
		self.segments[self.curr_segment] += f"    mov rdx, 1\n"

		if self.con_var:
			self.segments[self.curr_segment] += f"    mov rbx, {self.con_var.value}\n"
			self.segments[self.curr_segment] += f"    pop rax\n"
		else:
			self.segments[self.curr_segment] += f"    pop rax\n"
			self.segments[self.curr_segment] += f"    pop rbx\n"

		self.segments[self.curr_segment] += f"    cmp rbx, rax\n"
		self.segments[self.curr_segment] += f"    cmove rcx, rdx\n"

		if self.con_var:
			self.segments[self.curr_segment] += f"    mov {self.con_var.value}, rcx\n"
		else:
			self.segments[self.curr_segment] += f"    push rcx\n"
	
		self.operation = None

	def __less_than(self):
		self.segments[self.curr_segment] += f"    ;; Less than\n"
		self.segments[self.curr_segment] += f"    mov rcx, 0\n"
		self.segments[self.curr_segment] += f"    mov rdx, 1\n"

		if self.con_var:
			self.segments[self.curr_segment] += f"    mov rbx, {self.con_var.value}\n"
			self.segments[self.curr_segment] += f"    pop rax\n"
		else:
			self.segments[self.curr_segment] += f"    pop rax\n"
			self.segments[self.curr_segment] += f"    pop rbx\n"

		self.segments[self.curr_segment] += f"    cmp rbx, rax\n"
		self.segments[self.curr_segment] += f"    cmovl rcx, rdx\n"

		if self.con_var:
			self.segments[self.curr_segment] += f"    mov {self.con_var.value}, rcx\n"
		else:
			self.segments[self.curr_segment] += f"    push rcx\n"
	
		self.operation = None

	def __greater_than(self):
		self.segments[self.curr_segment] += f"    ;; Greater than\n"
		self.segments[self.curr_segment] += f"    mov rcx, 0\n"
		self.segments[self.curr_segment] += f"    mov rdx, 1\n"

		if self.con_var:
			self.segments[self.curr_segment] += f"    mov rbx, {self.con_var.value}\n"
			self.segments[self.curr_segment] += f"    pop rax\n"
		else:
			self.segments[self.curr_segment] += f"    pop rax\n"
			self.segments[self.curr_segment] += f"    pop rbx\n"

		self.segments[self.curr_segment] += f"    cmp rbx, rax\n"
		self.segments[self.curr_segment] += f"    cmovg rcx, rdx\n"

		if self.con_var:
			self.segments[self.curr_segment] += f"    mov {self.con_var.value}, rcx\n"
		else:
			self.segments[self.curr_segment] += f"    push rcx\n"
	
		self.operation = None

	def __less_than_equal(self):
		self.segments[self.curr_segment] += f"    ;; Less than equal\n"
		self.segments[self.curr_segment] += f"    mov rcx, 0\n"
		self.segments[self.curr_segment] += f"    mov rdx, 1\n"

		if self.con_var:
			self.segments[self.curr_segment] += f"    mov rbx, {self.con_var.value}\n"
			self.segments[self.curr_segment] += f"    pop rax\n"
		else:
			self.segments[self.curr_segment] += f"    pop rax\n"
			self.segments[self.curr_segment] += f"    pop rbx\n"

		self.segments[self.curr_segment] += f"    cmp rbx, rax\n"
		self.segments[self.curr_segment] += f"    cmovle rcx, rdx\n"

		if self.con_var:
			self.segments[self.curr_segment] += f"    mov {self.con_var.value}, rcx\n"
		else:
			self.segments[self.curr_segment] += f"    push rcx\n"
	
		self.operation = None

	def __greater_than_equal(self):
		self.segments[self.curr_segment] += f"    ;; Greater than equal\n"
		self.segments[self.curr_segment] += f"    mov rcx, 0\n"
		self.segments[self.curr_segment] += f"    mov rdx, 1\n"

		if self.con_var:
			self.segments[self.curr_segment] += f"    mov rbx, {self.con_var.value}\n"
			self.segments[self.curr_segment] += f"    pop rax\n"
		else:
			self.segments[self.curr_segment] += f"    pop rax\n"
			self.segments[self.curr_segment] += f"    pop rbx\n"

		self.segments[self.curr_segment] += f"    cmp rbx, rax\n"
		self.segments[self.curr_segment] += f"    cmovge rcx, rdx\n"

		if self.con_var:
			self.segments[self.curr_segment] += f"    mov {self.con_var.value}, rcx\n"
		else:
			self.segments[self.curr_segment] += f"    push rcx\n"
	
		self.operation = None
	
	def __not_equal(self):
		self.segments[self.curr_segment] += f"    ;; Not equal\n"
		self.segments[self.curr_segment] += f"    mov rcx, 0\n"
		self.segments[self.curr_segment] += f"    mov rdx, 1\n"

		if self.con_var:
			self.segments[self.curr_segment] += f"    mov rbx, {self.con_var.value}\n"
			self.segments[self.curr_segment] += f"    pop rax\n"
		else:
			self.segments[self.curr_segment] += f"    pop rax\n"
			self.segments[self.curr_segment] += f"    pop rbx\n"

		self.segments[self.curr_segment] += f"    cmp rbx, rax\n"
		self.segments[self.curr_segment] += f"    cmovne rcx, rdx\n"

		if self.con_var:
			self.segments[self.curr_segment] += f"    mov {self.con_var.value}, rcx\n"
		else:
			self.segments[self.curr_segment] += f"    push rcx\n"
	
		self.operation = None

	""" Special keywords """
	def __print(self, params):
		param_idx = 0
		while param_idx < len(params):
			val = params[param_idx]
			
			if val.name in OPERATOR:
				error(val, "Cannot use operators in print functions")
			elif val.id == NEW_LINE:
				self.segments[self.curr_segment] += f"    ;; Newline\n"
				self.segments[self.curr_segment] += f"    puts nl, 1\n\n"
				param_idx += 1
			elif val.id in self.var_stack:
				var = self.var_stack[val.value]
				if var.name == INT or var.name == FLOAT:
					self.segments[self.curr_segment] += f"    ;; print {var.id}\n"
					self.segments[self.curr_segment] += f"    mov rdi, {var.value}\n"
					self.segments[self.curr_segment] += f"    call print\n\n"
				elif var.name == STR:
					self.segments[self.curr_segment] += f"    ;; Puts {val.id}\n"
					self.segments[self.curr_segment] += f"    puts {val.id}, {val.id}_len_6969\n\n"
				param_idx += 1
			elif val.name in data_types:
				if val.name == INT or val.name == FLOAT:
					self.segments[self.curr_segment] += f"    ;; print {val.value}\n"
					self.segments[self.curr_segment] += f"    mov rdi, {val.value}\n"
					self.segments[self.curr_segment] += f"    call print\n\n"
				elif val.name == STR:
					self.segments["data"] += f"    str_{self.str_cnt}: dw {val.value}\n"
					self.segments["data"] += f"    str_{self.str_cnt}_len_6969 equ $ - str_{self.str_cnt}\n"
	
					self.segments[self.curr_segment] += f"    ;; Puts {val.value}\n"
					self.segments[self.curr_segment] += f"    puts str_{self.str_cnt}, str_{self.str_cnt}_len_6969\n\n"
	
					self.str_cnt += 1
				param_idx += 1
			else:
				error(val, f"Unknown word \'{val.value}\'");
	
	def __return(self):
		self.segments[self.curr_segment] += f"    pop rax\n"
		#TODO: Add a proper return system
		self.segments[self.curr_segment] += f"    mov rbp, rsp\n"
		self.segments[self.curr_segment] += f"    pop rbp\n"
		self.segments[self.curr_segment] += f"    ret\n"
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
									self.segments[self.curr_segment] += f"    ;; Pushing {variable.id}\n"
									self.segments[self.curr_segment] += f"    mov rax, {variable.value}\n"
									self.segments[self.curr_segment] += f"    push rax\n"
							else:
								# Pushing onto the stack
								self.segments[self.curr_segment] += f"    ;; Pushing {variable.id}\n"
								self.segments[self.curr_segment] += f"    mov rax, {variable.value}\n"
								self.segments[self.curr_segment] += f"    push rax\n"
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
						self.segments[self.curr_segment] += f"    ;; Pushing {token.value}\n"
						self.segments[self.curr_segment] += f"    push {token.value}\n"

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
						self.segments[self.curr_segment] += f"    ;; {var.id}++\n"
						self.segments[self.curr_segment] += f"    pop rax\n"
						self.segments[self.curr_segment] += f"    inc rax\n"
						self.segments[self.curr_segment] += f"    mov {var.value}, rax\n"
						self.token_cnt += 1

					elif token.value == DEC:
						var = self.line[self.token_cnt - 1]
						if self.token_cnt == 0:
							error(var, f"Token `{var.value}` requires one operand.")
						if var.value not in self.var_stack:
							error(var, f"Undefined reference to word `{var.value}`.")

						var = self.var_stack[var.value]
						self.segments[self.curr_segment] += f"    ;; {var.id}--\n"
						self.segments[self.curr_segment] += f"    pop rax\n"
						self.segments[self.curr_segment] += f"    dec rax\n"
						self.segments[self.curr_segment] += f"    mov {var.value}, rax\n"
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

				elif token.name == KEYWORD:

					if token.value == PRINT:
						params = self.line[self.token_cnt + 1:]
						self.token_cnt = len(self.line)
						self.__print(params)

					elif token.value == IF:
						self.token_cnt += 1
						self.addr_cnt = len(self.addr_stack)

						new_addr = Addr(IF, None, self.addr_cnt, False, False)
						self.addr_stack.append(new_addr)
						self.segments[self.curr_segment] += f"    ;; If\n"
						self.segments[self.curr_segment] += f"addr_{self.addr_stack[self.addr_cnt].id}_if:\n"
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
						self.segments[self.curr_segment] += f"    ;; Then\n"
						self.segments[self.curr_segment] += f"    pop rax\n"
						self.segments[self.curr_segment] += f"    cmp rax, 1\n"
						self.segments[self.curr_segment] += f"    je  addr_{self.addr_stack[self.addr_cnt].id}_then\n"
						self.segments[self.curr_segment] += f"    jne addr_{self.addr_stack[self.addr_cnt].id}_else\n"

						self.segments[self.curr_segment] += f"addr_{self.addr_stack[self.addr_cnt].id}_then:\n"

					elif token.value == ELSE:
						self.__end_scope()
						self.__start_scope()
						self.token_cnt += 1
						self.segments[self.curr_segment] += f"    jmp addr_{self.addr_stack[self.addr_cnt].id}_end\n"
						self.segments[self.curr_segment] += f"addr_{self.addr_stack[self.addr_cnt].id}_else:\n"

					elif token.value == END:
						self.__end_scope()

						self.token_cnt += 1
						addr = self.addr_stack[self.addr_cnt]
						if addr.type == IF:
							self.segments[self.curr_segment] += f"    jmp addr_{addr.id}_end\n"
							self.segments[self.curr_segment] += f"addr_{addr.id}_end:\n"
						elif addr.type == WHILE:
							self.segments[self.curr_segment] += f"    jmp addr_{addr.id}_while\n"
							self.segments[self.curr_segment] += f"addr_{addr.id}_end:\n"
						elif addr.type == FUNC:
							if not addr.start:
								error(self.func_stack[addr.name], f"Missing `in` token in function `{addr.name}`.")
							self.segments[self.curr_segment] += f"    push 0\n"
							self.segments[self.curr_segment] += f"    pop rax\n"
							self.segments[self.curr_segment] += f"    mov rbp, rsp\n"
							self.segments[self.curr_segment] += f"    pop rbp\n"
							self.segments[self.curr_segment] += f"    ret\n"
							self.curr_segment = "text"
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
						self.__start_scope()
						self.token_cnt += 1
						self.addr_cnt = len(self.addr_stack)

						new_addr = Addr(WHILE, None, self.addr_cnt, False, False)
						self.addr_stack.append(new_addr)
						self.segments[self.curr_segment] += f"    ;; While\n"
						self.segments[self.curr_segment] += f"addr_{self.addr_stack[self.addr_cnt].id}_while:\n"

					elif token.value == DO:
						self.__end_scope()
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
						self.segments[self.curr_segment] += f"    ;; Do\n"
						self.segments[self.curr_segment] += f"    pop rax\n"
						self.segments[self.curr_segment] += f"    cmp rax, 1\n"
						self.segments[self.curr_segment] += f"    je  addr_{self.addr_stack[self.addr_cnt].id}_do\n"
						self.segments[self.curr_segment] += f"    jne addr_{self.addr_stack[self.addr_cnt].id}_end\n"

						self.segments[self.curr_segment] += f"addr_{self.addr_stack[self.addr_cnt].id}_do:\n"

					elif token.value == FUNC:
						self.__start_scope()

						# Telling the compiler we encountered a function
						self.curr_segment = "func"

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

						self.segments[self.curr_segment] += f";; {new_func.name}\n"
						self.segments[self.curr_segment] += new_func.id + ":\n" 
						self.segments[self.curr_segment] += f"    push rbp\n"
						self.segments[self.curr_segment] += f"    mov rbp, rsp\n"

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


						self.segments[self.curr_segment] += f"    ;; Call {self.called_func[-1]}\n"
						self.segments[self.curr_segment] += f"    call {self.func_stack[self.called_func[-1]].id}\n"

						# Poping the parameters of the function
						for i in range(len(self.func_stack[self.called_func[-1]].params)):
							self.segments[self.curr_segment] += f"    pop rbx\n"

						if self.assigned_var:
							self.segments[self.curr_segment] += f"    mov {self.assigned_var.value}, rax\n"
						else:
							self.segments[self.curr_segment] += f"    push rax\n"
							self.ret_stack += 1

						self.called_func.pop()

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
