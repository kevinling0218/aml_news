#%% import library
import pandas as pd

#%% Read RPA result
def sibs_watchlist(params):
    file = params['file']
    result = pd.read_csv("sibs_watchlist/" + file + ".csv")

    def verify_watchlist(row):

        '''Verify whether the customer is a trur hit but comparing the names and other information'''

        # Get all customer name and strip off space if there is any
        all_name = row['SIBs_name'].split('|')
        all_name = [name.strip(" ") for name in all_name]

        if row['hit_status'] == "Y":
            if ((row['hit_CIF'] == row['SIBs_CIF']) and (row['hit_issue'] == row['SIBs_issue']) and (row['hit_name'] in all_name)):
                return "True"
            else:
                return "False"
        else:
            return "False"

    result['true_hit'] = result.apply(lambda row: verify_watchlist(row), axis=1)

    # Obtain the final result whether the customer is a true hit or not
    if "TRUE" in result['true_hit']:
        params['sibs_final'] = "TRUE"
    else:
        params['sibs_final'] = "FALSE"

    result.to_csv("sibs_watchlist/" + file + "temp.csv")

    # print (params['sibs_final'])
    return params['sibs_final']

