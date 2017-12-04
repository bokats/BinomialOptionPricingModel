from datetime import date
from math import exp, sqrt, floor

class BinomialOptionPricing:
    def __init__(self, stock_price, strike, expiration_date, dividend_dates, risk_free_rate, option_type, volatility, market_holidays):
        self.stock_price = stock_price
        self.strike = strike
        self.expiration_date = expiration_date
        self.dividend_dates = dividend_dates
        self.risk_free_rate = risk_free_rate
        self.option_type = option_type
        self.volatility = volatility
        self.daily_change = exp(volatility * sqrt(1/360))
        self.market_holidays = market_holidays
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
        total_days += self.number_of_market_holidays()
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
        self.tree.append(self.stock_price)
        level = 1
        number_of_nodes = 2
        while level <= days_to_expiration:
            times_up = level
            while number_of_nodes > 0:
                new_stock_price = self.stock_price * (self.daily_change ** times_up)
                new_stock_price = float(format(new_stock_price, '.2f'))
                self.tree.append(new_stock_price)
                number_of_nodes -= 1
                times_up -= 2
            level += 1
            number_of_nodes = level + 1
        print(self.tree)

    # def calculate_option_value(self):


b = BinomialOptionPricing(1, 1, date(2017, 12, 27), None, None, None, 0.4, None)
# b.build_tree()
b.determine_number_of_market_days()
