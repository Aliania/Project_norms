import pandas as pd
may = pd.read_excel('Documents/May.xlsx',)
#print(may.info())
#print(may.columns)

#may = may.dropna(axis = 'columns', inplace = True)
may1 = may.drop(columns=['Unnamed: 1','Unnamed: 2', 'Unnamed: 3', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 8', 'Unnamed: 10', 'Unnamed: 12'])
may1 = may1.set_axis(['product_name', 'weight_children', 'children_cost', 'nursery_weight', 'nursery_cost', 'weight_total', 'cost_total'], axis='columns')
may1 = may1.fillna('0')
print(may1)