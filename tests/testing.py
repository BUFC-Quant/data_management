from data_management.data_portal import FMPApi


if __name__ == '__main__':
    portal = FMPApi('4c820bedf369dc4593cb9aa6692a1d65')
    thing = database_entry.insert_security(portal.get_company_profile('AAPL'))

    # print(portal.get_company_profile('AAPL').columns)

