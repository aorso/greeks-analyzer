
# auto_call_option.py

from pricing_method.binomial_tree import BinomialTreePricer
from greek_method.binomial_tree_greek import BinomialTreeGreek

class AutoCallOption:
    def __init__(self, spot, strike, maturity, rate, volatility, dividend_yield, frequency_per_year, coupon, barrier, protection_barrier,type_autocall, memory_feature, **kwargs):
        self.spot = spot
        self.strike = strike
        self.maturity = maturity
        self.rate = rate
        self.volatility = volatility
        self.dividend_yield = dividend_yield
        self.frequency_per_year = frequency_per_year  # Liste des dates d'observation
        self.coupon = coupon  # Coupon payé si la condition est remplie
        self.barrier = barrier  # Barrière pour le remboursement anticipé
        self.protection_barrier = protection_barrier  # Barrière de protection du capital
        self.type_autocall = type_autocall
        self.memory_feature = memory_feature

    def price(self, steps=500):
        return BinomialTreePricer.price_autocall(
            spot=self.spot,
            strike=self.strike,
            maturity=self.maturity,
            rate=self.rate,
            volatility=self.volatility,
            dividend_yield=self.dividend_yield,
            frequency_per_year=self.frequency_per_year,
            coupon=self.coupon,
            barrier=self.barrier,
            protection_barrier=self.protection_barrier,
            type_autocall = self.type_autocall,
            memory_feature=self.memory_feature,
            steps=steps
        )
    
    def greek(self, steps=1000):
        return BinomialTreeGreek.binomial_autocall_greeks(
            spot=self.spot,
            strike=self.strike,
            maturity=self.maturity,
            rate=self.rate,
            volatility=self.volatility,
            dividend_yield=self.dividend_yield,
            frequency_per_year=self.frequency_per_year,
            coupon=self.coupon,
            barrier=self.barrier,
            protection_barrier=self.protection_barrier,
            type_autocall = self.type_autocall,
            memory_feature=self.memory_feature,
            steps=steps
        )
