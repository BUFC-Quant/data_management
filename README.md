# Data Management Library for BUFC Quant Team

## How to use 
### Installation Using `pip`
Simply call `pip install git+https://github.com/BUFC-Quant/data_management`

### Example Code
 ```python

 from data_management import data_portal
 ...
 portal = data_portal.FMPApi("<YOUR-API-KEY>")
 print(portal.fetch_intraday_prices("AAPL"))
 
 ```

## Data Portal Usage
### Importing
Import using 
 ```python

 from data_management import data_portal
 ```

 ### Initializing FMPApi 
 All that is required is your API key, which you can get for free by creating an account at https://financialmodelingprep.com/developer and going to your dashboard. 
 ```
 portal = data_portal.FMPApi("<YOUR-API-KEY>")
 ```

 ### FMP API Calls 
 The FMPApi class uses Dax Mickelson's `fmpsdk` package, which can be found [here](https://github.com/daxm/fmpsdk). FMPApi doesn't have all of the functionality included in `fmpsdk`, but it aims to make some of the calls simpler. For full functiuonality of Financial Modeling Prep's (FMP) API, you might need to use `fmpsdk` or write custom API calls to Financial Modeling Prep's endpoints. 

### Historical Price Data
To fetch historical price data for a security, you can use `fetch_price`, `fetch_prices`, or `fetch_intraday_price` depending on your needs. `fetch_price` and `fetch_intraday_price` will fetch for an individual security whereas `fetch_prices` is for a list of securities.

#### `fetch_price`
`fetch_price` takes in a security's symbol and optionally a start date and an end date. FMP's data restrictions apply to these calls. For example,

```python
portal.fetch_price("AAPL", start_date='2021-03-01', end_date='2021-03-07')
```

This will look like:

```
         date        open        high         low       close    adjClose       volume  unadjustedVolume  change  changePercent       vwap         label  changeOverTime
0  2021-03-05  120.980003  121.940002  117.570000  121.419998  121.419998  153590400.0       153590400.0    0.44          0.364  120.31000  March 05, 21         0.00364
1  2021-03-04  121.750000  123.599998  118.620003  120.129997  120.129997  178155000.0       178155000.0   -1.62         -1.331  120.78333  March 04, 21        -0.01331
2  2021-03-03  124.809998  125.709999  121.839996  122.059998  122.059998  112966300.0       112966300.0   -2.75         -2.203  123.20333  March 03, 21        -0.02203
3  2021-03-02  128.410004  128.720001  125.010002  125.120003  125.120003  102260900.0       102260900.0   -3.29         -2.562  126.28334  March 02, 21        -0.02562
4  2021-03-01  123.750000  127.930000  122.790001  127.790001  127.790001  116307900.0       116307900.0    4.04          3.265  126.17000  March 01, 21         0.03265
```

Note, date format must be `YYYY-mm-dd`. 

#### 'fetch_prices'
Same as `fetch_price` but must be given a list of symbols. Will return a dictionary of Pandas DataFrames with key-value pair (symbol, DataFrame). For example,

```python
portal.fetch_prices(["AAPL", "NVDA"], start_date='2021-03-01', end_date='2021-03-07')
```
This will look like: 

```
{'NVDA':          date        open        high         low       close    adjClose      volume  unadjustedVolume    change  changePercent       vwap         label  changeOverTime
0  2021-03-05  502.000000  502.000000  467.170013  498.459991  498.459991  13547800.0        13547800.0  -3.54001         -0.705  489.21000  March 05, 21        -0.00705
1  2021-03-04  512.030029  519.000000  483.350006  494.809998  494.809998  14333600.0        14333600.0 -17.22003         -3.363  499.05333  March 04, 21        -0.03363
2  2021-03-03  537.049988  538.059998  511.950012  512.190002  512.190002   9439800.0         9439800.0 -24.85999         -4.629  520.73334  March 03, 21        -0.04629
3  2021-03-02  556.000000  556.820007  535.840027  536.250000  536.250000   6602900.0         6602900.0 -19.75000         -3.552  542.97001  March 02, 21        -0.03552
4  2021-03-01  555.000000  557.000000  542.130005  553.669983  553.669983   8829600.0         8829600.0  -1.33002         -0.240  550.93333  March 01, 21        -0.00240, 'AAPL':          date        open        high         low       close    adjClose       volume  unadjustedVolume  change  changePercent       vwap         label  changeOverTime
0  2021-03-05  120.980003  121.940002  117.570000  121.419998  121.419998  153590400.0       153590400.0    0.44          0.364  120.31000  March 05, 21         0.00364
1  2021-03-04  121.750000  123.599998  118.620003  120.129997  120.129997  178155000.0       178155000.0   -1.62         -1.331  120.78333  March 04, 21        -0.01331
2  2021-03-03  124.809998  125.709999  121.839996  122.059998  122.059998  112966300.0       112966300.0   -2.75         -2.203  123.20333  March 03, 21        -0.02203
3  2021-03-02  128.410004  128.720001  125.010002  125.120003  125.120003  102260900.0       102260900.0   -3.29         -2.562  126.28334  March 02, 21        -0.02562
4  2021-03-01  123.750000  127.930000  122.790001  127.790001  127.790001  116307900.0       116307900.0    4.04          3.265  126.17000  March 01, 21         0.03265}
```

#### fetch_intraday_price
This will fetch intraday prices for a single security. Possible intervals are '1min', '4min', '15min', '30min', '1hour', '4hour'. The function will return a Pandas DataFrame. For example, 

```python
portal.fetch_intraday_price("AAPL")
```

This will look like: 

```
                     date    open     low    high   close  volume
0     2021-03-08 13:40:00  117.81  117.73  117.84  117.76  417464
1     2021-03-08 13:39:00  117.74  117.74  117.90  117.81  323055
2     2021-03-08 13:38:00  117.81  117.72  117.82  117.74  211675
3     2021-03-08 13:37:00  117.80  117.71  117.81  117.80  393984
4     2021-03-08 13:36:00  117.87  117.80  117.93  117.81  347232
...                   ...     ...     ...     ...     ...     ...
1498  2021-03-02 14:46:00  125.74  125.72  125.85  125.82  193118
1499  2021-03-02 14:45:00  125.73  125.72  125.78  125.73  132791
1500  2021-03-02 14:44:00  125.79  125.69  125.79  125.73  144289
1501  2021-03-02 14:43:00  125.79  125.73  125.81  125.78  122184
1502  2021-03-02 14:42:00  125.86  125.78  125.88  125.80  159537
```