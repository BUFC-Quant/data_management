from datetime import datetime, date, timedelta
import pandas as pd
from pandas.tseries.offsets import BDay
import numpy as np
from sqlalchemy import func, or_, and_
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
import models
import pandas_market_calendars as mcal

def datetime_modification(start_date, end_date):
    if end_date == None:
        today = pd.to_datetime('today') 
        offset = max(1, (today.weekday() + 6) % 7 - 3)
        diff = timedelta(days = offset)
        end_date = today - diff
        end_date = datetime.date(end_date.to_pydatetime())

    else:
        end_date = datetime.date(datetime.strptime(end_date, "%Y-%m-%d"))

    if start_date == None:
        start_date = pd.to_datetime('today') - timedelta(weeks = 5*52)
        start_date = datetime.date(start_date.to_pydatetime())

    else:
        start_date = datetime.date(datetime.strptime(start_date, "%Y-%m-%d"))

    return start_date, end_date

def check_for_security(ticker, session, db):
    query=session.query(models.Security).filter(models.Security.ticker==ticker).statement
    result=pd.read_sql(query, db)
    return result

def insert_missing_security(ticker, session, portal, db):
    company=portal.get_company_profile(ticker)
    insert_security(company, session)

    query=session.query(models.Security).filter(models.Security.ticker==ticker).statement
    result=pd.read_sql(query, db)

    if len(result)==0:
        print(f'Data for {ticker} not available from FMP.')
        return False

    return True

def insert_security(security_df, session):
    security=models.Security(
        currency = security_df['currency'].values[0],
        ticker = security_df['symbol'].values[0],
        name = security_df['companyName'].values[0], 
        exchange = security_df['exchangeShortName'].values[0], 
        isin = security_df['isin'].values[0], 
        description = security_df['description'].values[0], 
        company_url = security_df['website'].values[0], 
        cusip = security_df['cusip'].values[0],
        employees = security_df['fullTimeEmployees'].values[0],
        country = security_df['country'].values[0],
        state = security_df['state'].values[0],
        city = security_df['city'].values[0],
        address = security_df['address'].values[0], 
        zipcode = security_df['zip'].values[0], 
        industry = security_df['industry'].values[0], 
        sector = security_df['sector'].values[0],  
        ipo_date = security_df['ipoDate'].values[0], 
        is_etf = security_df['isEtf'].values[0],
        is_active = security_df['isActivelyTrading'].values[0]
    )

    session.add(security)
    session.commit()

def insert_prices(price_df, session):
    session.bulk_insert_mappings(models.SecurityPrice, price_df.to_dict(orient='records'))
    session.commit()

def insert_financial_ratios(ratio_df, session):
    session.bulk_insert_mappings(models.FinancialRatios, ratio_df.to_dict(orient='records'))
    session.commit()

def query_prices(ticker, session, db, portal, start_date=None, end_date=None):
    # First, check if security is present
    start_date, end_date = datetime_modification(start_date, end_date)

    result=check_for_security(ticker, session, db)

    if len(result)==0:
        inserted=insert_missing_security(ticker, session, portal, db)

        if not inserted:
            return 

    security_id=result['id'].values[0]

    # Now, find which prices we have (if any)
    query=session.query(models.SecurityPrice).outerjoin(models.Security).filter(models.Security.ticker==ticker).statement
    existing_data=pd.read_sql(query, db)

    if len(existing_data) > 0:
        existing_data.sort_values(by='date', inplace=True)
        existing_data.reset_index(inplace=True, drop=True)

        # Get trading days 
        nyse = mcal.get_calendar('NYSE')
        early = nyse.schedule(start_date=start_date, end_date=end_date)
        
        # Identify missing days from existing data (accoutning for gaps)
        days_needed = pd.to_datetime(mcal.date_range(early, frequency='1D'))
        days_needed = [i.date() for i in days_needed]
        
        missing_dates = np.setdiff1d(days_needed, existing_data['date'])

        if len(missing_dates) > 0:
            missing_data=portal.fetch_price(ticker, start_date=missing_dates[0], end_date=missing_dates[-1])
            missing_data['security_id']=security_id
            missing_data.reset_index(inplace=True)
            missing_data.drop('label', inplace=True, axis=1)

            insert_prices(missing_data, session)

            existing_data=pd.read_sql(query, db)
            existing_data.sort_values(by='date', inplace=True)

        return existing_data[(existing_data['date'] >= start_date) & (existing_data['date'] <= end_date)]
     
    
    else:
        data=portal.fetch_price(ticker, start_date=start_date, end_date=end_date)
        data.reset_index(inplace=True)
        data['security_id']=security_id
        data.drop('label', inplace=True)
        insert_prices(data, session)

        return data

def insert_balance_sheet(statement_df, session):
    session.bulk_insert_mappings(models.BalanceSheet, statement_df.to_dict(orient='records'))
    session.commit()

def insert_cashflow_statement(statement_df, session):
    session.bulk_insert_mappings(models.CashFlowStatement, statement_df.to_dict(orient='records'))
    session.commit()

def insert_income_statement(statement_df, session):
    session.bulk_insert_mappings(models.IncomeStatement, statement_df.to_dict(orient='records'))
    session.commit()

def query_balance_sheet(ticker, session, db, portal, start_date=None, end_date=None):
    start_date, end_date = datetime_modification(start_date, end_date)

    result=check_for_security(ticker, session, db)

    if len(result)==0:
        inserted=insert_missing_security(ticker, session, portal, db)

        if not inserted:
            return 

    security_id=result['id'].values[0]

    # Now, find which statements we have (if any)
    query=session.query(models.BalanceSheet).outerjoin(models.Security).filter(models.Security.ticker==ticker).statement
    existing_data=pd.read_sql(query, db)
    total_quarters_to_fetch = int(np.ceil(((end_date.year - start_date.year) * 12 + (end_date.month - start_date.month))/3))

    if len(existing_data) > 0:
        # First, we see if we need to fetch data to add onto our existing data 
        latest_date = max(existing_data.date)
        earliest_date = min(existing_data.date)

        missing_months_after = abs((end_date.year - latest_date.year) * 12 + (end_date.month - latest_date.month))
        num_quarters_rhs = np.ceil(missing_months_after/3)

        if earliest_date > start_date:
            # If we're missing on lhs, need to fetch starting at rhs all the way to lhs 
            data=portal.fetch_balance_sheet(ticker, limit=total_quarters_to_fetch)

            data['security_id']=security_id
            data_to_add=data[~data.isin(existing_data)].dropna()

            insert_balance_sheet(data_to_add, session)
            return data

        elif latest_date < end_date:
            # If we're missing on rhs, only needs to fetch number of rhs missing 
            data=portal.fetch_balance_sheet(ticker, limit=num_quarters_rhs)
            data['security_id']=security_id
            data_to_add=data[~data.isin(existing_data)].dropna()

            insert_balance_sheet(data_to_add, session)
            existing_data=pd.concat([existing_data, data_to_add])

        existing_data=existing_data[(existing_data['date'] >= start_date) & (existing_data['date'] <= end_date)]

        # Now, we do a quick verification that we aren't missing any data between start and end
        if len(existing_data) < total_quarters_to_fetch:
            # Fetch all the data since we can't easily determine which quarter is missing
            print(total_quarters_to_fetch)
            complete_data=portal.fetch_balance_sheet(ticker, limit=total_quarters_to_fetch)
            complete_data['security_id']=security_id
            data_to_add=complete_data[~complete_data.isin(existing_data)].dropna()

            insert_balance_sheet(data_to_add, session)

            return complete_data

        return existing_data

    else:
        complete_data=portal.fetch_balance_sheet(ticker, limit=total_quarters_to_fetch)
        complete_data['security_id']=security_id
        insert_balance_sheet(complete_data, session)

        return complete_data

def query_income_statement(ticker, session, db, portal, start_date=None, end_date=None):
    start_date, end_date = datetime_modification(start_date, end_date)

    result=check_for_security(ticker, session, db)

    if len(result)==0:
        inserted=insert_missing_security(ticker, session, portal, db)

        if not inserted:
            return 

    security_id=result['id'].values[0]

    # Now, find which statements we have (if any)
    query=session.query(models.IncomeStatement).outerjoin(models.Security).filter(models.Security.ticker==ticker).statement
    existing_data=pd.read_sql(query, db)
    total_quarters_to_fetch = int(np.ceil(((end_date.year - start_date.year) * 12 + (end_date.month - start_date.month))/3))

    if len(existing_data) > 0:
        # First, we see if we need to fetch data to add onto our existing data 
        latest_date = max(existing_data.date)
        earliest_date = min(existing_data.date)

        missing_months_after = abs((end_date.year - latest_date.year) * 12 + (end_date.month - latest_date.month))
        num_quarters_rhs = np.ceil(missing_months_after/3)

        if earliest_date > start_date:
            # If we're missing on lhs, need to fetch starting at rhs all the way to lhs 
            data=portal.fetch_income_statement(ticker, limit=total_quarters_to_fetch)

            data['security_id']=security_id
            data_to_add=data[~data.isin(existing_data)].dropna()

            insert_balance_sheet(data_to_add, session)
            return data
            

        elif latest_date < end_date:
            # If we're missing on rhs, only needs to fetch number of rhs missing 
            data=portal.fetch_income_statement(ticker, limit=num_quarters_rhs)
            data['security_id']=security_id
            data_to_add=data[~data.isin(existing_data)].dropna()

            insert_income_statement(data_to_add, session)
            existing_data=pd.concat([existing_data, data_to_add])

        existing_data=existing_data[(existing_data['date'] >= start_date) & (existing_data['date'] <= end_date)]

        # Now, we do a quick verification that we aren't missing any data between start and end
        if len(existing_data) < total_quarters_to_fetch:
            # Fetch all the data since we can't easily determine which quarter is missing
            complete_data=portal.fetch_income_statement(ticker, limit=total_quarters_to_fetch)
            complete_data['security_id']=security_id
            data_to_add=complete_data[~complete_data.isin(existing_data)].dropna()

            insert_income_statement(data_to_add, session)

            return complete_data

        return existing_data

    else:
        complete_data=portal.fetch_income_statement(ticker, limit=total_quarters_to_fetch)
        complete_data['security_id']=security_id
        insert_income_statement(complete_data, session)

        return complete_data

def query_cashflow_statement(ticker, session, db, portal, start_date=None, end_date=None):
    start_date, end_date = datetime_modification(start_date, end_date)
    result=check_for_security(ticker, session, db)

    if len(result)==0:
        inserted=insert_missing_security(ticker, session, portal, db)

        if not inserted:
            return 

    security_id=result['id'].values[0]

    # Now, find which statements we have (if any)
    query=session.query(models.CashFlowStatement).outerjoin(models.Security).filter(models.Security.ticker==ticker).statement
    existing_data=pd.read_sql(query, db)
    total_quarters_to_fetch = int(np.ceil(((end_date.year - start_date.year) * 12 + (end_date.month - start_date.month))/3))

    if len(existing_data) > 0:
        # First, we see if we need to fetch data to add onto our existing data 
        latest_date = max(existing_data.date)
        earliest_date = min(existing_data.date)

        missing_months_after = abs((end_date.year - latest_date.year) * 12 + (end_date.month - latest_date.month))
        num_quarters_rhs = np.ceil(missing_months_after/3)

        if earliest_date > start_date:
            # If we're missing on lhs, need to fetch starting at rhs all the way to lhs 
            data=portal.fetch_cf_statement(ticker, limit=total_quarters_to_fetch)

            data['security_id']=security_id
            data_to_add=data[~data.isin(existing_data)].dropna()

            insert_cashflow_statement(data_to_add, session)
            return data
            

        elif latest_date < end_date:
            # If we're missing on rhs, only needs to fetch number of rhs missing 
            data=portal.fetch_cf_statement(ticker, limit=num_quarters_rhs)
            data['security_id']=security_id
            data_to_add=data[~data.isin(existing_data)].dropna()

            insert_cashflow_statement(data_to_add, session)
            existing_data=pd.concat([existing_data, data_to_add])

        existing_data=existing_data[(existing_data['date'] >= start_date) & (existing_data['date'] <= end_date)]

        # Now, we do a quick verification that we aren't missing any data between start and end
        if len(existing_data) < total_quarters_to_fetch:
            # Fetch all the data since we can't easily determine which quarter is missing
            complete_data=portal.fetch_cf_statement(ticker, limit=total_quarters_to_fetch)
            complete_data['security_id']=security_id
            data_to_add=complete_data[~complete_data.isin(existing_data)].dropna()

            insert_cashflow_statement(data_to_add, session)

            return complete_data

        return existing_data

    else:
        complete_data=portal.fetch_cf_statement(ticker, limit=total_quarters_to_fetch)
        complete_data['security_id']=security_id
        insert_cashflow_statement(complete_data, session)

        return complete_data

def query_financial_ratios(ticker, session, db, portal, start_date=None, end_date=None):
    start_date, end_date = datetime_modification(start_date, end_date)
    result=check_for_security(ticker, session, db)

    if len(result)==0:
        inserted=insert_missing_security(ticker, session, portal, db)

        if not inserted:
            return 

    security_id=result['id'].values[0]

    # Now, find which statements we have (if any)
    query=session.query(models.FinancialRatios).outerjoin(models.Security).filter(models.Security.ticker==ticker).statement
    existing_data=pd.read_sql(query, db)
    total_quarters_to_fetch = int(np.ceil(((end_date.year - start_date.year) * 12 + (end_date.month - start_date.month))/3))

    if len(existing_data) > 0:
        # First, we see if we need to fetch data to add onto our existing data 
        latest_date = max(existing_data.date)
        earliest_date = min(existing_data.date)

        missing_months_after = abs((end_date.year - latest_date.year) * 12 + (end_date.month - latest_date.month))
        num_quarters_rhs = np.ceil(missing_months_after/3)

        if earliest_date > start_date:
            # If we're missing on lhs, need to fetch starting at rhs all the way to lhs 
            data=portal.fetch_financial_ratios(ticker, limit=total_quarters_to_fetch)

            data['security_id']=security_id
            data_to_add=data[~data.isin(existing_data)].dropna()

            insert_financial_ratios(data_to_add, session)
            return data
            

        elif latest_date < end_date:
            # If we're missing on rhs, only needs to fetch number of rhs missing 
            data=portal.fetch_financial_ratios(ticker, limit=num_quarters_rhs)
            data['security_id']=security_id
            data_to_add=data[~data.isin(existing_data)].dropna()

            insert_financial_ratios(data_to_add, session)
            existing_data=pd.concat([existing_data, data_to_add])

        existing_data=existing_data[(existing_data['date'] >= start_date) & (existing_data['date'] <= end_date)]

        # Now, we do a quick verification that we aren't missing any data between start and end
        if len(existing_data) < total_quarters_to_fetch:
            # Fetch all the data since we can't easily determine which quarter is missing
            complete_data=portal.fetch_financial_ratios(ticker, limit=total_quarters_to_fetch)
            complete_data['security_id']=security_id
            data_to_add=complete_data[~complete_data.isin(existing_data)].dropna()

            insert_financial_ratios(data_to_add, session)

            return complete_data

        return existing_data

    else:
        complete_data=portal.fetch_financial_ratios(ticker, limit=total_quarters_to_fetch)
        complete_data['security_id']=security_id
        insert_financial_ratios(complete_data, session)

        return complete_data


if __name__ == '__main__':
    from data_management.data_portal import FMPApi
    
    from sqlalchemy import MetaData
    from sqlalchemy.orm import sessionmaker
    from setup_psql_environment import get_database, get_connection_from_profile
    from sqlalchemy.ext.declarative import declarative_base

    db = get_database()
    Session = sessionmaker(bind=db)
    meta = MetaData(bind=db)
    session = Session()

    print(query_financial_ratios('AAPL', session, db, portal, start_date='2019-03-28', end_date='2020-12-26'))
  
    # aapl_bs=portal.fetch_balance_sheet("AAPL")
    

    # aapl_bs_more=portal.fetch_balance_sheet("AAPL", limit=6)

    # print(aapl_bs_more[~aapl_bs_more.isin(aapl_bs)].dropna())
    
    
    # aapl_bs['security_id']=1
    # print(aapl_bs)

    # start_date, end_date = datetime_modification('2020-03-28', '2020-12-26')

    # latest_date = max(aapl_bs.date)
    # earliest_date = min(aapl_bs.date)

    # missing_months_before = abs((earliest_date.year - start_date.year) * 12 + (earliest_date.month - start_date.month))
    # num_quarters_lhs = np.ceil(missing_months_before/3)

    # missing_months_after = abs((end_date.year - latest_date.year) * 12 + (end_date.month - latest_date.month))
    # num_quarters_rhs = np.ceil(missing_months_after/3)
 
    # total_quarters_to_fetch = np.ceil(num_quarters_lhs + num_quarters_rhs + ((end_date.year - start_date.year) * 12 + (end_date.month - start_date.month))/3)+1

    # print(total_quarters_to_fetch)
    # print(max(aapl_bs.date))
    # print(min(aapl_bs.date))
    # print(aapl_bs)
    # insert_balance_sheet(aapl_bs, session)

    # print(query_prices('TSLA', session, db, start_date='2018-03-24'))
    # print(query_prices('AAPL', session, db, start_date='2015-03-24'))

    # data=portal.fetch_price("AAPL").reset_index()
    # print(data)
    # data['security_id']=1
    # print(data.head())
    # query=session.query(models.SecurityPrice).outerjoin(models.Security).filter(models.Security.ticker=='AAPL').statement
    # df = pd.read_sql(query, db)
    # df.sort_values(by='date', inplace=True)
    # df.reset_index(inplace=True)

    # print(df.head())
    # print(data.head())
    # print(df[df['date']!=data['date']])




    # thing = insert_prices(data, session)