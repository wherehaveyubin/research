import numpy as np
import matplotlib.pyplot as plt

# Array of values
x = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
              0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
              0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.74076708, 0.0, 0.0, 0.0,
              0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.03115417, 7.567397, 0.0, 0.0, 0.0, 0.0,
              0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 17.24558908, 10.81880805, 7.93973601, 0.0,
              0.0, 0.0, 2.11341718, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.43660282, 0.0, 0.0, 0.0,
              0.63979379, 0.0, 3.73912271, 0.0, 0.0, 13.54317586, 0.0, 0.0, 0.0, 17.79360917, 7.93973601, 21.19185814, 0.0,
              9.4579352, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 33.31647482, 0.0, 0.0,
              0.0, 4.64899338, 6.83582952, 0.0, 0.0, 0.0])

# Step 1: Sorting values
x_sorted = np.sort(x)

# Step 2: Cumulative sum
cumulative_sum = np.cumsum(x_sorted)

# Step 3: Total sum for the Lorenz curve
total_sum = cumulative_sum[-1]

# Step 4: Lorenz curve
lorenz_curve = cumulative_sum / total_sum

# Step 5: Gini coefficient calculation
n = len(x)
gini_coefficient = (2 * np.sum(np.arange(1, n+1) * x_sorted) / (n * np.sum(x_sorted))) - (n + 1) / n

# Plotting the Lorenz curve
plt.figure(figsize=(8, 6))
plt.plot(np.linspace(0, 1, n), lorenz_curve, label="Lorenz Curve", color="b")
plt.plot([0, 1], [0, 1], label="Line of Equality", color="r", linestyle="--")
plt.fill_between(np.linspace(0, 1, n), 0, lorenz_curve, color="skyblue", alpha=0.4)
plt.title("Lorenz Curve")
plt.xlabel("Cumulative share of Census Block Groups")
plt.ylabel("Cumulative share of total SPAR")
plt.legend()
plt.grid(True)

plt.savefig("Figure 13.png", dpi=300)

plt.show()
