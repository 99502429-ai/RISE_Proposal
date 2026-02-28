import pandas as pd

df = pd.read_csv('pol_clean.csv')

print(f'Total: {df.size}')
print(f'Threads: {df.drop_duplicates(subset=['thread']).size}')