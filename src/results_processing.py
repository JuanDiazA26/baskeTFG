import pandas as pd

# Cálculo de average possessions
# Citar,a,BB,reference


def calculate_margin(df: pd.DataFrame) -> tuple[float, float]:
    """Calculate margin of victory in every game of
    the 25-26 NBA season"""

    df["margin"] = abs(df["PTS_h"] - df["PTS_v"])

    return df["margin"].mean(), df["margin"].std()


def main() -> None:
    df_results = pd.read_csv("data/results/complete/results_2526.csv")
    mean_margin, std_margin = calculate_margin(df_results)

    print(f"El margen medio de victoria es {mean_margin}")
    print(f"La desviación típica del margen de victoria es {std_margin}")


if __name__ == "__main__":
    main()
