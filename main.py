import requests
import pandas as pd
from tabulate import tabulate
from dotenv import load_dotenv
import os

load_dotenv()

class ChainData:
    def __init__(self):
        self.lot_sizes = {}
        self.BASE_URL = 'https://api.upstox.com/v2'
        self.ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.ACCESS_TOKEN}',
            'accept': 'application/json'
        }

    def store_lot_sizes(self, instrument_name: str, expiry_date: str) -> None:
        """
        Stores lot sizes for given instrument in lot_sizes dictionary.
        """
        params = {
            'instrument_key': instrument_name,
            'expiry_date': expiry_date,
        }
        # Fetching lot size data from API
        res = requests.get(f'{self.BASE_URL}/option/contract', headers=self.headers, params=params)
        if res.status_code != 200:
            print(f"Failed to fetch lot size data: {res.status_code} - {res.text}")
            return
        data = res.json()
        if data["data"]:
            for rows in data["data"]:
                self.lot_sizes[rows["instrument_key"]] = rows["lot_size"]

    def get_option_chain_data(self, instrument_name: str, expiry_date: str, side: str) -> pd.DataFrame:
        """
        Fetches option chain data for a given instrument and expiry date and returns the highest bid price for puts
        or the highest ask price for calls for each strike price.

        Args:
            instrument_name (str): Name of the instrument (e.g., NIFTY or BANKNIFTY).
            expiry_date (str): The expiration date of the options, in YYYY-MM-DD format.
            side (str): Option type to retrieve. Use "PE" for Put and "CE" for Call.

        Returns:
            pd.DataFrame: DataFrame containing instrument_name, strike_price, side, and bid/ask.
        """

        params = {
            'instrument_key': instrument_name,
            'expiry_date': expiry_date,
        }

        response = requests.get(f'{self.BASE_URL}/option/chain', headers=self.headers, params=params)

        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code} - {response.text}")
            return pd.DataFrame()

        data = response.json()

        # Storing lot sizes for each instrument
        self.store_lot_sizes(instrument_name, expiry_date)

        results = []
        for option_data in data["data"]:
            # Getting strike price and checking for PE or CE side
            strike_price = option_data['strike_price']
            if side == "PE":
                put_option = option_data.get('put_options')
                if put_option:
                    highest_bid = put_option['market_data']['bid_price']
                    results.append({
                        "instrument_name": put_option["instrument_key"],
                        "strike_price": strike_price,
                        "side": "PE",
                        "bid/ask": highest_bid
                    })
            elif side == "CE":
                call_option = option_data.get('call_options')
                if call_option:
                    highest_ask = call_option['market_data']['ask_price']
                    results.append({
                        "instrument_name": call_option["instrument_key"],
                        "strike_price": strike_price,
                        "side": "CE",
                        "bid/ask": highest_ask
                    })

        # Converting results to DataFrame
        df = pd.DataFrame(results, columns=["instrument_name", "strike_price", "side", "bid/ask"])
        return df

    def calculate_margin_and_premium(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates margin required and premium earned for each option contract.

        Args:
        - data (pd.DataFrame): DataFrame returned by `get_option_chain_data` containing columns
                            'instrument_name', 'strike_price', 'side', and 'bid/ask'.
                            
        Returns:
        - pd.DataFrame: Modified DataFrame with new columns 'margin_required' and 'premium_earned'.
        """
        
        margin_required_list = []
        premium_earned_list = []

        # Iterating over each row in the DataFrame
        for index, row in data.iterrows():
            if self.lot_sizes.get(row["instrument_name"]) and self.lot_sizes[row["instrument_name"]] > 0:
                body = {
                    "instruments": [
                        {
                        "transaction_type": "SELL",
                        "instrument_key": row["instrument_name"],
                        "product": "D",
                        "quantity": self.lot_sizes[row["instrument_name"]],
                        }
                    ]
                }
                # Requesting margin from API
                response = requests.post(f'{self.BASE_URL}/charges/margin', headers=self.headers, json=body)
                if response.status_code == 200:
                    margin_data = response.json()
                    margin_required_list.append(margin_data["data"]["margins"][0]["total_margin"])
                else:
                    print("Failed to fetch margin data:", response.status_code, response.text)
                
                # Calculating premium earned
                premium_earned_list.append(row["bid/ask"] * self.lot_sizes[row["instrument_name"]])
            else:
                margin_required_list.append(None)
                premium_earned_list.append(None)
            
        # Adding new columns to the DataFrame
        data["margin_required"] = margin_required_list
        data["premium_earned"] = premium_earned_list
        
        return data

    def pretty_print_df(self, df: pd.DataFrame) -> None:
        """
        Print the first 5 and last 5 rows of a DataFrame in a pretty table format.
        
        Args:
        - df (pd.DataFrame): The DataFrame to print.
        """
        # Combining first 5 and last 5 rows
        preview_df = pd.concat([df.head(5), df.tail(5)])
        print(tabulate(preview_df, headers='keys', tablefmt='pipe', showindex=False))


def main():
    test_cases = [
        ("NSE_INDEX|Nifty 50", "2024-11-07", "PE"),
        ("NSE_INDEX|Nifty 50", "2024-11-07", "CE"),
        ("NSE_INDEX|Nifty Bank", "2024-11-07", "PE"),
        ("NSE_INDEX|Nifty Bank", "2024-11-07", "CE"),
    ]
    
    # Instantiating the ChainData class
    chain_data = ChainData()
    
    all_dataframes = []

    # Looping over each test case
    for instrument_name, expiry_date, side in test_cases:
        # Fetching the option chain data for each test case
        option_chain_df = chain_data.get_option_chain_data(instrument_name, expiry_date, side)
        
        # If the option chain data is not empty, adding it to the list
        if not option_chain_df.empty:
            all_dataframes.append(option_chain_df)

    if all_dataframes:
        # Concatenating all dataframes from part 1
        final_df_part1 = pd.concat(all_dataframes, ignore_index=True)
        print("Excerpt of output from part 1:")
        chain_data.pretty_print_df(final_df_part1)
        
        # Calculating margin and premium for the combined DataFrame
        final_df_part2 = chain_data.calculate_margin_and_premium(final_df_part1)

        # Writing both DataFrames to separate sheets in the same Excel file
        with pd.ExcelWriter('output.xlsx') as writer:
            final_df_part1.to_excel(writer, sheet_name="Output Part 1", index=False)
            final_df_part2.to_excel(writer, sheet_name="Output Part 2", index=False)

        print("Excerpt of output from part 2:")
        chain_data.pretty_print_df(final_df_part2)
    else:
        print("No data collected across all test cases.")


if __name__ == "__main__":
    main()