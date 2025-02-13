# option.py
from datetime import datetime
import numpy as np

class Option:
    def __init__(self, type_option: str, spot: float, strike: float, rate: float, volatility: float,
                 dividend_yield: float = 0, maturity=None, time_type=None, valuation_date=None, expiration_date=None):
        if type_option not in ['call', 'put']:
            raise ValueError("Le type d'option doit être 'call' ou 'put'")
        
        self.type_option = type_option
        self.spot = spot
        self.strike = strike
        self.rate = rate
        self.volatility = volatility
        self.dividend_yield = dividend_yield

        # Gestion de la maturité
        if maturity is not None and time_type is not None:
            self.maturity = self.convert_to_years(maturity, time_type)
        elif valuation_date and expiration_date:
            self.maturity = self.calculate_maturity(valuation_date, expiration_date)
        else:
            raise ValueError("Vous devez fournir soit (maturity et time_type), soit (valuation_date et expiration_date).")

    @staticmethod
    def convert_to_years(time: float, unit: str) -> float:
        if unit == "days":
            return time / 365
        elif unit == "months":
            return time / 12
        elif unit == "years":
            return time
        else:
            raise ValueError("L'unité doit être 'days', 'months', ou 'years'.")

    @staticmethod
    def calculate_maturity(valuation_date: str, expiration_date: str) -> float:
        date1 = datetime.strptime(valuation_date, "%d/%m/%Y")
        date2 = datetime.strptime(expiration_date, "%d/%m/%Y")
        delta = (date2 - date1).days
        return delta / 365
