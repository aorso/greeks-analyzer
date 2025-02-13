
# models/lookback_option.py

from option_models.exotic_option import ExoticOption  
from pricing_method.monte_carlo import MonteCarloPricer
from greek_method.monte_carlo_greek import MonteCarloGreek

class LookbackOption(ExoticOption):
    def __init__(self, strike_type: str, min_price_observed=None, max_price_observed=None, **kwargs):
        super().__init__(exotic_type='lookback', **kwargs)

        if strike_type not in ['fixed', 'floating']:
            raise ValueError("Le type de strike doit être 'fixed' ou 'floating'.")

        self.strike_type = strike_type
        self.min_price_observed = min_price_observed
        self.max_price_observed = max_price_observed

    def price(self, num_paths=100000, time_steps=100):
        
        return MonteCarloPricer.price_lookback(
            type_option=self.type_option,
            spot=self.spot,
            strike=self.strike,
            maturity=self.maturity,
            rate=self.rate,
            volatility=self.volatility,
            dividend_yield=self.dividend_yield,
            strike_type=self.strike_type,
            num_paths=num_paths,
            time_steps=time_steps
        )


    def greek(self, num_paths=100_000, time_steps=100, seed=None):
        return MonteCarloGreek.montecarlo_lookback_greeks(
            type_option=self.type_option,
            spot=self.spot,
            strike=self.strike,
            maturity=self.maturity,
            rate=self.rate,
            volatility=self.volatility,
            dividend_yield=self.dividend_yield,
            strike_type=self.strike_type,
            num_paths=num_paths,
            time_steps=time_steps,
            seed=seed
        )

            
