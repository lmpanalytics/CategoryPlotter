import time
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Program to calculate Rolling 12 sales for TS categories from a csv file,
# containing 8 categories over all geographical markets and clusters.
# The results are plotted as png files.

# ****************** PROCEDURE START ******************
# Extract data from here:
# C:\Users\SEPALMM\Documents\06_Nestle\TS_Sales_Nestle\TS Special Ledger Nestle by Cluster, Market, and Category.xlsx
# Update 'periods' in method 'createDateRange()' in file 'PlotMain.py' to match ending date in above data file
# ****************** PROCEDURE END ******************


start = time.time()

# Read sales data
df_sales = pd.read_csv('sales.csv', sep=';')

# Convert to dates:
# Insert a day column, fill with 'ones'
df_sales.insert(3, 'Day', 1)

# Add one month and subtract one day to get last day in month dates
dates = pd.to_datetime(df_sales[['Year', 'Month', 'Day']]) + \
    pd.DateOffset(months=1) - pd.DateOffset(days=1)

# Add a new column and reorders dataframe so it's at the first column
df_sales['MyDate'] = dates

cols = df_sales.columns.tolist()
df_sales = df_sales[[cols[-1]] + cols[:-1]]

# Drop not needed columns and set index
df_sales = df_sales.drop(['Date', 'Year', 'Month', 'Day'], axis=1)


def fixMissingDates(df_grouped):
    """ Missing dates are added, with values filled by zeroes
    """
    # Reset the indexes created by the groupby function
    df_grouped = df_grouped.reset_index()

    # Set the index on the date column
    df_grouped = df_grouped.set_index('MyDate')

    rng = createDateRange()

    # Reindex based on the date range and fill missing values by zeroes
    df_grouped = df_grouped.reindex(rng, fill_value=0)

    return df_grouped


def createDateRange():
    """ Calculates from a start date and adds a number of monthly periods to arrive at an end date
    """
    return pd.date_range('2014-01-31', periods=55, freq='M')


def groupSalesByDates():
    """ Group category sales by dates and return a R12 data frame
    """
    # Group by dates and sum sales
    df_grouped = df_sales.groupby('MyDate').sum()

    # Handle missing dates
    df_grouped = fixMissingDates(df_grouped)

    # Apply a rolling 12 window
    df_R12 = df_grouped.rolling(12).sum()

    return(df_R12)


def sumTotalSalesBydates(df_R12SalesByDates):
    """ Sum total category sales and growth rates by dates
    """
    df_R12SalesByDates['sumTotal'] = df_R12SalesByDates.sum(
        axis=1).replace(0, np.nan)

    # Drop not needed columns
    df_R12SalesByDates = df_R12SalesByDates.drop(
        df_R12SalesByDates.columns[[0, 1, 2, 3, 4, 5, 6, 7]], axis=1)

    # Calculate R12 growth rate.
    # Number of rows is one less than total, else out-of-index error
    rows = df_R12SalesByDates.shape[0]-1
    # Create a list to store the data
    growthRates = []
    # Add manually the first entry, else dataframe merge will not match on length
    growthRates.append(np.nan)
    # Populate list
    for i in range(rows):
        # Handle div by 0
        if df_R12SalesByDates.iloc[i + 1]['sumTotal'] != 0:
            growthRates.append(
                ((df_R12SalesByDates.iloc[i]['sumTotal'] / df_R12SalesByDates.iloc[i + 1]['sumTotal'])-1)*100)
        else:
            growthRates.append(np.nan)

    rng = createDateRange()

    # Construct temporary DataFrame from a dictionary
    d = {'myDate': rng, 'growthRate': growthRates}
    df_temp = pd.DataFrame(data=d).set_index('myDate')
    # Merge dataframes
    df_R12SalesByDates = pd.merge(
        df_R12SalesByDates, df_temp, how='left', left_index=True, right_index=True)

    return(df_R12SalesByDates)


def groupSalesByCluster(marketCluster):
    """ Group category sales by a cluster and return a R12 data frame
    """
    # Filter on a market cluster
    df = df_sales.loc[df_sales['Cluster'] == marketCluster]

    # Group by this cluster and sum sales
    df_grouped = df.groupby(['MyDate', 'Cluster']).sum()

    # Handle missing dates
    df_grouped = fixMissingDates(df_grouped)

    # Drop 'Cluster' column to facilitate R12 window calculation
    df_grouped = df_grouped.drop(['Cluster'], axis=1)

    # Apply a rolling 12 window
    df_R12 = df_grouped.rolling(12).sum()

    return(df_R12)


def groupSalesByMarket(market):
    """ Group category sales by a market and return a R12 data frame
    """
    # Filter on a market
    df = df_sales.loc[df_sales['Market'] == market]

    # Group by this market and sum sales
    df_grouped = df.groupby(['MyDate', 'Market']).sum()

    # Handle missing dates
    df_grouped = fixMissingDates(df_grouped)

    # Drop 'Market' column to facilitate R12 window calculation
    df_grouped = df_grouped.drop(['Market'], axis=1)

    # Apply a rolling 12 window
    df_R12 = df_grouped.rolling(12).sum()

    return(df_R12)


def extractGeographicalAreas(ColName):
    """ Make set of Clusters or Markets
    """
    return set(df_sales[ColName])


# Extract set of Clusters and Markets
setOfClusters = extractGeographicalAreas('Cluster')
setOfMarkets = extractGeographicalAreas('Market')


# Create plot and save as picture of category sales by date
df1 = groupSalesByDates()
# print(df1)
ax1 = df1.plot(subplots=True, layout=(4, 2), figsize=(12, 12),
               sharex=False, title='Rolling 12 Net Sales by Category')
ax1[0][0].set_ylabel('EUR')

print('Saving: Rolling 12 Net Sales by Category.png')
plt.savefig('SalesPlots/02.Rolling 12 Net Sales by Category.png')
plt.close()


# Create plot and save as picture of total sales by date
df_total = sumTotalSalesBydates(df1)
# print(df_total)
ax_total = df_total.plot(subplots=True, layout=(1, 2), figsize=(12, 6),
                         sharex=False, title='Rolling 12 Net Sales\nTotal and Growth rate')
ax_total[0][0].set_ylabel('EUR')
ax_total[0][1].set_ylabel('%')

print('Saving: Rolling 12 Net Sales, Total and Growth rate.png')
plt.savefig('SalesPlots/01.Rolling 12 Net Sales, Total and Growth rate.png')
plt.close()


# Loop through Clusters and Markets, create plots and save as pictures
clusterCounter = 3
for cluster in setOfClusters:
    df2 = groupSalesByCluster(cluster)
    # print(df2)
    ax2 = df2.plot(subplots=True,  layout=(4, 2),
                   figsize=(12, 12), sharex=False, title=cluster+'\nRolling 12 Net Sales by Category')
    ax2[0][0].set_ylabel('EUR')

    print('Saving: '+cluster+' Rolling 12 Net Sales by Category.png')
    plt.savefig('SalesPlots/0'+str(clusterCounter)+'.'+cluster +
                ' Rolling 12 Net Sales by Category.png')
    clusterCounter += 1


for market in setOfMarkets:
    df3 = groupSalesByMarket(market)
    # print(df3)
    ax3 = df3.plot(subplots=True,  layout=(4, 2),
                   figsize=(12, 12), sharex=False, title=market+'\nRolling 12 Net Sales by Category')
    ax3[0][0].set_ylabel('EUR')

    print('Saving: '+market+' Rolling 12 Net Sales by Category.png')
    plt.savefig('SalesPlots/'+market + ' Rolling 12 Net Sales by Category.png')
    plt.close()

# https://realpython.com/python-matplotlib-guide/

# https://pandas.pydata.org/pandas-docs/stable/visualization.html

# https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.plot.html


end = time.time()
print('Execution time (sec): ', (end - start))
