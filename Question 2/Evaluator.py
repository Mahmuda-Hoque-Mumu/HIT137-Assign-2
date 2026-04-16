tokens = []
pos = 0


# ==========================
# Converts input string into a list of tokens where every token represent numbers, operators, or parentheses.
# ==========================
def tokenizer(data):
    token = []
    i = 0
    n = len(data)
    while i < n:
        char = data[i]
        # Passing over empty spaces
        if char.isspace():
            i += 1
            continue
        # Extract numeric values
        if char.isdigit():
            start = i
            while i < n and data[i].isdigit():
                i += 1
            token.append(f"[NUM:{data[start:i]}]")
            continue
        # Arithmetic operators
        if char in "+-*/":
            token.append(f"[OP:{char}]")
            i += 1
            continue
        # Left parenthesis token
        if char == "(":
            token.append("[LPAREN:(]")
            i += 1
            continue
        # Right parenthesis token
        if char == ")":
            token.append("[RPAREN:)]")
            i += 1
            continue

        # Errors handling
        return "ERROR"

    # End marker token
    token.append("[END]")
    return token


# =========================
# Functions for navigation of tokens
# =========================

# Return the current token without progressing the pointer
def current():
    if pos < len(tokens):
        return tokens[pos]
    return "[END]"


# Advance the token pointer to the next token
def advance():
    global pos
    pos += 1

def expect_end():
    return current() == "[END]"

# =========================
# PARSER that builds a tree from tokens
# =========================

# Handle addition and subtraction
def parse_expression():
    tree = parse_term()
    if tree == "ERROR":
        return "ERROR"

    # Process + and - operators with
    while current().startswith("[OP:+]") or current().startswith("[OP:-]"):
        op = current()[4]
        advance()
        right = parse_term()

        if right == "ERROR":
            return "ERROR"
        tree = (op, tree, right)
    return tree

# Handle multiplication, division, and implicit multiplication
def parse_term():
    tree = parse_factor()
    if tree == "ERROR":
        return "ERROR"
    while True:
        tok = current()
        # Explicit multiplication or division
        if tok.startswith("[OP:*]") or tok.startswith("[OP:/]"):
            op = tok[4]
            advance()
            right = parse_factor()
            if right == "ERROR":
                return "ERROR"
            tree = (op, tree, right)
            continue

        # Implicit multiplication handling
        # Apply when number or closing parenthesis is followed by number or opening parenthesis
        if (
            tok.startswith("[NUM:")
            or tok.startswith("[LPAREN")
        ):
            tree = ("*", tree, parse_factor())
            continue
        break
    return tree


# Handling unary operators such as negation
def parse_factor():
    tok = current()
    # Unary minus operator
    if tok.startswith("[OP:-]"):
        advance()
        operand = parse_factor()
        if operand == "ERROR":
            return "ERROR"
        return ("neg", operand)

    # Unary plus is not supported
    if tok.startswith("[OP:+]"):
        return "ERROR"
    return parse_atom()

# Handling numeric values and parenthesized expressions
def parse_atom():
    tok = current()
    # Numeric
    if tok.startswith("[NUM:"):
        advance()
        return ("num", int(tok[5:-1]))

    # Parenthesized expression
    if tok.startswith("[LPAREN"):
        advance()
        tree = parse_expression()
        if tree == "ERROR":
            return "ERROR"
        if not current().startswith("[RPAREN"):
            return "ERROR"
        advance()
        return tree
    return "ERROR"


# =========================
# Computing the value of the Tree
# =========================
def eval_tree(tree):
    if tree == "ERROR":
        return "ERROR"
    # Numeric tree
    if tree[0] == "num":
        return tree[1]
    # Unary negation tree
    if tree[0] == "neg":
        v = eval_tree(tree[1])
        return "ERROR" if v == "ERROR" else -v
    left = eval_tree(tree[1])
    right = eval_tree(tree[2])
    if left == "ERROR" or right == "ERROR":
        return "ERROR"
    op = tree[0]

    # Binary operations
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        if right == 0:
            return "ERROR"
        return left / right
    return "ERROR"


# =========================
# FORMATTING
# Converting the three and results into readable output
# =========================

# Convert the Tree into a structured string representation
def format_tree(tree):
    if tree == "ERROR":
        return "ERROR"
    if tree[0] == "num":
        return str(tree[1])
    if tree[0] == "neg":
        return f"(neg {format_tree(tree[1])})"
    return f"({tree[0]} {format_tree(tree[1])} {format_tree(tree[2])})"


# Format final evaluation result for display
def format_result(val):
    if val == "ERROR":
        return "ERROR"
    # Convert floating integers to integer format
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return str(round(val, 4))

# =======================
# MAIN
# Reads input files, processes expressions, and writes outputs
# =======================
def evaluate_file(input_path: str):
    global tokens, pos
    results = []
    output = []

    # =========================
    # Safe file loading
    # =========================
    try:
        with open(input_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"ERROR: File '{input_path}' not found.")
        return []   # or return a structured error if your assignment expects it

    for line in lines:
        line = line.strip()

        tokens = tokenizer(line)
        pos = 0

        tree = parse_expression()

        if tree == "ERROR" or not expect_end():
            tree_out = "ERROR"
            result_out = "ERROR"
            tok_out = "ERROR"
        else:
            value = eval_tree(tree)
            if value == "ERROR":
                tree_out = "ERROR"
                result_out = "ERROR"
            else:
                tree_out = format_tree(tree)
                result_out = format_result(value)

            tok_out = " ".join(tokens)

        results.append({
            "input": line,
            "tree": tree_out,
            "tokens": tok_out,
            "result": result_out
        })

        output.append(
            f"Input: {line}\n"
            f"Tree: {tree_out}\n"
            f"Tokens: {tok_out}\n"
            f"Result: {result_out}\n"
        )
        output.append("")

    with open("output.txt", "w") as f:
        f.write("\n".join(output))

    return results

# Program's entry point
if __name__ == "__main__":
    evaluate_file("input_text.txt")