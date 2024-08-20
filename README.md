# LoadShift Trading Strategy

5MWh Battery using 1.4 charge/discharge cycles per day - using a genetic algorithm to maximize profits trading on 15-min timeframes on the energy market.

## Installation
Clone the git repo
To install all required packages, do the following:

Create and activate a virtual enviroment, eg. 

<code>python3 -m venv venv</code>

<code>source venv/bin/activate</code>

Install required packages

<code>pip install -r requirements.txt</code>

## Usage

### Unformatted .csv
Use <code>extractCSVColumn.py</code> to extract the appropriate column of the file and output it to the prices.csv file. 

### Formatted .csv
Input all the recorded prices <code>#.# \n</code>. The prices will be split into groups of 96 representing one day.
Run the main.py file. 
Depending on computational power and time available, adjust the <code>POPULATION_SIZE</code> and <code>GENERATIONS</code> variable accordingly.

The resulting trading strategy will be in the output/tradingStrategy.csv file which describes the chosen trading strategy.

## File Description

### Project structure
```plaintext
loadShift
├── .gitignore
├── README.md
├── requirements.txt
├── input/
│   └── prices.csv
│   └── balancingEnergy2023.csv
│   └── dayAhead2023.csv
├── output/
│   └── tradingStrategy.csv
└── src/
    └── main.py
    └── extractCSVColumn.py
```

## input/
Historic price-data is input here via csv-files eg. 2023 day-ahead trading prices and 2023 balancing-energy prices.

The appropriate column of the input .csv file can be converted into the prices.csv file format via the <code>extractCSVColumn.py</code> function

### prices.csv
Input all the recorded prices. The prices will be split into groups of 96 representing one day {24*4 = 96 15-min timeframes per day}. 

### tradingStrategy.csv
Output of the trading choices made for each timeframe (Buy/Sell/Nothing)
1.4 Cycles equals to a total of 14 Buys and 14 Sells per day. This number of trades per day has to be reached.
