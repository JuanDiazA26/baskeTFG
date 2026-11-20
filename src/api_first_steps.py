from nba_api.stats.endpoints import leaguedashteamstats


def last_n_netrtg(season="2026-27", n=10, location=None, date_to=None):
    df = leaguedashteamstats.LeagueDashTeamStats(
        season=season,
        measure_type_detailed_defense="Advanced",
        per_mode_detailed="PerGame",
        # last_n_games=n,
        location_nullable=location or "",
        date_to_nullable=date_to or "",
        timeout=30,
    ).get_data_frames()[0]

    # print(df.columns)

    df.to_csv("data/ratings/advanced_25_26.csv")

    out = df[["TEAM_NAME", "NET_RATING", "PACE", "GP"]].copy()
    # out["team"] = out["TEAM_NAME"].str.split().str[-1].str.lower()  # "Oklahoma City Thunder" -> "thunder"
    return out


print(last_n_netrtg(season="2025-26").sort_values("NET_RATING", ascending=False).head())
