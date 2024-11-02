# BreakoutAI ML Internship Task Documentation

**By:** Jayanti Goswami  
**GitHub:** [Jayanti2919/stock-data-fetching](https://github.com/Jayanti2919/stock-data-fetching)  
**Email:** jayanti2919@gmail.com  

---

## Overview

This project uses the Upstox API to retrieve options chain data, calculate margin requirements, and determine premium earned for NSE_INDEX instruments. The main code is in `main.py` with a `ChainData` class containing two primary methods: `get_option_chain_data()` and `calculate_margin_and_premium()`. Additionally, an `auth.py` file handles authentication and token generation.

Before running `main.py`, `auth.py` must be executed to generate an access token. Store this token in the `.env` file.

### Assumptions

1. **Upstox API Access**: The API is accessible, stable, and provides data in a structured format.
2. **Sufficient System Resources**: The system has enough resources to handle data concatenation and processing.
3. **Basic Error Handling**: Assumes minimal error handling for network issues or API failures.

---

## Authentication

To use the Upstox API, follow these steps:

1. **Create an Upstox Account** and an app with `http://localhost:8000` as the redirect URI.
2. Open the following URI in your browser (replace placeholders with actual values):
   ```
   https://api.upstox.com/v2/login/authorization/dialog?client_id=<YOUR-CLIENT-ID>&redirect_uri=<YOUR-REDIRECT-URI>&response_type=code
   ```
3. Log in and retrieve the code from the redirected URI (`http://localhost:8000/?code=<YOUR-CODE>`).
4. Update `.env` with:
   ```
   AUTH_CODE=<YOUR_AUTH_CODE>
   ACCESS_TOKEN=<YOUR-ACCESS-TOKEN>  # obtained from auth.py
   API_KEY=<API-KEY-FROM-APP>
   API_SECRET=<API-SECRET-FROM-APP>
   ```
5. Run `auth.py` to generate the access token, then update `.env` accordingly.

---

## Functions in `ChainData` Class (main.py)

1. **`__init__`**  
   Initializes base URL, access token, and headers. Also sets up a `lot_sizes` dictionary to store instrument lot sizes.
   
   ```python
   chain_data = ChainData()
   ```

2. **`store_lot_sizes(instrument_name, expiry_date)`**  
   Stores lot sizes for a specified instrument and expiry date in `self.lot_sizes`.

3. **`get_option_chain_data(instrument_name, expiry_date, side)`**  
   Fetches option chain data for a given instrument, expiry date, and option type (PE/CE). Returns a DataFrame with highest bid (for PE) or ask prices (for CE) for each strike price.
   
   ```python
   df = chain_data.get_option_chain_data("NSE_INDEX|Nifty 50", "2024-11-07", "PE")
   ```

4. **`calculate_margin_and_premium(data)`**  
   Calculates margin requirements and premium earned for each option contract based on lot sizes.

   ```python
   final_df = chain_data.calculate_margin_and_premium(df)
   ```

5. **`pretty_print_df(df)`**  
   Prints the DataFrame in a nicely formatted table for quick visualization.

   ```python
   chain_data.pretty_print_df(df)
   ```

---

## Notes

- **Error Handling**: Prints error messages for API failures and returns default values.
- **Environment Variables**: ACCESS_TOKEN is stored in `.env` for secure API access.
- **Use of AI**:
  - **ChatGPT**: Used for comparative analysis of APIs, clarifying trading jargon, and generating function descriptions.
  - **GitHub Copilot**: Assisted in generating code snippets for DataFrame concatenation and Excel output.
- **Other Resources**:
  - Upstox Developer API documentation for API details.
  - Upstox Community for debugging errors.
  - CSV file from Upstox Instruments page for test cases.

---

