import pandas as pd
import math
import os


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

        df["margin"] = abs(df["PTS_h"] - df["PTS_v"])

        return df["margin"].std()

    def _get_team_info(self, team: str, home: bool):
        """Obtain a team's info (ratings and possessions).

        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, seq_len).
            mask (torch.Tensor): Mask tensor for encoder tensor due to padding (batch_size, seq_len, seq_len).

        Returns:
            torch.Tensor: Output tensor of shape (batch_size, seq_len, d_model).

        """

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

    def predict(self, home_team: str, away_team: str):

        home_rtg, home_poss = self._get_team_info(home_team, True)
        away_rtg, away_poss = self._get_team_info(away_team, False)

        poss = (home_poss + away_poss) / 2
        sigma = self.std_margin

        net_rtg_diff = home_rtg - away_rtg

        win_prob_home = round(
            0.5 * (1 + math.erf((net_rtg_diff * poss / 100) / sigma / math.sqrt(2))), 2
        )
        win_prob_away = round(1 - win_prob_home, 2)

        # Suponiendo que el margen real sigue (aprox.) una distribución normal,
        # la probabilidad de ganar es la probabilidad de que el margen sea > 0

        print(
            f"La prob de victoria de {home_team.capitalize()} (local) es {win_prob_home}"
        )
        print(
            f"La prob de victoria de {away_team.capitalize()} (visitante) es {win_prob_away}"
        )


def main():

    results_path = "data/results/complete/results_2526.csv"
    ratings_path = "data/ratings/net_ratings_2526.csv"

    predictor = BasicPredictor(results_path, ratings_path)
    predictor.predict("knicks", "celtics")


if __name__ == "__main__":
    main()
