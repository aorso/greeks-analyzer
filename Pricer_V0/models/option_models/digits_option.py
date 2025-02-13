
# digits_options.py

import numpy as np
from scipy.stats import norm
from option_models.option import Option  
from greek_method.black_scholes_greek import DigitGreek


class DigitOption(Option):
    def __init__(self, type_option, cash_payout, barrier=None, barrier_type=None, **kwargs):

        super().__init__(type_option=type_option, **kwargs)  # Passe type_option explicitement
        self.cash_payout = cash_payout
        self.barrier = barrier
        self.barrier_type = barrier_type.lower() if barrier_type else None

        # Validation du type de barrière
        if self.barrier_type not in (None, 'up', 'down'):
            raise ValueError("barrier_type doit être 'up', 'down' ou None.")


    def price(self):

        d2 = (np.log(self.spot / self.strike) + (self.rate - 0.5 * self.volatility**2) * self.maturity) / (self.volatility * np.sqrt(self.maturity))
        base_price = self.cash_payout * np.exp(-self.rate * self.maturity)

        if self.type_option == "call":
            price = base_price * norm.cdf(d2)
        elif self.type_option == "put":
            price = base_price * (1 - norm.cdf(d2))
        else:
            raise ValueError("type_option doit être 'call' ou 'put'.")

        # Gestion des barrières
        if self.barrier:
            if self.barrier_type == "up" and self.spot >= self.barrier:
                return 0.0  # Barrière franchie, option sans valeur
            elif self.barrier_type == "down" and self.spot <= self.barrier:
                return 0.0  # Barrière franchie, option sans valeur

        return price



    def greek(self):
        return DigitGreek.bs_greeks_digit(
        S=self.spot,
        K=self.strike,
        T=self.maturity,
        r=self.rate,
        sigma=self.volatility,
        q=self.dividend_yield,
        cash_payout=self.cash_payout,
        type_option= self.type_option,
        barrier=self.barrier,
        barrier_type=self.barrier_type
    )


    def payoff(self):
        if self.type_option == "call":
            return self.cash_payout if self.spot >= self.strike else 0.0
        elif self.type_option == "put":
            return self.cash_payout if self.spot <= self.strike else 0.0
        else:
            raise ValueError("type_option doit être 'call' ou 'put'.")

    def proba_ITM(self):
        d2 = (np.log(self.spot / self.strike) + (self.rate - 0.5 * self.volatility**2) * self.maturity) / (self.volatility * np.sqrt(self.maturity))
        if self.type_option == "call":
            return norm.cdf(d2)
        elif self.type_option == "put":
            return norm.cdf(-d2)
        else:
            raise ValueError("type_option doit être 'call' ou 'put'.")
        
    def expected_payoff(self):
        probability_in_the_money = self.proba_ITM()  # Probabilité que l'option soit dans la monnaie
        nominal_payoff = self.payoff()  # Payoff nominal basé sur la méthode payoff()
        
        # Expected payoff = nominal payoff * probabilité d'être dans la monnaie
        return nominal_payoff * probability_in_the_money
