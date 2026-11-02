from src.optimizer.model import priority, value

print(value(priority(1.0, 0.2), 30))
print(value(priority(1.0, 0.2), 60))