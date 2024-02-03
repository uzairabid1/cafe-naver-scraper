import pandas as pd

data = pd.read_csv('output.csv')
writer = pd.ExcelWriter('output.xlsx')
data.to_excel(writer, index=False,encoding='utf-8')
writer.save()
