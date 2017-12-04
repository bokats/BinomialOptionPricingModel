from datetime import date
from math import exp, sqrt, floor

class BinomialOptionPricing:
    def __init__(self, stock_price, strike, expiration_date, dividend_dates, risk_free_rate, option_type, volatility, market_holidays, up_probability):
        self.stock_price = stock_price
        self.strike = strike
        self.expiration_date = expiration_date
        self.dividend_dates = dividend_dates
        self.risk_free_rate = risk_free_rate
        self.option_type = option_type
        self.volatility = volatility
        self.daily_change = exp(volatility * sqrt(1/360))
        print(self.daily_change)
        self.market_holidays = market_holidays
        self.up_probability = up_probability
        self.tree = []

    def determine_number_of_market_days(self):
        today = date.today()
        days_to_expiration = (self.expiration_date - today).days
        total_days = floor(days_to_expiration / 7) * 5
        today_weekday = today.weekday()
        expiration_weekday = self.expiration_date.weekday()
        additional_days = 0
        if expiration_weekday > today_weekday:
            if expiration_weekday > 4:
                additional_days += max(4 - today_weekday, 0)
            else:
                additional_days += max(expiration_weekday - today_weekday, 0)
        elif today_weekday > expiration_weekday:
            additional_days = 0
            if today_weekday < 4:
                additional_days += max(4 - today_weekday, 0)
            additional_days += min(expiration_weekday + 1, 5)
        total_days += additional_days
        total_days += self.number_of_market_holidays(today)
        return total_days

    def number_of_market_holidays(self, today):
        holidays = 0
        for date in self.market_holidays:
            if date > today and date <= self.expiration_date:
                holidays += 1
        return holidays

    def build_tree(self):
        # build out the expected stock price in the form of an array
        today = date.today()
        days_to_expiration = self.determine_number_of_market_days()
        self.tree.append([[self.stock_price, None]])
        level = 1
        number_of_nodes = 2
        while level <= days_to_expiration:
            times_up = level
            new_level = []
            while number_of_nodes > 0:
                new_stock_price = self.stock_price * (self.daily_change ** times_up)
                new_stock_price = float(format(new_stock_price, '.2f'))
                new_level.append([new_stock_price, None])
                number_of_nodes -= 1
                times_up -= 2
            level += 1
            number_of_nodes = level + 1
            self.tree.append(new_level)
        print(self.tree)

    def calculate_call_value(self, stock_price):
        return float(format(max(stock_price - self.strike, 0), '.2f'))

    def calculate_put_value(self, stock_price):
        return float(format(max(self.strike - stock_price, 0), '.2f'))

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
                    future_binomial_value = (self.up_probability * self.tree[level + 1][i][1]) + ((1 - self.up_probability) * self.tree[level + 1][i + 1][1])
                    pv_binomial_value = future_binomial_value / ((1 + self.risk_free_rate)**(1/360))
                    pv_binomial_value = float(format(pv_binomial_value, '.2f'))
                    exercise_value = calc_fcn(self.tree[level][i][0])
                    self.tree[level][i][1] = max(pv_binomial_value, exercise_value)
        # print(self.tree)
        print(self.tree[0][0][1])
        return self.tree[0][0][1]

b = BinomialOptionPricing(10, 10, date(2018, 12, 10), None, 0.03, 0, 0.3, [], 0.5)
b.build_tree()
b.calculate_option_value()
# b.determine_number_of_market_days()
