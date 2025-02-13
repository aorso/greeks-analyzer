# asian_option.py
    
from option_models.exotic_option import ExoticOption  
from pricing_method.monte_carlo import MonteCarloPricer
from greek_method.monte_carlo_greek import MonteCarloGreek



class AsianOption(ExoticOption):
    def __init__(self, average_type: str, observation_frequency=None, **kwargs):
        self.observation_frequency = observation_frequency  
        super().__init__(exotic_type='asian', **kwargs)  # Appeler uniquement les arguments attendus

        if average_type not in ['arithmetic', 'geometric']:
            raise ValueError("Le type de moyenne doit être 'arithmetic' ou 'geometric'.")
        if average_type == 'arithmetic' and observation_frequency not in ['daily', 'weekly', 'monthly']:
            raise ValueError("Pour une moyenne arithmétique, la fréquence doit être 'daily', 'weekly', ou 'monthly'.")

        self.average_type = average_type
        self.frequency = observation_frequency if average_type == 'arithmetic' else None

    def price(self, num_paths=100000, time_steps=100):
        return MonteCarloPricer.price_asian(
            type_option=self.type_option,
            spot=self.spot,
            strike=self.strike,
            maturity=self.maturity,
            rate=self.rate,
            volatility=self.volatility,
            dividend_yield=self.dividend_yield,
            average_type=self.average_type,
            observation_frequency = self.observation_frequency,
            num_paths=num_paths,
            time_steps=time_steps
        )

    def greek(self, num_paths=100_000, time_steps=100, seed=None):
        return MonteCarloGreek.montecarlo_asian_greeks(
            type_option=self.type_option,
            spot=self.spot,
            strike=self.strike,
            maturity=self.maturity,
            rate=self.rate,
            volatility=self.volatility,
            dividend_yield=self.dividend_yield,
            average_type=self.average_type,
            observation_frequency=self.observation_frequency,
            num_paths=num_paths,
            time_steps=time_steps,
            seed=seed
        )





















