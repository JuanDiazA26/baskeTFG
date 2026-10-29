from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd

advanced_stats = leaguedashplayerstats.LeagueDashPlayerStats(
    season='2026-27',
    measure_type_detailed_defense='Advanced',
    per_mode_detailed='PerGame'
)

df_avanzado = advanced_stats.get_data_frames()[0]

columnas_clave = ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'MIN', 'NET_RATING', 'USG_PCT', 'PIE']
df_limpio: pd.DataFrame = df_avanzado[columnas_clave]

print(df_limpio.sort_values(by="PIE", ascending=False)[df_limpio["MIN"] > 20.0].head(20))