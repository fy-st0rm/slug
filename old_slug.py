import sys
import os

# Data types
INT = "int"
STR = "str"
FLOAT = "float"
data_types = [INT, STR, FLOAT]

# Operators
PLUS  = "+"
MINUS = "-"
MULT  = "*"
DIV   = "/"
EQUAL = "="
operators = [PLUS, MINUS, MULT, DIV]

var_stack = {}

class Variable:
	def __init__(self, name, type, value):
		self.name = name	
		self.type = type
		self.value = value
	
	def get_val(self):
		if self.type == STR:
			return f"\"{self.value}\""
		elif self.type == INT:
			return str(self.value)

class Token:
	def __init__(self, type, value):
		self.type = type
		self.value = value


def error(msg):
	assert False, msg

def is_float(val):
	try:
		float(val)
		return True
	except ValueError:
		return False

def create_token(val):
	if val.isdigit():
		return Token(INT, int(val))
	elif is_float(val):
		return Token(FLOAT, float(val))
	elif val[0] == "\"" and val[-1] == "\"":
		val = val[1::]
		val = val[:-1:]
		return Token(STR, val)

def calc_operation(op, a, b):
	if op == PLUS:
		if a.type == INT or a.type == FLOAT:
			return a.value + b.value
		else:
			error(f"Cannot perform \"{op}\" in type \"{a.type}\".")
	elif op == MINUS:
		if a.type == INT or a.type == FLOAT:
			return a.value - b.value
		else:
			error(f"Cannot perform \"{op}\" in type \"{a.type}\".")
	elif op == MULT:
		if a.type == INT or a.type == FLOAT:
			return a.value * b.value
		else:
			error(f"Cannot perform \"{op}\" in type \"{a.type}\".")
	elif op == DIV:
		if a.type == INT or a.type == FLOAT:
			return a.value / b.value
		else:
			error(f"Cannot perform \"{op}\" in type \"{a.type}\".")

def simulate_code(code):
	lines = code.split("\n")
	for line in lines:
		# TODO : Make spliting by tabs as well
		tokens = line.split(" ")
		tokens = list(filter(bool, tokens))
		index = 0

		while index < len(tokens):
			# Parsing the variable declarations
			if tokens[index] in data_types:
				type = tokens[index]
				name = tokens[index + 1]
				index += 2
				var = Variable(name, type, None)

				if name not in var_stack:
					var_stack[name] = var
				else:
					error(f"Redeclaration of variable \"{name}\"")
			
			# Checking for the assign operator
			elif tokens[index] == EQUAL:
				name = tokens[index - 1]
				index += 1
				value = tokens[index:]
				index = len(tokens)

				# Checking if the assigned variable is already in stack or not
				if name not in var_stack:
					error(f"Variable \"{name}\" not defined")
				
				if len(value) <= 0:
					error(f"Value to assign not found.")

				val_index = 0
				var = var_stack[name]

				while val_index < len(value):
					val = value[val_index]

					# If the assigned value is a variable
					if val in var_stack:
						new_val = create_token(var_stack[val].get_val())
						if (var.type == new_val.type):
							var.value = new_val.value
							val_index += 1
						else:
							error(f"Cannot assign \"{new_val.type}\" to variable with \"{var.type}\" data type.")

					# If there are operators inside the assigned value
					elif val in operators:
						val_index += 1
						a = create_token(var.get_val())
						b = create_token(value[val_index])
						var.value = calc_operation(val, a, b)
						val_index += 1
					else:
						# Getting the strings
						if val[0] == "\"" and val[-1] != "\"":
							val_index += 1
							for i in range(val_index, len(value)):
								val += " " + value[i]
								val_index += 1
								if value [i][-1] == "\"":
									val_index -= 1
									break

						new_val = create_token(val)
						if new_val:
							if var.type == new_val.type:
								var.value = new_val.value
								val_index += 1
							else:
								error(f"Cannot assign \"{new_val.type}\" to variable with \"{var.type}\" data type.")
						else:
							error(f"Unknown world {val}")
				
			elif tokens[index] == "print":
				index += 1
				params = tokens[index:]
				index = len(tokens)
				param_idx = 0

				while param_idx < len(params):
					val = params[param_idx]

					if val in operators:
						error("Cannot use operators in print functions")
					elif val in var_stack:
						print(var_stack[val].value, end=" ")
					elif val == ",":
						print("")
					else:
						# Getting the strings
						if val[0] == "\"" and val[-1] != "\"":
							param_idx += 1
							for i in range(param_idx, len(params)):
								val += " " + params[i]
								param_idx += 1
								if params[i][-1] == "\"":
									param_idx -= 1
									break

						token = create_token(val)
						if token:
							print(token.value, end=" ")
						else:
							error(f"Unknown word {val}")
					param_idx += 1

			elif tokens[index] in var_stack:
				index += 1
			else:
				printf(f"Unknown word {tokens[index]}")

def compile_code(code):
	file_name = sys.argv[2].strip(".slug") + ".asm"
	obj_file = file_name.strip(".asm") + ".o"
	exe_file = file_name.strip(".asm")
	out_file = open(file_name, "w")

	data_segment =  "section .data\n"
	data_segment += "    nl dw 10\n"
	bss_segment = "section .bss\n"
	
	print_macro =  "%macro print 2\n"
	print_macro += "    mov   eax, 4\n"
	print_macro += "    mov   ebx, 1\n"
	print_macro += "    mov   ecx, %1\n"
	print_macro += "    mov   edx, %2\n"
	print_macro += "    int   80h\n"
	print_macro += "%endmacro\n"

	text_segment = "section .text\n"
	text_segment += "    global _start\n"
	text_segment += "_start:\n"

	exit_segment =  "exit:\n"
	exit_segment += "    mov eax, 1\n"
	exit_segment += "    mov ebx, 0\n"
	exit_segment += "    int 80h\n"

	lines = code.split("\n")
	str_cnt = 0

	for line in lines:
		# TODO : Make spliting by tabs as well
		tokens = line.split(" ")
		tokens = list(filter(bool, tokens))
		index = 0

		while index < len(tokens):
			# Parsing the variable declarations
			if tokens[index] in data_types:
				type = tokens[index]
				name = tokens[index + 1]
				index += 2
				var = Variable(name, type, None)

				if name not in var_stack:
					var_stack[name] = var
					data_segment += f"	{name} db"
				else:
					error(f"Redeclaration of variable \"{name}\"")

			# Checking for the assign operator
			#TODO PROPERLY HANDLE THE EQUAL THEN PRE CALULATING THE VALUES IN COMPILED ONE
			elif tokens[index] == EQUAL:
				name = tokens[index - 1]
				index += 1
				value = tokens[index:]
				index = len(tokens)

				# Checking if the assigned variable is already in stack or not
				if name not in var_stack:
					error(f"Variable \"{name}\" not defined")
				
				if len(value) <= 0:
					error(f"Value to assign not found.")

				val_index = 0
				var = var_stack[name]

				while val_index < len(value):
					val = value[val_index]

					# If the assigned value is a variable
					if val in var_stack:
						new_val = create_token(var_stack[val].get_val())
						if (var.type == new_val.type):
							var.value = new_val.value
							text_segment += f"    mov rax, [{val}]\n"
							text_segment += f"    mov [{var}], rax\n"
							val_index += 1
						else:
							error(f"Cannot assign \"{new_val.type}\" to variable with \"{var.type}\" data type.")

					# If there are operators inside the assigned value
					elif val in operators:
						val_index += 1
						a = create_token(var.get_val())
						b = create_token(value[val_index])
						var.value = calc_operation(val, a, b)
						
						text_segment += f"    edx, {var}\n"
						text_segment += f"    call atoi\n"

						val_index += 1
					else:
						# Getting the strings
						if val[0] == "\"" and val[-1] != "\"":
							val_index += 1
							for i in range(val_index, len(value)):
								val += " " + value[i]
								val_index += 1
								if value [i][-1] == "\"":
									val_index -= 1
									break

						new_val = create_token(val)
						if new_val:
							if var.type == new_val.type:
								var.value = new_val.value
								final_value = var.value
								val_index += 1
							else:
								error(f"Cannot assign \"{new_val.type}\" to variable with \"{var.type}\" data type.")
						else:
							error(f"Unknown world {val}")

				# Adding the final value to the data segment
				data_segment += f"\'{final_value}\'\n"

			# Handling print TODO: Maintain proper print function 
			elif tokens[index] == "print":
				index += 1
				params = tokens[index:]
				index = len(tokens)
				param_idx = 0

				while param_idx < len(params):
					val = params[param_idx]

					if val in operators:
						error("Cannot use operators in print functions")
					elif val in var_stack:
						text_segment += f"    print {val}, {len(var_stack[val].get_val())}\n"
					elif val == ",":
						text_segment += "    print nl, 1\n"
					else:
						# Getting the strings
						if val[0] == "\"" and val[-1] != "\"":
							param_idx += 1
							for i in range(param_idx, len(params)):
								val += " " + params[i]
								param_idx += 1
								if params[i][-1] == "\"":
									param_idx -= 1
									break

						token = create_token(val)
						if token:
							data_segment += f"    str_{str_cnt} dw \"{token.value}\"\n"
							text_segment += f"    print str_{str_cnt}, {len(val)}\n"
							str_cnt += 1
						else:
							error(f"Unknown word {val}")
					param_idx += 1

			elif tokens[index] in var_stack:
				index += 1
			else:
				error(f"Unknown word {tokens[index]}")

	out_file.write(print_macro)
	out_file.write("\n")
	out_file.write(data_segment)
	out_file.write("\n")
	out_file.write(bss_segment)
	out_file.write("\n")
	out_file.write(text_segment)
	out_file.write("\n")
	out_file.write(exit_segment)

	out_file.close()

	os.system(f"nasm -felf64 {file_name}")
	os.system(f"ld -o {exe_file} {obj_file}")

def usage():
	print("slug [cmd] [filename]")
	print("cmds: sim  -- simulates code")
	print("      comp -- compiles code")

if __name__ == "__main__":
	if len(sys.argv) <= 2:
		usage()
		exit(1)
	
	mode = sys.argv[1]
	file_name = sys.argv[2]
	if file_name.split(".")[-1] != "slug":
		print("Only supports file with extention \".slug\"")
		exit(1)

	with open(file_name, "r") as file:
		code = file.read()
	
	if mode == "sim":
		simulate_code(code)
	elif mode == "com":
		compile_code(code)
	else:
		usage()
		print("ERROR: Unkown cmd")
		exit(1)

