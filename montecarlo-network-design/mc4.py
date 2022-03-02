import pandas as pd
import numpy as np
from pulp import *
from statistics import mean
import plotly.express as px
import dash_table
import plotly.graph_objects as go




import random
random.seed(1447)


#%%

# Importing manufacturing variable costs
manvar_costs = pd.read_excel('data/variable costs.xlsx', index_col = 0)
# Importing freight costs
freight_costs = pd.read_excel('data/freight costs.xlsx', index_col = 0)
# Calculating total cost by adding manufacturing cost and freight cost
var_cost = freight_costs/1000 + manvar_costs 
# Factory Fixed Costs
fixed_costs = pd.read_excel('data/fixed cost.xlsx', index_col = 0)
# Two types of plants: Low Capacity and High Capacity Plant
cap = pd.read_excel('data/capacity.xlsx', index_col = 0)
# Demand by Market
demand = pd.read_excel('data/demand.xlsx', index_col = 0)

#%%

def optimization_model(fixed_costs, var_cost, demand, demand_col, cap):
    '''Build the optimization based on input parameters'''
    # Define Decision Variables
    loc = ['USA', 'GERMANY', 'JAPAN', 'BRAZIL', 'INDIA']
    size = ['LOW', 'HIGH']
    plant_name = [(i,s) for s in size for i in loc]
    prod_name = [(i,j) for i in loc for j in loc]   

    # Initialize Class
    model = LpProblem("Capacitated Plant Location Model", LpMinimize)

    # Create Decision Variables
    x = LpVariable.dicts("production_", prod_name,
                         lowBound=0, upBound=None, cat='continuous')
    y = LpVariable.dicts("plant_", 
                         plant_name, cat='Binary')

    # Define Objective Function
    model += (lpSum([fixed_costs.loc[i,s] * y[(i,s)] * 1000 for s in size for i in loc])
              + lpSum([var_cost.loc[i,j] * x[(i,j)]   for i in loc for j in loc]))

    # Add Constraints
    for j in loc:
        model += lpSum([x[(i, j)] for i in loc]) == demand.loc[j,demand_col]
    for i in loc:
        model += lpSum([x[(i, j)] for j in loc]) <= lpSum([cap.loc[i,s]*y[(i,s)] * 1000
                                                           for s in size])                                                 
    # Solve Model
    model.solve()
    
    # Results
    status_out = LpStatus[model.status]
    objective_out  = pulp.value(model.objective)
    plant_bool = [y[plant_name[i]].varValue for i in range(len(plant_name))]
    fix = sum([fixed_costs.loc[i,s] * y[(i,s)].varValue * 1000 for s in size for i in loc])
    var = sum([var_cost.loc[i,j] * x[(i,j)].varValue for i in loc for j in loc])
    plant_prod = [x[prod_name[i]].varValue for i in range(len(prod_name))]
   
    return status_out, objective_out, y, x, fix, var

#%%

def run_simulation(CV):
    N = 50
    df_demand = pd.DataFrame({'scenario': np.array(range(1, N + 1))})
    data = demand.reset_index()    
    markets = data['(Units/month)'].values
    for col, value in zip(markets, data['Demand'].values):
        sigma = CV * value
        df_demand[col] = np.random.normal(value, sigma, N)
        df_demand[col] = df_demand[col].apply(lambda t: t if t>=0 else 0)
    
    # Add Initial Scenario
    COLS = ['scenario'] + list(demand.index)
    VALS = [0] + list(demand['Demand'].values)
    df_init = pd.DataFrame(dict(zip(COLS, VALS)), index = [0])
    
    # Concat
    df_demand = pd.concat([df_init, df_demand])
    demand_var = df_demand.drop(['scenario'], axis = 1).T
    
    loc = ['USA', 'GERMANY', 'JAPAN', 'BRAZIL', 'INDIA']
    size = ['LOW', 'HIGH']
    plant_name = [(i,s) for s in size for i in loc]
    list_scenario, list_status, list_results, list_totald, list_fixcost, list_varcost = [], [], [], [], [], []
    y = LpVariable.dicts("plant_",  plant_name, cat='Binary')
    df_bool = pd.DataFrame(data = [y[plant_name[i]].varValue for i in range(len(plant_name))], index = [i + '-' + s for s in size for i in loc])
    
    
    for i in range(0, 50): 
        # Calculations
        status_out, objective_out, y, x, fix, var = optimization_model(fixed_costs, var_cost, demand_var, i, cap)    
        # Append results  
        list_status.append(status_out)
        if status_out == 'Optimal':
            list_results.append(objective_out)
            df_bool[i] = [y[plant_name[i]].varValue for i in range(len(plant_name))]
            list_fixcost.append(fix)
            list_varcost.append(var)
            total_demand = demand_var[i].sum()
            list_totald.append(total_demand)
            list_scenario.append(i)
        
    
    return  list_results, df_bool, list_totald, list_fixcost, list_varcost, list_scenario



result_objectives, results_bool, results_totaldemand, result_totalfix, result_totalvar, result_scenario = run_simulation(0.2)


#%%

def return_bool_table(CV):
    bool_table = run_simulation(CV)[1]
    bool_table = bool_table.astype(str)
    bool_table = bool_table.drop([0], axis = 1)
    bool_table = bool_table.reset_index(level=0)
    bool_table = bool_table.replace(to_replace ="0.0",
                 value ="")
    bool_table = bool_table.replace(to_replace ="1.0",
                 value ="Functional")
    
    return bool_table

#%%
def return_unique(CV):
    df_bool = run_simulation(CV)[1]
    df_unique = df_bool.T.drop_duplicates().T
    df_unique.columns = ['INITIAL'] + ['C' + str(i) for i in range(1, len(df_unique.columns))]
    df_unique = df_unique.astype(str)
    df_unique = df_unique.drop(['INITIAL'], axis = 1)
    df_unique = df_unique.reset_index(level=0)
    df_unique = df_unique.replace(to_replace ="0.0",
                 value ="")
    df_unique = df_unique.replace(to_replace ="1.0",
                 value ="Functional")
    return df_unique

#%%
def pie(CV):
    df_unique = return_unique(CV)
    df_bool = return_bool_table(CV)
    COL_NAME, COL_NUMBER = [], []
    for col1 in df_unique.columns:
        count = 0
        COL_NAME.append(col1)
        for col2 in df_bool.columns:
            if (df_bool[col2]!=df_unique[col1]).sum()==0:
                count += 1
        COL_NUMBER.append(count)
    df_comb = pd.DataFrame({'column':COL_NAME, 'count':COL_NUMBER}).set_index('column')
    df_comb = df_comb.reset_index(level=0)
    df_comb = df_comb.iloc[1: , :]
    values = df_comb['count']
    names = df_comb['column']
    fig = px.pie(df_comb, values=values, names=names)
    
    return fig






#%%
# old version of pie chart where the df contaning the data was returned instead of the pie chart
#def pie_df(CV):
def return_finalfig(CV):
    df_u = return_unique(CV)
    df_bool = return_bool_table(CV)
    COL_NAME, COL_NUMBER = [], []
    for col1 in df_u.columns:
        count = 0
        COL_NAME.append(col1)
        for col2 in df_bool.columns:
            if (df_bool[col2]!=df_u[col1]).sum()==0:
                count += 1
        COL_NUMBER.append(count)
    df_comb = pd.DataFrame({'column':COL_NAME, 'count':COL_NUMBER}).set_index('column')
    df_comb = df_comb.reset_index(level=0)
    df_comb = df_comb.iloc[1: , :]
    max_combo = df_comb[df_comb['count'] == df_comb['count'].max()].iloc[0,0]
    max_combo_openings = df_u[['index',max_combo]]
    df_u.insert(1, 'country', ['USA','DEU', 'JPN', 'BRA', 'IND', 'USA','DEU', 'JPN', 'BRA', 'IND'])
    df_u.insert(2, 'capacity', ['Low capacity','Low capacity','Low capacity','Low capacity','Low capacity','High Capacity','High Capacity','High Capacity','High Capacity','High Capacity'])
    max_combo_openings = df_u[['index','country', 'capacity', max_combo]]
    max_combo_openings = max_combo_openings.replace("", np.nan)
    max_combo_openings = max_combo_openings.dropna()
    max_combo_openings = max_combo_openings.iloc[:,:-1]
    max_combo_openings = max_combo_openings.iloc[:,1:]
    max_combo_openings = max_combo_openings.groupby(['country'])['capacity'].apply(','.join)
    max_combo_openings = max_combo_openings.reset_index(level=0)
    
    finalfig = px.choropleth(max_combo_openings, locations='country',                     
                        #title="Hover of shaded countries for details of functional production facilities",
                        #hover_name="country", # column to add to hover information
                        hover_data=["capacity"])
    return finalfig
                    
#%%
def return_unique1(CV):
    df_bool = run_simulation(CV)[1]
    udf = df_bool.T.drop_duplicates().T
    udf.columns = ['INITIAL'] + ['C' + str(i) for i in range(1, len(udf.columns))]
    udf = udf.astype(str)
    udf = udf.drop(['INITIAL'], axis = 1)
    udf = udf.reset_index(level=0)
    udf = udf.replace(to_replace ="0.0",
                 value ="")
    udf = udf.replace(to_replace ="1.0",
                 value ="Functional")
    utable = dash_table.DataTable(         
       data= udf.to_dict('records'),
       columns = [{"name": str(l), "id": str(l)} for l in udf.columns],
       filter_action="native",     # allow filtering of data by user ('native') or not ('none')
       sort_action="native",       # enables data to be sorted per-column by user or not ('none')
       sort_mode="single",         # sort across 'multi' or 'single' columns
       column_selectable="multi",  # allow users to select 'multi' or 'single' columns
       row_selectable="multi",     # allow users to select 'multi' or 'single' rows
       page_action="native",       # all data is passed to the table up-front or not ('none')     
       )
    return utable
#%%

def return_bool_table(CV):
    bool_table = run_simulation(CV)[1]
    bool_table = bool_table.astype(str)
    bool_table = bool_table.drop([0], axis = 1)
    bool_table = bool_table.reset_index(level=0)
    bool_table = bool_table.replace(to_replace ="0.0",
                 value ="")
    bool_table = bool_table.replace(to_replace ="1.0",
                 value ="Functional")
    
    return bool_table

#%%

