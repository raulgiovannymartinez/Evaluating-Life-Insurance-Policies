import pandas as pd
import numpy as np
from datetime import datetime
import numpy_financial as npf

class Policy:
    def __init__(self, fp):
        self.fp = fp
        self.df_policies = self.get_policies()
        self.df_dbs = self.get_dbs()
        self.df_premiums = self.get_premiums()
        self.survival_dict = self.get_survivals() # {male: mortality rates, female: mortality rates}
                
    def get_policies(self):
        return pd.read_excel(self.fp, sheet_name = 'Policy', engine='openpyxl')
    
    def get_dbs(self):
        return pd.read_excel(self.fp, sheet_name = 'DB', engine='openpyxl').set_index('Year')
    
    def get_premiums(self):
        return pd.read_excel(self.fp, sheet_name = 'Premiums', engine='openpyxl').set_index('Year')
    
    def get_survivals(self):
        gender_dict = {}
        
        gender = ['male', 'female']
        cols_to_select = ['B:CD', 'CG:HA']
        
        for g, c in zip(gender, cols_to_select):
            df_raw = pd.read_excel(self.fp, sheet_name = 'Survival', engine='openpyxl', usecols=c, skiprows=1)
            df_pivot = df_raw.stack().rename_axis(['age','duration']).reset_index().rename(columns={0:'rate'})
            df_pivot['duration'] = df_pivot['duration'].apply(lambda x: int(float(x))-1)
            
            gender_dict[g] = df_pivot
        return gender_dict
    

class Insured:
    def __init__(self, policy_obj, policy_no, valuation_date):
        self.po = policy_obj
        self.po_row = self.po.df_policies.query('`Policy Number`==\'{}\''.format(policy_no))
        
        self.v_date = datetime.strptime(valuation_date, '%m/%d/%Y')
        
    def name(self):
        return self.po_row.Name.values[0]

    def gender(self):
        return 'male' if str(self.po_row.Gender.values[0])=='M' else 'female'

    def age(self):
        today = self.v_date
        dob = self.po_row.DOB[0]
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def avg_severity(self):
        return float(self.po_row.AverageSeverity)

    def carrier(self):
        return self.po_row.Carrier.values[0]


class Valuation:
    def __init__(self, policy_obj, insured_obj, rate_pct, include_fee, fee_value, policy_no, adj_param):
        self.po = policy_obj
        self.po_row = self.po.df_policies.query('`Policy Number`==\'{}\''.format(policy_no))
        
        self.insured = insured_obj
        
        self.rate = rate_pct
        self.fee_bool = include_fee
        self.fee_value = fee_value
        self.policy_no = policy_no
        self.v_date = self.insured.v_date
        
        self.qx = self.prob_survival()
        self.qx_adj = self.prob_survival_adj(adj_param)
        self.px = self.prob_mortality()
        self.tpx = self.prob_mortality_t()
        
        self.p_db = self.prob_db()
        self.p_premium = self.prob_premium()
        self.fees_list = self.fees_list()
        self.cash_flow = self.calc_cash_flow()
        self.valuation = self.calc_valuation()
    
    def prob_survival(self):
        age = self.insured.age()
        gender = self.insured.gender()
        return self.po.survival_dict[gender].query('age=={}'.format(age)).rate.values
    
    def prob_survival_adj(self, adj_param):
        return np.array([min(1,i) for i in self.qx*adj_param*self.insured.avg_severity()])
    
    def prob_mortality(self):
        return 1-self.qx_adj
    
    def prob_mortality_t(self):
        tpx_vals = []
        for i in range(len(self.px)):
            if i == 0:
                tpx_vals.append(self.px[0])
            else:
                tpx_vals.append(self.px[i]*tpx_vals[i-1])
            
        return np.array(tpx_vals)
    
    def prob_db(self):
        db = self.po.df_dbs.loc[self.v_date.year+1:,self.policy_no].values
        N = len(self.tpx)-len(db)
        db = np.pad(db, (0, N), 'constant')
        return (1-self.tpx)*db
    
    def prob_premium(self):
        premium = self.po.df_premiums.loc[self.v_date.year:,self.policy_no].values
        return self.tpx*premium
    
    def fees_list(self):
        list_ = []
        for i in range(len(self.px)):
            constant = self.px[i]*1000
            if i<5:
                list_.append(self.px[i]*self.fee_value+constant)
            else:
                list_.append(constant)
        return np.array(list_)
    
    def calc_cash_flow(self):
        cf = self.p_db-self.p_premium
        if self.fee_bool:
            return cf-self.fees_list
        return cf
    
    def calc_valuation(self):
        list_ = []
        for i in range(len(self.cash_flow)):
            list_.append(npf.npv(self.rate/100.0, np.concatenate(([0], self.cash_flow[i:]), axis=0)))
        return list_
    

 
fp = r'.\SoftwareEngineer_TakeHome.xlsx'       
percent_rate = 12
fee = True        
fee_value = 500
policy_no = 'JF5575160'
valuation_date = '11/29/2020'
mortality_adj_param = 0.01


P = Policy(fp)

I = Insured(P,
            policy_no,
            valuation_date)

V = Valuation(P, 
              I,
              percent_rate, 
              fee, 
              fee_value, 
              policy_no, 
              mortality_adj_param)
