"""
The idea here is to let the agent hallucinate its own tools and have them
dynamically registered. Probably not a good idea...
"""

from gremllm import Gremllm

# Remind me to not shop at your store
cart = Gremllm('shopping_cart')
cart.add_item('apple', 1.50)
cart.add_item('banana', 0.75)
total = cart.calculate_total()
print(f"Cart contents: {cart.contents_as_json()}")
print(f"Cart total: {total}")
cart.clear()

