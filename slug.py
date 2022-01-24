import sys

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
EQUAL = "="
OPERATOR = "operator"
operators = [EQUAL, PLUS, MINUS, MULT, DIV]

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
	while i < len(words):
		if words[i] in data_types:
			program.append(Token(DATA_TYPE, words[i]))
		elif words[i] in operators:
			program.append(Token(OPERATOR, words[i]))
		elif words[i].isdigit():
			program.append(Token(INT, words[i]))
		elif is_float(words[i]):
			program.append(Token(FLOAT, words[i]))
		elif words[i][0] == "\"" and words[i][-1] == "\"":
			program.append(Token(STR, words[i]))
		elif words[i][0] == "\"":
			word = words[i] 
			while word[-1] != "\"":
				i += 1
				word += " " + words[i]
			program.append(Token(STR, word))
		else:
			program.append(Token(WORD, words[i]))
		i += 1

def simulate_code(program):
	pass

def compile_code(file_name, program):
	pass

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
	print(program)

