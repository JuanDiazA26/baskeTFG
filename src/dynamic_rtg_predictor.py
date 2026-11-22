import math
from nba_api.stats.endpoints import (
    teamgamelogs,
    scheduleleaguev2,
)
import numpy as np
import os
import pandas as pd

# Para el siguiente, añadir net ratings de equipos contra los que se saca net rating
# Y back to backs
# Pasar fecha como argumento


class DynamicRatingPredictor:

    def __init__(
        self, recalculate: bool, season: str = "2026-27", n_games: int | None = None
    ):

        self.season = season
        self.n_games = n_games

        self.league_results = self._get_league_results(recalculate)
        self.std_margin = self._get_margin()
        self.team_logs = self._get_team_logs()

        self.home_adv = (
            self.league_results["homeTeam_score"]
            - self.league_results["awayTeam_score"]
        ).mean()

    @staticmethod
    def norm_cdf(x: float) -> float:
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def _get_league_results(self, recalculate: bool = False) -> pd.DataFrame:

        path = f"data/results/{self.season[2:]}/results_{self.season.replace('-', '')[2:]}.csv"

        if recalculate:

            schedule = scheduleleaguev2.ScheduleLeagueV2(
                season=self.season, timeout=30
            ).get_data_frames()[0]

            sched = schedule[
                [
                    "gameId",
                    "gameDate",
                    "homeTeam_teamName",
                    "awayTeam_teamName",
                    "homeTeam_score",
                    "awayTeam_score",
                ]
            ].copy()

            sched["gameId"] = sched["gameId"].astype(str).str.zfill(10)
            sched["gameDate"] = pd.to_datetime(
                sched["gameDate"], format="%m/%d/%Y %H:%M:%S"
            ).dt.normalize()

            # Partidos de temporada regular terminados
            sched = (
                sched[(sched["gameId"].str[2] == "2") & (sched["gameStatus"] == 3)]
                .sort_values("gameDate")
                .reset_index(drop=True)
            )

            sched.to_csv(path, index=False)
            return sched

        else:

            sched = pd.read_csv(path)
            return sched

    def _get_margin(self) -> float:

        df_results = self.league_results

        df_results["margin"] = (
            self.league_results["homeTeam_score"]
            - self.league_results["awayTeam_score"]
        )

        return (df_results["margin"]).std()

    def _get_team_logs(self) -> pd.DataFrame:
        team_logs = teamgamelogs.TeamGameLogs(
            season_nullable=self.season,
            season_type_nullable="Regular Season",
            measure_type_player_game_logs_nullable="Advanced",
            last_n_games_nullable=self.n_games if self.n_games else "",
            timeout=30,
        ).get_data_frames()[0]

        return team_logs[["GAME_DATE", "TEAM_ID", "TEAM_NAME", "NET_RATING", "PACE"]]

    def _get_team_info(self, team_id: str) -> tuple[float, float]:

        df_team = self.team_logs[self.team_logs["TEAM_ID"] == team_id]

        # print(f"La cantidad de partidos utilizados es {len(df_team)}")

        # Hay que cambiar la fórmula de cálculo, añadir exponencial
        net_rating = df_team["NET_RATING"].mean()
        poss = df_team["PACE"].mean()

        return net_rating, poss

    def _get_team_name(self, team_id: int) -> str:
        match = self.team_logs.loc[self.team_logs["TEAM_ID"] == team_id, "TEAM_NAME"]
        return match.iloc[0]

    def _predict(
        self,
        home_team: str,
        away_team: str,
        line: float,
    ) -> tuple[float, float]:

        home_rtg, home_poss = self._get_team_info(team_id=home_team)
        away_rtg, away_poss = self._get_team_info(team_id=away_team)
        net_rtg_diff = home_rtg - away_rtg

        s = -line
        poss = (home_poss + away_poss) / 2
        home_adv = (
            self.league_results["homeTeam_score"]
            - self.league_results["awayTeam_score"]
        ).mean()
        mu = net_rtg_diff * poss / 100 + home_adv
        sigma = self.std_margin

        cover_prob_home = 1 - self.norm_cdf((s - mu) / sigma)
        cover_prob_away = 1 - cover_prob_home

        # print(
        #     f"La prob de cubrir spread de {line} de {home_team} (local) es {cover_prob_home:.2f}"
        # )
        # print(
        #     f"La prob de cubrir spread de {-line} de {away_team} (visitante) es {cover_prob_away:.2f}"
        # )

        return cover_prob_home, cover_prob_away

    def _choose_line(
        self,
        home_team: str,
        away_team: str,
        min_line: float = -10.5,
        max_line: float = 10.5,
    ):

        min_diff = 1.0
        best_line = -2.5
        favourite = home_team

        for line in np.arange(min_line, max_line + 1e-9, 1.0):

            if line in [-0.5, 0.5]:
                continue

            line = float(line)

            cover_prob_home, cover_prob_away = self._predict(home_team, away_team, line)

            current_diff = abs(cover_prob_home - cover_prob_away)
            if current_diff < min_diff:
                min_diff = current_diff
                best_line = line

                if line > 0:
                    favourite = away_team
                    best_line = -line

        # print(
        #     f"La línea elegida entre {home_team} (local) y {away_team} (visitante) es {favourite}: {best_line}"
        # )

        return favourite, best_line

    def predict_games(self, date: str, min_line: float = -10.5, max_line: float = 10.5) -> None:

        schedule = scheduleleaguev2.ScheduleLeagueV2(
            season=self.season, timeout=30
        ).get_data_frames()[0]

        sched = schedule[
            [
                "gameId",
                "gameDate",
                "homeTeam_teamId",
                "awayTeam_teamId",
            ]
        ].copy()

        sched["gameId"] = sched["gameId"].astype(str).str.zfill(10)
        sched["gameDate"] = pd.to_datetime(
            sched["gameDate"], format="%m/%d/%Y %H:%M:%S"
        ).dt.normalize()

        sched = (
            sched[sched["gameDate"] == date]
            .reset_index(drop=True)
        )

        home_ids = sched["homeTeam_teamId"].to_list()
        away_ids = sched["awayTeam_teamId"].to_list()
        home_teams = [self._get_team_name(home_id) for home_id in home_ids]
        away_teams = [self._get_team_name(away_id) for away_id in away_ids]

        favourites: list[str] = []
        lines: list[float] = []

        for home_id, away_id in zip(home_ids, away_ids):
            favourite, line = self._choose_line(home_id, away_id, min_line, max_line)

            favourites.append(self._get_team_name(favourite))
            lines.append(line)

        df_games = pd.DataFrame({
            "home_team": home_teams,
            "away_team": away_teams,
            "favourite": favourites,
            "lines": lines
        })

        df_games.to_csv(f"data/games/{date.replace("-", "_")}.csv", index=False)

def main():

    predictor = DynamicRatingPredictor(recalculate=False)
    predictor.predict_games(date="2026-11-22", min_line=-25.5, max_line=25.5)


if __name__ == "__main__":

    main()
