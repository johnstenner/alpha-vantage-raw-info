# ETF Lookthrough Tool Alpha Vantage
# This script is a simple tool to fetch ETF profile data and sector weights from Alpha Vantage. 


# Looks like Alpha Vantage does not have the info on holdings if the company held in the fund is not listed on an american exchange. This also excludes OTC listed stocks. This is a big limitation for this tool.
# this is leading to incorrect weights for sectors.
# Also, it doesnt pull Real Estate sector data for any of the tested funds, IVV/ICLN/SPLG/MGC/VOO. Looking at the raw output in the terminal, Real Estate just isnt included in the retrieved sector data. 


import requests
import pandas as pd

api_key = 'MY_API_KEY_GOES_HERE' # ADD IN YOUR API KEY BEFORE RUNNING
tickers = ['IVV', 'ICLN', 'SPLG', 'MGC', 'VOO']

# Store data
etf_data = []
sector_data = []

url = 'https://www.alphavantage.co/query'

for ticker in tickers:
    print(f"Fetching data for {ticker}...")
    
    params = {
        'function': 'ETF_PROFILE',
        'symbol': ticker,
        'apikey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # Print raw data for debugging
        print(f"Data received for {ticker}:", data)
        
        if data:
            # ETF Profile data
            profile = {
                'Symbol': ticker,
                'Net Assets': data.get('net_assets'),
                'Expense Ratio': data.get('net_expense_ratio'),
                'Portfolio Turnover': data.get('portfolio_turnover'),
                'Dividend Yield': data.get('dividend_yield'),
                'Inception Date': data.get('inception_date'),
                'Leveraged': data.get('leveraged')
            }
            etf_data.append(profile)
            
            # Sector data
            sectors = data.get('sectors', []) # WHY IS THIS NOT GIVING REAL ESTATE SECTOR??? DOES ALPHA VANTAGE NOT HAVE THIS DATA? SECTOR DATA IS ALSO SLIGHTLY OFF FROM ISSUER WEBSITES
            for sector in sectors:
                sector_row = {
                    'Symbol': ticker,
                    'Sector': sector.get('sector'),
                    'Weight': float(sector.get('weight', 0))  # Convert weight to float
                }
                sector_data.append(sector_row)
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
    

# Create DataFrames
if len(etf_data) > 0:
    df_profiles = pd.DataFrame(etf_data)
    print("\nETF Profile Data:")
    print(df_profiles)
else:
    print("No ETF profile data collected")

if len(sector_data) > 0:
    df_sectors = pd.DataFrame(sector_data)
    print("\nSector Data Columns:", df_sectors.columns)
    print("\nSector Data Sample:")
    print(df_sectors.head())
    
    try:
        # Optional: Pivot the sectors data to create a wide format where each sector is a column
        df_sectors_wide = df_sectors.pivot_table(
            index='Symbol', 
            columns='Sector', 
            values='Weight',
            aggfunc='first'
        )

        # Save to Excel with multiple sheets
        with pd.ExcelWriter('etf_profiles.xlsx') as writer:
            df_profiles.to_excel(writer, sheet_name='ETF_Profiles', index=False)
            df_sectors.to_excel(writer, sheet_name='Sectors_Long', index=False)
            df_sectors_wide.to_excel(writer, sheet_name='Sectors_Wide')

        print("\nETF Profile Data:")
        print(df_profiles)
        print("\nSector Data (Long Format):")
        print(df_sectors)
        print("\nSector Data (Wide Format):")
        print(df_sectors_wide)
        
    except Exception as e:
        print(f"Error during pivot or save: {str(e)}")
else:
    print("No sector data collected")
