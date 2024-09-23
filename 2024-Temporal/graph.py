import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import seaborn as sns

sns.set(style="darkgrid")

dates_full = pd.date_range(start='2024-01-01', end='2024-01-31')
possibility_cumulative = np.zeros(len(dates_full))

# case 1
dates = pd.date_range(start='2024-01-01', end='2024-01-10')
possibility = np.linspace(10, 5, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[:len(dates)] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Early January')

plt.xlabel('Date')
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d')) # show only month and day

plt.savefig('case1.png', format='png')

plt.tight_layout()
plt.show()


# case 2
dates = pd.date_range(start='2024-01-01', end='2024-01-04')
possibility = np.linspace(4, 6, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[:len(dates)] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Likely early in January, possibly before the 5th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case2.png', format='png')

plt.tight_layout()
plt.show()


# case 3
dates = pd.date_range(start='2024-01-07', end='2024-01-13')
num_dates = len(dates)

mean_date = pd.Timestamp('2024-01-10')
std_dev = 1 
date_nums = (dates - mean_date).days
gaussian_distribution = norm.pdf(date_nums, loc=0, scale=std_dev)
gaussian_distribution = np.interp(gaussian_distribution, (gaussian_distribution.min(), gaussian_distribution.max()), (3, 7))
gaussian_distribution = gaussian_distribution / gaussian_distribution.sum()
possibility_cumulative[6:13] += gaussian_distribution

plt.figure(figsize=(10, 5))
plt.plot(dates, gaussian_distribution, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Around Jan 10th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case3.png', format='png')

plt.tight_layout()
plt.show()


# case 4
dates = pd.date_range(start='2024-01-20', end='2024-01-31')
possibility = np.linspace(5, 7, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[19:31] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Late January')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case4.png', format='png')

plt.tight_layout()
plt.show()


# case 5
dates = pd.date_range(start='2024-01-01', end='2024-01-04')
possibility = np.linspace(5, 7, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[:len(dates)] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Before the 5th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case5.png', format='png')

plt.tight_layout()
plt.show()


# case 6
dates = pd.date_range(start='2024-01-27', end='2024-01-31')
possibility = np.linspace(8, 8, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[26:31] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Towards late January, around the 27th or later')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case6.png', format='png')

plt.tight_layout()
plt.show()


# case 7
dates = pd.date_range(start='2024-01-13', end='2024-01-14')
possibility = np.linspace(6, 6, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[12:14] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Middle of January, perhaps the 13th or 14th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case7.png', format='png')

plt.tight_layout()
plt.show()


# case 8
dates = pd.date_range(start='2024-01-23', end='2024-01-25')
possibility = np.linspace(9, 9, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[22:25] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Between Jan 23rd and 25th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case8.png', format='png')

plt.tight_layout()
plt.show()


# case 9
dates = pd.date_range(start='2024-01-21', end='2024-01-31')
possibility = np.linspace(4, 6, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[20:31] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Near the end of January, likely after the 20th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case9.png', format='png')

plt.tight_layout()
plt.show()

# case 10
dates = pd.date_range(start='2024-01-01', end='2024-01-03')
possibility = np.linspace(4, 6, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[:len(dates)] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Sometime early in January, perhaps by the 3rd')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case10.png', format='png')

plt.tight_layout()
plt.show()


# case 11
dates = pd.date_range(start='2024-01-01', end='2024-01-05')
possibility = np.linspace(4, 6, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[:len(dates)] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Somewhere in early January, likely before the 6th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case11.png', format='png')

plt.tight_layout()
plt.show()


# case 12
dates = pd.date_range(start='2024-01-03', end='2024-01-04')
possibility = np.linspace(9, 9, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[2:4] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('The 3rd or the 4th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case12.png', format='png')

plt.tight_layout()
plt.show()


# case 13
dates = pd.date_range(start='2024-01-20', end='2024-01-31')
possibility = np.linspace(5, 8, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[19:31] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Should be late January')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case13.png', format='png')

plt.tight_layout()
plt.show()


# case 14
dates = pd.date_range(start='2024-01-14', end='2024-01-15')
possibility = np.linspace(8, 8, len(dates))
possibility = possibility / possibility.sum()
possibility_cumulative[13:15] += possibility

plt.figure(figsize=(10, 5))
plt.plot(dates, possibility, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Mid-January, potentially around the 14th or 15th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case14.png', format='png')

plt.tight_layout()
plt.show()


# case 15
dates = pd.date_range(start='2024-01-09', end='2024-01-15')
num_dates = len(dates)

mean_date = pd.Timestamp('2024-01-12')
std_dev = 1 
date_nums = (dates - mean_date).days
gaussian_distribution = norm.pdf(date_nums, loc=0, scale=std_dev)
gaussian_distribution = np.interp(gaussian_distribution, (gaussian_distribution.min(), gaussian_distribution.max()), (3, 6))
gaussian_distribution = gaussian_distribution / gaussian_distribution.sum()
possibility_cumulative[8:15] += gaussian_distribution

plt.figure(figsize=(10, 5))
plt.plot(dates, gaussian_distribution, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('About mid-January, roughly the 12th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('case15.png', format='png')

plt.tight_layout()
plt.show()


# cumulative graph
possibility_cumulative = possibility_cumulative / possibility_cumulative.sum()

plt.figure(figsize=(10, 5))
plt.plot(dates_full, possibility_cumulative, marker='o')
plt.grid(color='white', linestyle='-', linewidth=0.5)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Cumulative Probability Distribution')

plt.xticks(dates_full)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))

plt.savefig('cumulative.png', format='png')

plt.tight_layout()
plt.show()
