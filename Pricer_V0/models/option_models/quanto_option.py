# quanto_option.py
# quanto_option.py

from option_models.option import Option
from pricing_method.black_scholes import BlackScholesPricer
from greek_method.black_scholes_greek import QuantoGreek
import numpy as np

class QuantoOption(Option):
    def __init__(self, fx_rate_volatility, fx_correlation, foreign_rate, exchange_rate=1.0, **kwargs):
        super().__init__(**kwargs)
        self.fx_rate_volatility = fx_rate_volatility
        self.fx_correlation = fx_correlation
        self.foreign_rate = foreign_rate
        self.exchange_rate = exchange_rate

        # Calcul de la volatilité ajustée pour la quanto option
        self.adjusted_volatility = np.sqrt(
            self.volatility**2 + self.fx_rate_volatility**2 - 
            2 * self.fx_correlation * self.volatility * self.fx_rate_volatility
        )

    def price(self):
  
        adjusted_rate = self.rate - self.foreign_rate
        return self.exchange_rate * BlackScholesPricer.price(
            S=self.spot,
            K=self.strike,
            T=self.maturity,
            r=adjusted_rate,
            sigma=self.adjusted_volatility,
            q=self.dividend_yield,
            option_type=self.type_option
        )

    def greek(self):

        adjusted_rate = self.rate - self.foreign_rate
        return QuantoGreek.bs_greeks_quanto(
            S=self.spot,
            K=self.strike,
            T=self.maturity,
            r=adjusted_rate,
            sigma=self.adjusted_volatility,
            q=self.dividend_yield,
            fx_rate_volatility=self.fx_rate_volatility,
            fx_correlation=self.fx_correlation,
            option_type=self.type_option
        )
