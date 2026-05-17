import pandas as pd
from scipy.stats import ttest_rel

# H0: Query order does not affect execution time.
# alpha: 0.05

filter_df = pd.read_csv("results/filter_order_results.csv")

filter_t_stat, filter_p_value = ttest_rel(
    filter_df["time_a"],
    filter_df["time_b"]
)

print("===== FILTER ORDER EXPERIMENT =====")
print(f"T-statistic : {filter_t_stat}")
print(f"P-value     : {filter_p_value}")

if filter_p_value < 0.05:
    print("Reject H0 → significant difference detected")
else:
    print("Fail to reject H0 → no significant difference")


print()


join_df = pd.read_csv("results/join_order_results.csv")

join_t_stat, join_p_value = ttest_rel(
    join_df["time_a"],
    join_df["time_b"]
)

print("===== JOIN ORDER EXPERIMENT =====")
print(f"T-statistic : {join_t_stat}")
print(f"P-value     : {join_p_value}")

if join_p_value < 0.05:
    print("Reject H0 → significant difference detected")
else:
    print("Fail to reject H0 → no significant difference")