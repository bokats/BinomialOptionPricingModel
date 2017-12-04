from datetime import date, timedelta
from math import exp, sqrt, floor

class BinomialOptionPricing:
    def __init__(self, stock_price, strike, expiration_date, dividend_dates, \
    qtr_div, risk_free_rate, option_type, volatility, market_holidays, up_probability):
        self.stock_price = stock_price
        self.strike = strike
        self.expiration_date = expiration_date
        self.dividend_dates = dividend_dates
        self.qtr_div = qtr_div
        self.risk_free_rate = risk_free_rate
        self.option_type = option_type
        self.volatility = volatility
        self.daily_change = exp(volatility * sqrt(1/360))
        # print(self.daily_change)
        self.market_holidays = market_holidays
        self.up_probability = up_probability
        self.tree = []
        self.dates = []

    def find_exact_days(self):
        today = date.today()
        current = today
        if today.weekday() < 5:
            pass
        else:
            while current.weekday() != 0:
                current += timedelta(1)
        self.dates = []

        while current <= self.expiration_date:
            if current.weekday() < 5 and current not in self.market_holidays:
                self.dates.append(current)
            current += timedelta(1)

    def build_tree(self):
        # build out the expected stock price in the form of an array
        days_to_expiration = len(self.dates)
        self.tree.append([[self.stock_price, None, self.dates[0]]])
        level = 1
        number_of_nodes = 2
        while level < days_to_expiration:
            times_up = level
            new_level = []
            day = self.dates[level]
            while number_of_nodes > 0:
                new_stock_price = self.stock_price * (self.daily_change ** times_up)
                new_stock_price = self.round_to_two_decimals(new_stock_price)
                new_level.append([new_stock_price, None, day])
                number_of_nodes -= 1
                times_up -= 2
            level += 1
            number_of_nodes = level + 1
            self.tree.append(new_level)

    def round_to_two_decimals(self,number):
        return float(format(number, '.2f'))

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
                    self.tree[level][i][1] = calc_fcn(self.tree[level][i][0])
            else:
                for i in range(len(self.tree[level])):
                    future_binomial_value = (self.up_probability * self.tree[level + 1][i][1]) + \
                    ((1 - self.up_probability) * self.tree[level + 1][i + 1][1])
                    pv_days = 1
                    if self.dates[level].weekday() == 4:
                        pv_days = 3
                    pv_binomial_value = future_binomial_value / ((1 + self.risk_free_rate)**(pv_days/360))
                    pv_binomial_value = self.round_to_two_decimals(pv_binomial_value)
                    exercise_value = calc_fcn(self.tree[level][i][0])
                    if self.option_type == 0 and self.dates[level + 1] in self.dividend_dates:
                        exercise_value += self.qtr_div
                    self.tree[level][i][1] = max(pv_binomial_value, exercise_value)
        # print(self.tree)
        # print(self.tree[0][0][1])
        return self.tree[0][0][1]

def run_model(stock_price, strike, expiration_date, dividend_dates, qtr_div, risk_free_rate, option_type, volatility, market_holidays, up_probability):
    b = BinomialOptionPricing(stock_price, strike, expiration_date, dividend_dates, qtr_div, risk_free_rate, option_type, volatility, market_holidays, up_probability)
    b.find_exact_days()
    b.build_tree()
    return b.calculate_option_value()

div_dates = [date(2018,1,30), date(2018, 4, 30), date(2018,7,30), date(2018,10,30)]
# div_dates = [date(2017,12,6)]

# run_model(7.4, 5, date(2018, 2,17), div_dates, 0.05, 0.01, 1, 1, [], 0.5)
# b = BinomialOptionPricing(38.12, 32.5, date(2017, 12, 12), None, 0.01, 1, 0.5, [], 0.5)
# b.find_exact_days()

def find_implied_volatiliy(target_option_price, stock_price, strike, \
    expiration_date, dividend_dates, qtr_div, risk_free_rate, option_type, \
    market_holidays, up_probability):
    # use binary search to find volatility given option price
    low_bound = 0.0
    high_bound = 5.0
    middle = (high_bound + low_bound) / 2

    res = run_model(stock_price, strike, expiration_date, \
    dividend_dates, qtr_div, risk_free_rate, option_type, middle, market_holidays, \
    up_probability)

    while res != target_option_price:
        if res < target_option_price:
            low_bound = middle
        else:
            high_bound = middle
        middle = (high_bound + low_bound) / 2
        res = run_model(stock_price, strike, expiration_date, \
        dividend_dates, qtr_div, risk_free_rate, option_type, middle, market_holidays, \
        up_probability)

    print(middle)

# find_implied_volatiliy(0.95, 17.4, 15, date(2019, 1,17), div_dates, 0.2, 0.01, 1, [], 0.5)
find_implied_volatiliy(1.2, 38.1, 32.5, date(2018, 4,17), div_dates, 0, 0.01, 1, [], 0.5)
