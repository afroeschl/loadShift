import random
import csv
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from numba import jit, prange
import os

# Constants
POPULATION_SIZE = 100
GENERATIONS = 500
MUTATION_RATE = 0.1
NUM_BUY_SELL = 14
GROUP_SIZE = 95

@jit(nopython=True)
def calculate_profit(actions, prices):
    capacity = 30
    total_profit = 0
    transactions = []
    for i in range(len(actions)):
        if actions[i] == 1 and capacity <= 90:  # 1 for buy
            capacity += 10
            total_profit -= prices[i]
        elif actions[i] == 2 and capacity >= 10:  # 2 for sell
            capacity -= 10
            total_profit += prices[i]
        transactions.append((prices[i], actions[i], capacity, total_profit))
    return total_profit, transactions

def create_individual(prices_len):
    actions = np.zeros(prices_len, dtype=np.int32)
    buy_indices = random.sample(range(prices_len), NUM_BUY_SELL)
    sell_indices = random.sample([i for i in range(prices_len) if i not in buy_indices], NUM_BUY_SELL)
    for b in buy_indices:
        actions[b] = 1  # 1 for buy
    for s in sell_indices:
        actions[s] = 2  # 2 for sell
    return actions

def mutate(individual):
    if random.random() < MUTATION_RATE:
        buy_indices = [i for i, action in enumerate(individual) if action == 1]
        sell_indices = [i for i, action in enumerate(individual) if action == 2]
        non_action_indices = [i for i, action in enumerate(individual) if action == 0]

        if random.random() < 0.5 and non_action_indices:
            new_buy = random.choice(non_action_indices)
            individual[random.choice(buy_indices)] = 0
            individual[new_buy] = 1
        else:
            new_sell = random.choice(non_action_indices)
            individual[random.choice(sell_indices)] = 0
            individual[new_sell] = 2

    return individual

def crossover(parent1, parent2):
    crossover_point = random.randint(0, len(parent1) - 1)
    child1 = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
    child2 = np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))

    while np.sum(child1 == 1) != NUM_BUY_SELL or np.sum(child1 == 2) != NUM_BUY_SELL:
        child1 = mutate(create_individual(len(parent1)))
    while np.sum(child2 == 1) != NUM_BUY_SELL or np.sum(child2 == 2) != NUM_BUY_SELL:
        child2 = mutate(create_individual(len(parent1)))

    return child1, child2

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
    return best_individual, best_profit, transactions


def main(file_path):
    with open(file_path, 'r') as file:
        prices = [float(line.strip()) for line in file]

    price_groups = [prices[i:i + GROUP_SIZE] for i in range(0, len(prices), GROUP_SIZE)]
    all_results = []
    total_profit = 0

    for day, group in enumerate(price_groups):
        best_individual, best_profit, transactions = genetic_algorithm(group)
        num_buys = np.sum(np.array(best_individual) == 1)
        num_sells = np.sum(np.array(best_individual) == 2)

        all_results.append((day, best_profit, num_buys, num_sells, transactions))

        print(f"Day {day + 1}")
        print(f"Profit: {round(best_profit,3)}\n")
        total_profit += best_profit

    print(f"Total Profit: {round(total_profit,3)}")

    # Write all results to CSV
    with open('output/tradingStrategy.csv', 'w', newline='') as csvfile:
        fieldnames = ['Day', 'Price', 'Action', 'Capacity', 'Current Profit']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for day, best_profit, num_buys, num_sells, transactions in all_results:
            writer.writerow({'Day': f"Day {day + 1}", 'Price': 'Total Profit', 'Action': best_profit})
            writer.writerow({'Day': f"Day {day + 1}", 'Price': 'Number of Buys', 'Action': num_buys})
            writer.writerow({'Day': f"Day {day + 1}", 'Price': 'Number of Sells', 'Action': num_sells})

            for price, action, capacity, cumulative_profit in transactions:
                writer.writerow({'Day': f"Day {day + 1}", 'Price': price, 'Action': action, 'Capacity': f"{capacity}%", 'Current Profit': cumulative_profit})

if __name__ == "__main__":
    main('./input/prices.txt')