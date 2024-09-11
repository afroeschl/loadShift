import random
import csv
import numpy as np
from numba import jit, prange
import time

# Constants
POPULATION_SIZE = 200
GENERATIONS = 1000
MUTATION_RATE = 0.1     # Chance of Mutation
NUM_BUY_SELL = 14       # Enforce 14 buy and 14 sell actions
GROUP_SIZE = 96         # Number of prices grouped to one cycle
NET_FEE = 18            # Fee for using the energy network (18$/MWh)

@jit(nopython=True)
def calculate_profit(actions, prices):      # Calculate profit according to actions and prices
    capacity = 40       # Battery capacity at start/end of each cycle
    totalProfit = 0
    transactions = []
    for i in range(len(actions)):
        if actions[i] == 1 and capacity <= 80:  # 1 for buy
            capacity += 20
            totalProfit -= prices[i]
            totalProfit -= NET_FEE
        elif actions[i] == 2 and capacity >= 20:  # 2 for sell
            capacity -= 20
            totalProfit += prices[i]

        transactions.append((prices[i], actions[i], capacity, totalProfit))

    return totalProfit, transactions

# Ensure that the individual has exactly 14 buys and 14 sells
def enforce_buy_sell_constraint(individual):
    buy_indices = np.where(individual == 1)[0]
    sell_indices = np.where(individual == 2)[0]
    non_action_indices = np.where(individual == 0)[0]

    # If there are more than 14 buys, we randomly reset excess buys
    while len(buy_indices) > NUM_BUY_SELL:
        excess_buy = random.choice(buy_indices)
        individual[excess_buy] = 0
        buy_indices = np.where(individual == 1)[0]

    # If there are fewer than 14 buys, we randomly convert non-actions to buys
    while len(buy_indices) < NUM_BUY_SELL:
        new_buy = random.choice(non_action_indices)
        individual[new_buy] = 1
        non_action_indices = np.where(individual == 0)[0]
        buy_indices = np.where(individual == 1)[0]

    # If there are more than 14 sells, we randomly reset excess sells
    while len(sell_indices) > NUM_BUY_SELL:
        excess_sell = random.choice(sell_indices)
        individual[excess_sell] = 0
        sell_indices = np.where(individual == 2)[0]

    # If there are fewer than 14 sells, we randomly convert non-actions to sells
    while len(sell_indices) < NUM_BUY_SELL:
        new_sell = random.choice(non_action_indices)
        individual[new_sell] = 2
        non_action_indices = np.where(individual == 0)[0]
        sell_indices = np.where(individual == 2)[0]

    return individual

# Create individual with exactly 14 buy and 14 sell actions
def create_individual(prices_len):
    actions = np.zeros(prices_len, dtype=np.int32)
    buy_indices = random.sample(range(prices_len), NUM_BUY_SELL)
    sell_indices = random.sample([i for i in range(prices_len) if i not in buy_indices], NUM_BUY_SELL)

    for b in buy_indices:
        actions[b] = 1  # 1 for buy
    for s in sell_indices:
        actions[s] = 2  # 2 for sell
    return actions

# Mutate individual while maintaining the exact 14 buy and 14 sell actions
def mutate(individual):
    if random.random() < MUTATION_RATE:
        buy_indices = [i for i, action in enumerate(individual) if action == 1]
        sell_indices = [i for i, action in enumerate(individual) if action == 2]
        non_action_indices = [i for i, action in enumerate(individual) if action == 0]

        # Mutate buys or sells but keep the counts of 14 buys and 14 sells intact
        if random.random() < 0.5 and non_action_indices:
            # Mutate a buy action
            new_buy = random.choice(non_action_indices)
            old_buy = random.choice(buy_indices)
            individual[old_buy] = 0
            individual[new_buy] = 1
        elif non_action_indices:
            # Mutate a sell action
            new_sell = random.choice(non_action_indices)
            old_sell = random.choice(sell_indices)
            individual[old_sell] = 0
            individual[new_sell] = 2

    # Enforce that after mutation, we still have 14 buys and 14 sells
    return enforce_buy_sell_constraint(individual)

# Crossover ensures resulting individuals still have 14 buys and 14 sells
def crossover(parent1, parent2):
    crossover_point = random.randint(0, len(parent1) - 1)
    child1 = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
    child2 = np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))

    # Enforce that after crossover, both children have 14 buys and 14 sells
    return enforce_buy_sell_constraint(child1), enforce_buy_sell_constraint(child2)

@jit(nopython=True, parallel=True)
def evaluate_population(population, prices):
    fitness_scores = np.zeros(len(population))
    for i in prange(len(population)):
        fitness_scores[i] = calculate_profit(population[i], prices)[0]
    return fitness_scores


def genetic_algorithm(prices):
    population = [create_individual(len(prices)) for _ in range(POPULATION_SIZE)]

    for generation in range(GENERATIONS):
        # Evaluate fitness scores
        fitness_scores = evaluate_population(np.array(population), np.array(prices))

        # Convert fitness_scores to a list of scalars if it is a numpy array
        if isinstance(fitness_scores, np.ndarray):
            fitness_scores = fitness_scores.tolist()

        # Ensure fitness_scores and population are zipped together and sorted
        sorted_population = sorted(zip(fitness_scores, population), key=lambda x: x[0], reverse=True)
        population = [ind for _, ind in sorted_population]

        next_generation = population[:POPULATION_SIZE // 2]

        while len(next_generation) < POPULATION_SIZE:
            parent1, parent2 = random.sample(population[:POPULATION_SIZE // 2], 2)
            child1, child2 = crossover(parent1, parent2)
            next_generation.append(mutate(child1))
            next_generation.append(mutate(child2))

        population = next_generation

    best_individual = max(population, key=lambda x: calculate_profit(x, prices)[0])
    best_profit, transactions = calculate_profit(best_individual, prices)
    time.sleep(10)
    return best_individual, best_profit, transactions


def main(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        prices = [float(row[0].strip()) for row in reader]

    price_groups = [prices[i:i + GROUP_SIZE] for i in range(0, len(prices), GROUP_SIZE)]
    all_results = []
    total_profit = 0

    for day, group in enumerate(price_groups):
        best_individual, best_profit, transactions = genetic_algorithm(group)
        num_buys = np.sum(np.array(best_individual) == 1)
        num_sells = np.sum(np.array(best_individual) == 2)

        all_results.append((day, best_profit, num_buys, num_sells, transactions))

        print(f"Day {day + 1}")
        print(f"Profit: {round(best_profit*0.5,3)}\n")
        total_profit += best_profit*0.5

    print(f"Total Profit: {round(total_profit,3)}")

    # Write all results to CSV
    with open('output/tradingStrategy.csv', 'w', newline='') as csvfile:
        fieldnames = ['Day', 'Price', 'Action', 'Capacity', 'Current Profit', 'Daily Profit']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for day, best_profit, num_buys, num_sells, transactions in all_results:
            profit = f"Day {day+1} Profit: {best_profit} €"
            for price, action, capacity, cumulative_profit in transactions:
                row_data = {'Day': f"Day {day + 1}", 'Price': price, 'Action': action, 'Capacity': f"{capacity}%", 'Current Profit': cumulative_profit, 'Daily Profit' : profit}
                writer.writerow(row_data)
                profit = ''

if __name__ == "__main__":
    main('./input/prices.csv')