#%% import library
import pandas as pd


#%% Read RPA result
def ename_result(params, factor_number):
    file = params['file']
    result = pd.read_csv("ename/" + file + "_ename.csv")
    print (params['name'])
    all_names = params['name'].split('|')
    all_names = [name.strip(" ") for name in all_names]

    def verify_ename(row):
        '''Verify whether it's true hit base on 1 or 2 factors'''

        # If only requires 1 factor, if the name does not match then we will label it as False hit
        if factor_number == 1:
            if row['Matched_Name'] not in all_names:
                return False
            else:
                return True

        # If only requires 2 factors, if the name does not match then we will need to check for another factor
        # (use "category" to show case here, in the production we should factor in all)
        # If there is another factor does not match, then we will label it as False
        if factor_number == 2:
            if row['Matched_Name'] not in all_names:
                if (row['Category'] != "Individual"):
                    return False
            else:
                return True


    result['e_name_true_hit'] = result.apply(lambda row: verify_ename(row), axis=1)

    # Obtain the final result whether the customer is a true hit or not
    if "TRUE" in result['e_name_true_hit']:
        params['ename_final'] = "TRUE"
    else:
        params['ename_final'] = "FALSE"

    result.to_csv("ename/" + file + "temp.csv")
    return params['ename_final']

