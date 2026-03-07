class CalculatorNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "number1": ("FLOAT", {"default": 0.0}),
                "number2": ("FLOAT", {"default": 0.0}),
                "operation": ("STRING", ),
                #"operation": (["+", "-", "*", "/", "%"], ),
            }
        }

    RETURN_TYPES = ("STRING",)
    #RETURN_TYPES = ("*",)
    FUNCTION = "calculate"
    CATEGORY = "SBCODE"

    def calculate(self, number1, number2, operation):
        try:
            if operation == "+":
                result = number1 + number2
            elif operation == "-":
                result = number1 - number2
            elif operation == "*":
                result = number1 * number2
            elif operation == "/":
                if number2 == 0:
                    return ("Error: Division by zero",)
                result = number1 / number2
            elif operation == "%":
                result = number1 % number2
            else:
                return ("Error: Unknown operation",)

            return (f"Result: {result}",)
        except Exception as e:
            return (f"Error: {str(e)}",)

