def final_check(params):
    '''If all 3 checks (SIBs, Ename, and Google search are False, the case will be labelled as False)'''

    def obtain_result(row):

        if ((row['sibs_final'] == "FALSE") and (row['ename_final'] == "FALSE") and (row['news_final'] == "FALSE")):
            return "False"
        else:
            print ("not passed")
            return "True"

    params['final_result'] = params.apply(lambda row: obtain_result(row), axis=1)

    return params

