# this script serves testing purposes

from blablado import Assistant
assistant = Assistant()

def compute_sum(a:int, b:int):
    """Sums two numbers"""
    print(f"summing {a} and {b}...")
    return a + b

assistant.register_tool(compute_sum)

assistant.do("add 5 plus 4")

assistant.microphone_index = 3
assistant.listen()
