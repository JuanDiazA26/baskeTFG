from nba_api.stats.endpoints import teamgamelogs

adv = teamgamelogs.TeamGameLogs(
    season_nullable="2026-27",
    season_type_nullable="Regular Season",
    measure_type_player_game_logs_nullable="Advanced",
    timeout=30,
    # team_id_nullable=
).get_data_frames()[0]

# print(adv.head())

df = adv[["GAME_DATE", "TEAM_NAME", "MATCHUP", "NET_RATING", "PACE"]]

df = df[df["TEAM_NAME"] == "New York Knicks"]

print(df)
