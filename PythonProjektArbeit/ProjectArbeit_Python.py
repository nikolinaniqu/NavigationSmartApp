import numpy as np
import pandas as pd
import csv
import matplotlib
import plotly

file="Luftqualitaet_Konstanz01012024_21072025.csv"

with open(file,"r") as f:
    f=pd.read_csv(file)

df=pd.DataFrame(f)
print(df)