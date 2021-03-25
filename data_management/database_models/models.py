from sqlalchemy import Column, ForeignKey, Boolean, String, \
                       Integer, BigInteger, Float, Date    
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Enum, UniqueConstraint
import enum

Base = declarative_base()

class PriceFrequency(enum.Enum):
    daily = 'daily'
    weekly = 'weekly'
    monthly = 'monthly'
    quarterly = 'quarterly'
    yearly = 'yearly'

class Security(Base):
    __tablename__ = 'security'
    id = Column(Integer, primary_key=True, autoincrement=True)
    currency = Column('currency', String(3), nullable=False)
    ticker = Column('ticker', String(12), nullable=False)
    name = Column('name', String(200), nullable=False)
    has_invalid_data = Column('has_invalid_data', Boolean)
    exchange = Column('exchange', String(12), nullable=False)
    isin = Column('isin', String(12), unique=True, nullable=False)
    description = Column('description', String(2000))
    company_url = Column('company_url', String(100))
    cusip = Column('cusip', String(9), unique=True, nullable=False)
    employees = Column('employees', Integer)
    country = Column('country', String(200))
    state = Column('state', String(200))
    city = Column('city', String(200))
    address = Column('address', String(200))
    zipcode = Column('zipcode', String(200))
    industry = Column('industry', String(200), nullable=False)
    sector = Column('sector', String(200), nullable=False)

    # NOT SURE ABOUT THESE 
    ipo_date = Column('ipo_date', Date)
    is_etf = Column('isEtf', Boolean)
    is_active = Column('isActive', Boolean)

class SecurityPrice(Base):
    __tablename__ = 'security_price'
    date = Column('date', Date, nullable=False, primary_key=True)
    open = Column('open', Float)
    high = Column('high', Float)
    low = Column('low', Float)
    close = Column('close', Float)
    adjClose = Column('adjClose', Float)
    volume = Column('volume', Float)
    unadjustedVolume = Column('unadjustedVolume', Float)
    change = Column('change', Float)
    changePercent = Column('changePercent', Float)
    vwap = Column('vwap', Float)
    changeOverTime = Column('changeOverTime', Float)
    security = relationship('Security')
    security_id = Column(Integer, ForeignKey('security.id',
                                             onupdate="CASCADE",
                                             ondelete="CASCADE"),
                         nullable=False, primary_key=True)
    UniqueConstraint('date', 'security_id')
    

class BalanceSheet(Base):
    __tablename__ = 'balance_sheet'
    date = Column('date', Date, nullable=False, primary_key=True)
    security_id = Column(Integer, ForeignKey('security.id', onupdate = "CASCADE", ondelete = "CASCADE"), nullable = False, primary_key=True)
    security = relationship('Security')
    reportedCurrency = Column("reportedCurrency", String(5))
    fillingDate = Column("fillingDate", Date)

    acceptedDate = Column("acceptedDate", Date)

    period = Column("period", String(5))

    cashAndCashEquivalents = Column("cashAndCashEquivalents", Float)

    shortTermInvestments = Column("shortTermInvestments", Float)

    cashAndShortTermInvestments = Column("cashAndShortTermInvestments", Float)

    netReceivables = Column("netReceivables", Float)

    inventory = Column("inventory", Float)

    otherCurrentAssets = Column("otherCurrentAssets", Float)

    totalCurrentAssets = Column("totalCurrentAssets", Float)

    propertyPlantEquipmentNet = Column("propertyPlantEquipmentNet", Float)

    goodwill = Column("goodwill", Float)

    intangibleAssets = Column("intangibleAssets", Float)

    goodwillAndIntangibleAssets = Column("goodwillAndIntangibleAssets", Float)

    longTermInvestments = Column("longTermInvestments", Float)

    taxAssets = Column("taxAssets", Float)

    otherNonCurrentAssets = Column("otherNonCurrentAssets", Float)

    totalNonCurrentAssets = Column("totalNonCurrentAssets", Float)

    otherAssets = Column("otherAssets", Float)

    totalAssets = Column("totalAssets", Float)

    accountPayables = Column("accountPayables", Float)

    shortTermDebt = Column("shortTermDebt", Float)

    taxPayables = Column("taxPayables", Float)

    deferredRevenue = Column("deferredRevenue", Float)

    otherCurrentLiabilities = Column("otherCurrentLiabilities", Float)

    totalCurrentLiabilities = Column("totalCurrentLiabilities", Float)

    longTermDebt = Column("longTermDebt", Float)

    deferredRevenueNonCurrent = Column("deferredRevenueNonCurrent", Float)

    deferredTaxLiabilitiesNonCurrent = Column("deferredTaxLiabilitiesNonCurrent", Float)

    otherNonCurrentLiabilities = Column("otherNonCurrentLiabilities", Float)

    totalNonCurrentLiabilities = Column("totalNonCurrentLiabilities", Float)

    otherLiabilities = Column("otherLiabilities", Float)

    totalLiabilities = Column("totalLiabilities", Float)

    commonStock = Column("commonStock", Float)

    retainedEarnings = Column("retainedEarnings", Float)

    accumulatedOtherComprehensiveIncomeLoss = Column("accumulatedOtherComprehensiveIncomeLoss", Float)

    othertotalStockholdersEquity = Column("othertotalStockholdersEquity", Float)

    totalStockholdersEquity = Column("totalStockholdersEquity", Float)

    totalLiabilitiesAndStockholdersEquity = Column("totalLiabilitiesAndStockholdersEquity", Float)

    totalInvestments = Column("totalInvestments", Float)

    totalDebt = Column("totalDebt", Float)

    netDebt = Column("netDebt", Float)
    UniqueConstraint('security_id')

class IncomeStatement(Base):
    __tablename__ = 'income_statement'
    date = Column('date', Date, nullable=False, primary_key=True)
    security_id = Column(Integer, ForeignKey('security.id', onupdate = "CASCADE", ondelete = "CASCADE"), nullable = False, primary_key=True)
    security = relationship('Security')

    reportedCurrency = Column("reportedCurrency", String(5))

    fillingDate = Column("fillingDate", Float)

    acceptedDate = Column("acceptedDate", Float)

    period = Column("period", String(5))

    revenue = Column("revenue", Float)

    costOfRevenue = Column("costOfRevenue", Float)

    grossProfit = Column("grossProfit", Float)

    grossProfitRatio = Column("grossProfitRatio", Float)

    researchAndDevelopmentExpenses = Column("researchAndDevelopmentExpenses", Float)

    generalAndAdministrativeExpenses = Column("generalAndAdministrativeExpenses", Float)

    sellingAndMarketingExpenses = Column("sellingAndMarketingExpenses", Float)

    otherExpenses = Column("otherExpenses", Float)

    operatingExpenses = Column("operatingExpenses", Float)

    costAndExpenses = Column("costAndExpenses", Float)

    interestExpense = Column("interestExpense", Float)

    depreciationAndAmortization = Column("depreciationAndAmortization", Float)

    ebitda = Column("ebitda", Float)

    ebitdaratio = Column("ebitdaratio", Float)

    operatingIncome = Column("operatingIncome", Float)

    operatingIncomeRatio = Column("operatingIncomeRatio", Float)

    totalOtherIncomeExpensesNet = Column("totalOtherIncomeExpensesNet", Float)

    incomeBeforeTax = Column("incomeBeforeTax", Float)

    incomeBeforeTaxRatio = Column("incomeBeforeTaxRatio", Float)

    incomeTaxExpense = Column("incomeTaxExpense", Float)

    netIncome = Column("netIncome", Float)

    netIncomeRatio = Column("netIncomeRatio", Float)

    eps = Column("eps", Float)

    epsdiluted = Column("epsdiluted", Float)

    weightedAverageShsOut = Column("weightedAverageShsOut", Float)

    weightedAverageShsOutDil = Column("weightedAverageShsOutDil", Float)
    UniqueConstraint('security_id')

class CashFlowStatement(Base):
    __tablename__ = 'cash_flow_statement'
    date = Column('date', Date, nullable=False, primary_key=True)
    security_id = Column(Integer, ForeignKey('security.id', onupdate = "CASCADE", ondelete = "CASCADE"), nullable = False, primary_key=True)
    security = relationship('Security')

    reportedCurrency = Column("reportedCurrency", String(5))

    fillingDate = Column("fillingDate", Float)

    acceptedDate = Column("acceptedDate", Float)

    period = Column("period", String(5))

    netIncome = Column("netIncome", Float)

    depreciationAndAmortization = Column("depreciationAndAmortization", Float)

    deferredIncomeTax = Column("deferredIncomeTax", Float)

    stockBasedCompensation = Column("stockBasedCompensation", Float)

    changeInWorkingCapital = Column("changeInWorkingCapital", Float)

    accountsReceivables = Column("accountsReceivables", Float)

    inventory = Column("inventory", Float)

    accountsPayables = Column("accountsPayables", Float)

    otherWorkingCapital = Column("otherWorkingCapital", Float)

    otherNonCashItems = Column("otherNonCashItems", Float)

    netCashProvidedByOperatingActivities = Column("netCashProvidedByOperatingActivities", Float)

    investmentsInPropertyPlantAndEquipment = Column("investmentsInPropertyPlantAndEquipment", Float)

    acquisitionsNet = Column("acquisitionsNet", Float)

    purchasesOfInvestments = Column("purchasesOfInvestments", Float)

    salesMaturitiesOfInvestments = Column("salesMaturitiesOfInvestments", Float)

    otherInvestingActivites = Column("otherInvestingActivites", Float)

    netCashUsedForInvestingActivites = Column("netCashUsedForInvestingActivites", Float)

    debtRepayment = Column("debtRepayment", Float)

    commonStockIssued = Column("commonStockIssued", Float)

    commonStockRepurchased = Column("commonStockRepurchased", Float)

    dividendsPaid = Column("dividendsPaid", Float)

    otherFinancingActivites = Column("otherFinancingActivites", Float)

    netCashUsedProvidedByFinancingActivities = Column("netCashUsedProvidedByFinancingActivities", Float)

    effectOfForexChangesOnCash = Column("effectOfForexChangesOnCash", Float)

    netChangeInCash = Column("netChangeInCash", Float)

    cashAtEndOfPeriod = Column("cashAtEndOfPeriod", Float)

    cashAtBeginningOfPeriod = Column("cashAtBeginningOfPeriod", Float)

    operatingCashFlow = Column("operatingCashFlow", Float)

    capitalExpenditure = Column("capitalExpenditure", Float)

    freeCashFlow = Column("freeCashFlow", Float)
    UniqueConstraint('security_id')