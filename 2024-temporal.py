import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

file_path = *

# case 1
dates = pd.date_range(start='2024-01-01', end='2024-01-10')
possibility = np.linspace(0.7, 0.5, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Early January')

plt.xlabel('Date')
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d')) # show only month and day

plt.savefig(file_path + 'case1.png', format='png')

plt.tight_layout()
plt.show()


# case 2
dates = pd.date_range(start='2024-01-01', end='2024-01-04')
possibility = np.linspace(0.6, 0.4, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Likely early in January, possibly before the 5th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case2.png', format='png')

plt.tight_layout()
plt.show()


# case 3
dates = pd.date_range(start='2024-01-07', end='2024-01-13')
num_dates = len(dates)

mean_date = pd.Timestamp('2024-01-10')
std_dev = 1 
date_nums = (dates - mean_date).days
gaussian_distribution = norm.pdf(date_nums, loc=0, scale=std_dev)
gaussian_distribution = np.interp(gaussian_distribution, (gaussian_distribution.min(), gaussian_distribution.max()), (0.5, 0.7))

plt.figure(figsize=(10, 6))
plt.plot(dates, gaussian_distribution)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Around Jan 10th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case3.png', format='png')

plt.tight_layout()
plt.show()


# case 4
dates = pd.date_range(start='2024-01-20', end='2024-01-31')
possibility = np.linspace(0.5, 0.7, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Late January')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case4.png', format='png')

plt.tight_layout()
plt.show()


# case 5
dates = pd.date_range(start='2024-01-01', end='2024-01-04')
possibility = np.linspace(0.5, 0.7, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Before the 5th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case5.png', format='png')

plt.tight_layout()
plt.show()


# case 6
dates = pd.date_range(start='2024-01-27', end='2024-01-31')
possibility = np.linspace(0.8, 0.8, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Towards late January, around the 27th or later')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case6.png', format='png')

plt.tight_layout()
plt.show()


# case 7
dates = pd.date_range(start='2024-01-13', end='2024-01-14')
possibility = np.linspace(0.6, 0.6, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Middle of January, perhaps the 13th or 14th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case7.png', format='png')

plt.tight_layout()
plt.show()


# case 8
dates = pd.date_range(start='2024-01-23', end='2024-01-25')
possibility = np.linspace(0.9, 0.9, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Between Jan 23rd and 25th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case8.png', format='png')

plt.tight_layout()
plt.show()


# case 9
dates = pd.date_range(start='2024-01-21', end='2024-01-31')
possibility = np.linspace(0.4, 0.6, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Near the end of January, likely after the 20th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case9.png', format='png')

plt.tight_layout()
plt.show()

# case 10
dates = pd.date_range(start='2024-01-01', end='2024-01-03')
possibility = np.linspace(0.4, 0.6, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Sometime early in January, perhaps by the 3rd')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case10.png', format='png')

plt.tight_layout()
plt.show()


# case 11
dates = pd.date_range(start='2024-01-01', end='2024-01-05')
possibility = np.linspace(0.4, 0.6, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Somewhere in early January, likely before the 6th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case11.png', format='png')

plt.tight_layout()
plt.show()


# case 12
dates = pd.date_range(start='2024-01-03', end='2024-01-04')
possibility = np.linspace(0.9, 0.9, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('The 3rd or the 4th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case12.png', format='png')

plt.tight_layout()
plt.show()


# case 13
dates = pd.date_range(start='2024-01-20', end='2024-01-31')
possibility = np.linspace(0.5, 0.8, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Should be late January')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case13.png', format='png')

plt.tight_layout()
plt.show()


# case 14
dates = pd.date_range(start='2024-01-14', end='2024-01-15')
possibility = np.linspace(0.8, 0.8, len(dates))

plt.figure(figsize=(10, 6))
plt.plot(dates, possibility, marker='o')

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('Mid-January, potentially around the 14th or 15th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case14.png', format='png')

plt.tight_layout()
plt.show()


# case 15
dates = pd.date_range(start='2024-01-09', end='2024-01-15')
num_dates = len(dates)

mean_date = pd.Timestamp('2024-01-10')
std_dev = 1 
date_nums = (dates - mean_date).days
gaussian_distribution = norm.pdf(date_nums, loc=0, scale=std_dev)
gaussian_distribution = np.interp(gaussian_distribution, (gaussian_distribution.min(), gaussian_distribution.max()), (0.4, 0.6))

plt.figure(figsize=(10, 6))
plt.plot(dates, gaussian_distribution)

plt.xlabel('Date')
plt.ylabel('Possibility')
plt.title('About mid-January, roughly the 12th')

plt.xticks(dates)
plt.ylim(0, 1)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

plt.savefig(file_path + 'case15.png', format='png')

plt.tight_layout()
plt.show()
