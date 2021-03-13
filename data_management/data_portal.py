import fmpsdk
import pandas as pd


class FMPApi(object):
    def __init__(self, api_key):
        self.api_key=api_key

    def _clean_datetime(self, dataframe):
        dataframe['date']=pd.to_datetime(dataframe['date'])
        dataframe.set_index('date', inplace=True)
        dataframe=dataframe.iloc[::-1]
        return dataframe

    def fetch_price(self, symbol: str, start_date: str = None, end_date: str = None):
        """
        Returns historical prices of 1 security as a pandas dataframe. 
        """
        data=pd.DataFrame(fmpsdk.historical_price_full(self.api_key, symbol, from_date=start_date, to_date=end_date)['historical'])

        return self._clean_datetime(data)

    def fetch_prices(self, symbols: list, start_date: str = None, end_date: str = None):
        """
        Returns prices of multiple securities as a dictionary of pandas dataframes. 
        """
        price_list: list = fmpsdk.historical_price_full(self.api_key, symbols, from_date=start_date, to_date=end_date)['historicalStockList']

        price_dict: dict = {}

        for j, i in enumerate(reversed(symbols)):
            data=pd.DataFrame(price_list[j]['historical'])
            price_dict[i] = self._clean_datetime(data)

        return price_dict 

    def _fetch_financial_statement(self, symbol: str, statement: str, limit=4, as_reported: bool = False, period: str = "quarter"):
        """
        Fetches the financial statement of a company. as_reported = True for statement as reported, false for not. Helper for fetch_cf_statement,
        fetch_balance_sheet, and fetch_income_statement. 

        Period options: quarter, annual
        Statement options: balance_sheet, income_statement, cash_flow_statement 
        """
        if as_reported:
            if statement=="balance_sheet":
                return fmpsdk.balance_sheet_statement_as_reported(apikey=self.api_key, symbol=symbol, period=period, limit=limit)

            elif statement=="cash_flow_statement":
                return fmpsdk.cash_flow_statement_as_reported(apikey=self.api_key, symbol=symbol, period=period, limit=limit)

            elif statement=="income_statement":
                return fmpsdk.income_statement_as_reported(apikey=self.api_key, symbol=symbol, period=period, limit=limit)
        
        else:
            if statement=="balance_sheet":
                return fmpsdk.balance_sheet_statement(apikey=self.api_key, symbol=symbol, period=period, limit=limit)

            elif statement=="cash_flow_statement":
                return fmpsdk.cash_flow_statement(apikey=self.api_key, symbol=symbol, period=period, limit=limit)

            elif statement=="income_statement":
                return fmpsdk.income_statement(apikey=self.api_key, symbol=symbol, period=period, limit=limit)


    def fetch_cf_statement(self, symbol: str, limit: int = 4, as_reported: bool = False, period: str = "quarter"):
        """
        Fetches cash flow statement for given symbol. 

        :param str symbol: the symbol of the security (ticker)
        :param int limit: the number of periods to return
        :param bool as_reported: True to return as reported statement
        :param str period: either 'quarter' or 'annual' 
        :return: the statement
        :rtype: pd.DataFrame

        """
        return pd.DataFrame(self._fetch_financial_statement(symbol=symbol, statement="cash_flow_statement", limit=limit, as_reported=as_reported, period=period))

    def fetch_balance_sheet(self, symbol: str, limit: int = 4, as_reported: bool = False, period: str = "quarter"):
        """
        Fetches balance sheet for given symbol. 

        :param str symbol: the symbol of the security (ticker)
        :param int limit: the number of periods to return
        :param bool as_reported: True to return as reported statement
        :param str period: either 'quarter' or 'annual' 
        :return: the statement
        :rtype: pd.DataFrame

        """
        return pd.DataFrame(self._fetch_financial_statement(symbol=symbol, statement="balance_sheet", limit=limit, as_reported=as_reported, period=period))

    def fetch_income_statement(self, symbol: str, limit: int = 4, as_reported: bool = False, period: str = "quarter"):
        """
        Fetches income statement for given symbol. 

        :param str symbol: the symbol of the security (ticker)
        :param int limit: the number of periods to return
        :param bool as_reported: True to return as reported statement
        :param str period: either 'quarter' or 'annual' 
        :return: the statement
        :rtype: pd.DataFrame

        """
        return pd.DataFrame(self._fetch_financial_statement(symbol=symbol, statement="income_statement", limit=limit, as_reported=as_reported, period=period))

    
    def list_market_indices(self):
        return pd.DataFrame(fmpsdk.indexes(apikey=self.api_key))

    def get_spy_constituents(self):
        return fmpsdk.sp500_constituent(apikey=self.api_key)

    def get_nasdaq_constituents(self):
        return fmpsdk.nasdaq_constituent(apikey=self.api_key)

    def get_dow_constituents(self):
        return fmpsdk.dowjones_constituent(apikey=self.api_key)

    def get_historical_dow_constituents(self):
        raise NotImplementedError

    def get_historical_spy_constituents(self):
        raise NotImplementedError

    def get_historical_nasdaq_constituents(self):
        raise NotImplementedError

    def get_available_indexes(self):
        return pd.DataFrame(fmpsdk.available_indexes(apikey=self.api_key))

    def fetch_intraday_price(self, symbol: str, frequency: str = '1min'):
        """
        Fetches intraday prices for given symbol with open, high, low, close, and volume data. 

        :param str symbol: the symbol of the security (ticker)
        :param str frequency: the frequency of data (1min, 5min, 15min, 30min, 1hour, 4hour)
        :return: the data
        :rtype: pd.DataFrame

        """
        data=pd.DataFrame(fmpsdk.historical_chart(apikey=self.api_key, symbol=symbol, time_delta=frequency))
        data.set_index('date', inplace=True)
        data=data.iloc[::-1]
        return data

    def get_company_profile(self, symbol: str):
        """

        """
        return pd.DataFrame(fmpsdk.company_profile(apikey=self.api_key, symbol=symbol))
