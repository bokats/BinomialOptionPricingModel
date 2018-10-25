from datetime import date, timedelta
from math import exp, sqrt, floor

class BinomialOptionPricing:
    def __init__(self, stock_price, strike, expiration_date, dividend_dates, \
    qtr_div, risk_free_rate, option_type, volatility):
        self.stock_price = stock_price
        self.strike = strike
        self.expiration_date = expiration_date
        self.dividend_dates = dividend_dates
        self.qtr_div = qtr_div
        self.risk_free_rate = risk_free_rate
        self.option_type = option_type
        self.volatility = volatility
        self.tree = []
        self.dates = []
        self.number_of_intervals = 365 - (52 * 2) - 8

    def find_exact_days(self):
        today = date.today()
        current = today
        if today.weekday() < 5:
            pass
        else:
            while current.weekday() != 0:
                current += timedelta(1)

        while current <= self.expiration_date:
            if current.weekday() < 5:
                self.dates.append(current)
            current += timedelta(1)


        self.up_move = exp(self.volatility * sqrt(1/self.number_of_intervals))
        self.down_move = 1 / self.up_move
        self.up_probability = (exp(self.risk_free_rate * (1/len(self.dates))) - self.down_move) / (self.up_move - self.down_move)
        self.up_move = self.round_to_four_decimals(self.up_move)
        self.down_move = self.round_to_four_decimals(self.down_move)
        self.up_probability = self.round_to_four_decimals(self.up_probability)

    def build_tree(self):
        # build out the expected stock price in the form of an array
        days_to_expiration = len(self.dates)
        self.tree.append([[self.stock_price, None, self.dates[0]]])
        level = 0
        while level < days_to_expiration:
            new_level = []
            day = self.dates[level]
            num_nodes = len(self.tree[-1])
            node_num = 1
            for node in self.tree[-1]:
                up_price = node[0] * self.up_move
                up_price = self.round_to_two_decimals(up_price)
                new_level.append([up_price, None, day])
                if node_num == num_nodes:
                    down_price = node[0] * self.down_move
                    down_price = self.round_to_two_decimals(down_price)
                    new_level.append([down_price, None, day])
                node_num += 1
            level += 1
            self.tree.append(new_level)

    def round_to_two_decimals(self,number):
        return float(format(number, '.2f'))

    def round_to_four_decimals(self, number):
        return float(format(number, '.4f'))

    def calculate_call_value(self, stock_price):
        return self.round_to_two_decimals(max(stock_price - self.strike, 0))

    def calculate_put_value(self, stock_price):
        return self.round_to_two_decimals(max(self.strike - stock_price, 0))

    def calculate_option_value(self):
        # 0 = call, 1 = put
        if self.option_type == 0:
            calc_fcn = self.calculate_call_value
        else:
            calc_fcn = self.calculate_put_value

        for level in range(len(self.tree) - 1, -1, -1):
            if level == len(self.tree) - 1:
                for i in range(len(self.tree[level])):
                    stock_price = self.tree[level][i][0]
                    if self.option_type == 0 and self.tree[level][i][2] in self.dividend_dates:
                        stock_price += self.qtr_div
                    self.tree[level][i][1] = calc_fcn(stock_price)

            else:
                for i in range(len(self.tree[level])):
                    future_binomial_value = (self.up_probability * self.tree[level + 1][i][1]) + \
                    ((1 - self.up_probability) * self.tree[level + 1][i + 1][1])
                    pv_binomial_value = future_binomial_value * exp(-self.risk_free_rate / self.number_of_intervals)
                    pv_binomial_value = self.round_to_two_decimals(pv_binomial_value)
                    exercise_value = calc_fcn(self.tree[level][i][0])
                    if self.option_type == 0 and self.tree[level][i][2] in self.dividend_dates:
                        exercise_value += self.qtr_div
                    self.tree[level][i][1] = max(pv_binomial_value, exercise_value)
        # print(self.tree[0][0][1])
        return self.tree[0][0][1]

def run_model(stock_price, strike, expiration_date, dividend_dates, qtr_div, risk_free_rate, option_type, volatility):
    b = BinomialOptionPricing(stock_price, strike, expiration_date, dividend_dates, qtr_div, risk_free_rate, option_type, volatility)
    b.find_exact_days()
    b.build_tree()
    return b.calculate_option_value()

def find_implied_volatiliy(target_option_price, stock_price, strike, \
    expiration_date, dividend_dates, qtr_div, risk_free_rate, option_type):
    # use binary search to find volatility given option price
    low_bound = 0.0
    high_bound = 5.0
    middle = (high_bound + low_bound) / 2

    res = run_model(stock_price, strike, expiration_date, \
    dividend_dates, qtr_div, risk_free_rate, option_type, middle)

    prev_middle = middle
    while res != target_option_price:
        if res < target_option_price:
            low_bound = middle
        else:
            high_bound = middle

        middle = (high_bound + low_bound) / 2
        if middle == prev_middle:
            break
        else:
            prev_middle = middle
        res = run_model(stock_price, strike, expiration_date, \
        dividend_dates, qtr_div, risk_free_rate, option_type, middle)

    print(middle)

stock_price = 294
strike = 100
expiration_date = date(2019,3,15)
div_dates = []
dividend = 0.0
risk_free_rate = 0.034
option_type = 1
# volatility = 0.27203840359
option_price = 4.25

market_holidays = []



# run_model(stock_price, strike, expiration_date, div_dates, dividend, \
#           risk_free_rate, option_type, volatility, market_holidays)
# b = BinomialOptionPricing(100, 100, date(2018, 1,11), div_dates, 1.0, 0.05, 0, 0.3, market_holidays)
# b.find_exact_days()
# b.build_tree()
# b.calculate_option_value()

find_implied_volatiliy(option_price, stock_price, strike, \
    expiration_date, div_dates, dividend, risk_free_rate, option_type)
