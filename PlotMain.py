from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time

start = time.time()

# Read sales data
df_sales = pd.read_csv('sales.csv', sep=',')

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

    # Create a date range starting Jan 2014
    rng = pd.date_range('2014-01-31', periods=55, freq='M')

    # Reindex based on the date range and fill missing values by zeroes
    df_grouped = df_grouped.reindex(rng, fill_value=0)

    return df_grouped


def groupSalesByDates():
    """ Group sales by dates and return a R12 data frame
    """
    # Group by dates and sum sales
    df_grouped = df_sales.groupby('MyDate').sum()

    # Handle missing dates
    df_grouped = fixMissingDates(df_grouped)

    # Apply a rolling 12 window
    df_R12 = df_grouped.rolling(12).sum()

    return(df_R12)


def groupSalesByCluster(marketCluster):
    """ Group sales by a cluster and return a R12 data frame
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
    """ Group sales by a market and return a R12 data frame
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

print(groupSalesByDates())

# Loop through Clusters and Markets
for cluster in setOfClusters:
    print("\n", cluster, ":")
    print(groupSalesByCluster(cluster))


for market in setOfMarkets:
    print("\n", market, ":")
    print(groupSalesByMarket(market))


end = time.time()
print('Execution time (sec): ', (end - start))
