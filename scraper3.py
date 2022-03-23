import pandas as pd
import json

with open(r'resources\plz_verzeichnis_v2.json') as data_file:    
    data = json.load(data_file)  
df = pd.json_normalize(data)[['fields.kanton','fields.postleitzahl']]

print(df.shape)
print(df.columns)
#for col in df["fields.postleitzahl"].columns:
#    print(col)