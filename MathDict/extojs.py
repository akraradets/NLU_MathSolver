import xlrd
from collections import OrderedDict
import simplejson as json

# Open the workbook and select the first worksheet
wb = xlrd.open_workbook('Math-Question.xlsx')
sh = wb.sheet_by_index(0)

# List to hold dictionaries
q_list = []

# Iterate through each row in worksheet and fetch values into dict
for rownum in range(1, sh.nrows):
    qs = OrderedDict()
    row_values = sh.row_values(rownum)
    qs['Question'] = row_values[0]
    qs['Answer'] = row_values[1]
   

    q_list.append(qs)

# Serialize the list of dicts to JSON
j = json.dumps(q_list)

# Write to file
with open('data.json', 'w') as f:
    f.write(j)