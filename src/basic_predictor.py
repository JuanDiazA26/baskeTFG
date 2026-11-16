import math
import numpy as np
import os
import pandas as pd


def norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

class BasicPredictor:
    """Initial prediction model.

    This class takes into account net rating, home/away and possessions and margin of
    victory to calculate the probability of a team winning against another given both
    net ratings and where the game is being played.

    Args:
        results_path (str): Path of the results data.
        ratings_path (str): Path of the ratings data.

    Attributes:
        df_results (pd.DataFrame): DataFrame of the results to calculate average
        possessions.
        df_ratings (pd.DataFrame): DataFrame of the ratings and average possessions
        for every team.
    """

    def __init__(self, results_path: str, ratings_path: str):

        self.df_results = pd.read_csv(results_path, sep=",")
        self.df_ratings = pd.read_csv(ratings_path, sep=",")
        self.std_margin = self._calculate_margin()

    def _calculate_margin(self) -> float:
        """Calculate mean and std of margin of victory in every game of
        the 25-26 NBA season.

        Args:

        """

        df = self.df_results.copy()

        df["margin"] = df["PTS_h"] - df["PTS_v"]

        return df["margin"].std()

    def _get_team_info(self, team: str, home: bool):
        """Obtain a team's info (ratings and possessions).

        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, seq_len).
            mask (torch.Tensor): Mask tensor for encoder tensor due to padding (batch_size, seq_len, seq_len).

        Returns:
            torch.Tensor: Output tensor of shape (batch_size, seq_len, d_model).

        """

        # Net rating global como alternativa
        
        team_info = self.df_ratings.loc[
            self.df_ratings["team"] == team,
            ["netrtg_home", "netrtg_away", "home_poss", "away_poss"],
        ]

        if home:
            net_rtg = team_info["netrtg_home"].item()
            possessions = team_info["home_poss"].item()
            return net_rtg, possessions
        else:
            net_rtg = team_info["netrtg_away"].item()
            possessions = team_info["away_poss"].item()
            return net_rtg, possessions

    def _predict(self, home_team: str, away_team: str, line: float) -> tuple[float, float]:

        s = -line

        home_rtg, home_poss = self._get_team_info(home_team, True)
        away_rtg, away_poss = self._get_team_info(away_team, False)
        net_rtg_diff = home_rtg - away_rtg

        poss = (home_poss + away_poss) / 2
        home_adv = (self.df_results["PTS_h"] - self.df_results["PTS_v"]).mean()
        mu = net_rtg_diff * poss / 100 - home_adv
        sigma = self.std_margin

        # Suponiendo que el margen real sigue (aprox.) una distribución normal,
        # la probabilidad de ganar es la probabilidad de que el margen sea > 0

        # Ahora la media es la diferencia "esperada" entre ambos equipos, y la línea
        # se introduce para determinar la parte de la curva que cubre

        cover_prob_home = 1 - norm_cdf((s - mu) / sigma)
        cover_prob_away = 1 - cover_prob_home

        print(
            f"La prob de cubrir spread de {line} de {home_team.capitalize()} (local) es {cover_prob_home:.2f}"
        )
        print(
            f"La prob de cubrir spread de {-line} de {away_team.capitalize()} (visitante) es {cover_prob_away:.2f}"
        )

        return cover_prob_home, cover_prob_away

    def choose_line(self, home_team: str, away_team: str, min_line: float = -10.5, max_line: float = 10.5):

        min_diff = 1.0
        best_line = -2.5

        for line in np.arange(min_line, max_line + 1e-9, 1.0):

            line = float(line)

            cover_prob_home, cover_prob_away = self._predict(
                home_team,
                away_team,
                line
            )

            current_diff = abs(cover_prob_home - cover_prob_away)
            if current_diff < min_diff:
                min_diff = current_diff
                best_line = line

        print(f"La línea elegida para el partido entre {home_team} (local) y {away_team} (visitante) es {best_line}")

        #return min_diff


def main():

    results_path = "data/results/complete/results_2526.csv"
    ratings_path = "data/ratings/net_ratings_2526.csv"

    predictor = BasicPredictor(results_path, ratings_path)
    predictor.choose_line("knicks", "raptors")


if __name__ == "__main__":
    main()