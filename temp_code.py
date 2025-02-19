
# Python program for a simple console calculator

def calculate(expression):
    return eval(expression)

if __name__ == '__main__':
    input_expression = input("Enter an arithmetic expression: ")
    try:
        result = calculate(input_expression)
        print("Result:", result)
    except Exception as e:
        print("Error in expression:", e)