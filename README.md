# LoadShift Trading Strategy

5MWh Battery using 1.4 charge/discharge cycles per day - using a genetic algorithm to maximize profits on 15-min timeframe on the day ahead energy market.

### Usage
Input all the recorded prices <code>#.# \newline</code>. The prices will be split into groups of 95 representing one day.

Run the main.py file. 
Depending on computational power and time available, adjust the <code>POPULATION_SIZE</code> and <code>
GENERATIONS</code> variable accordingly.

The chosen trading strategy will be in the output/tradingStrategy.csv file which describes when the algorithm chose to either buy/sell/do nothing

## File Description

### Project structure
```plaintext
LoadShift
├── .gitignore
├── README.md
├── input/
│   └── prices.txt
├── output/
│   └── tradingStrategy.csv
└── src/
    └── main.py
```

### prices.txt
Input all the recorded prices. The prices will be split into groups of 95 representing one day {24*4-1 = 95 15-min timeframes per day}. 

Sample data for 4 days has already been added.

### tradingStrategy.csv
Output of the trading choices made for each timeframe (Buy/Sell/Nothing)
1.4 Cycles equals to a total of 14 Buys and 14 Sells per day. This number of trades per day has to be reached.