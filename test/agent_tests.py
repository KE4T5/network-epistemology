from src.epinet.agent import Agent

# TODO: rewrite to python test
a = Agent(1, 0.59, [])
print(a.credence)
a.update_credence(20, 12, 0.1)
print(a.credence)