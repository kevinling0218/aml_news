import pandas as pd

df = pd.read_csv('params.csv')
range_lower = 180
range_upper = 192

df['query'] = df['query'].str.strip().str.replace('&', '%26')
df['file'] = df['file'].str.strip()
df['micro_files'] = df['micro_files'].astype(str)

df.loc[range(13, 25), 'file'] = df.loc[range(13, 25), 'query'].map(lambda x: x.lower().replace("-", "_").replace(" ", "_"))
df.loc[range(26, 38), 'file'] = df.loc[range(26, 38), 'query'].map(lambda x: x.lower().replace("-", "_").replace(" ", "_"))
df.loc[range(39, 63), 'file'] = df.loc[range(39, 63), 'query'].map(lambda x: x.lower().replace("-", "_").replace(" ", "_"))
df.loc[range(63, 72), 'file'] = df.loc[range(63, 72), 'query'].map(lambda x: x.lower().replace("-", "_").replace(" ", "_"))
df.loc[range(74, 80), 'file'] = df.loc[range(74, 80), 'query'].map(lambda x: x.lower().replace("-", "_").replace(" ", "_"))
df.loc[range(81, 93), 'file'] = df.loc[range(81, 93), 'query'].map(lambda x: x.lower().replace("-", "_").replace(" ", "_"))
df.loc[range(94, 98), 'file'] = df.loc[range(94, 98), 'query'].map(lambda x: x.lower().replace("-", "_").replace(" ", "_"))
df.loc[range(99, 103), 'file'] = df.loc[range(99, 103), 'query'].map(lambda x: x.lower().replace("-", "_").replace(" ", "_"))
df.loc[range(range_lower, range_upper), 'file'] = df.loc[range(range_lower, range_upper), 'query'].map(lambda x: x.lower().replace("-", "_").replace(" ", "_"))


df.loc[range(0, 12), 'query'] = df.loc[range(0, 12), 'query'].map(lambda x: f'"{x}"')
df.loc[range(13, 25), 'query'] = df.loc[range(13, 25), 'query'].map(lambda x: f'"{x}"')
df.loc[range(26, 38), 'query'] = df.loc[range(26, 38), 'query'].map(lambda x: f'"{x}"')
df.loc[range(39, 63), 'query'] = df.loc[range(39, 63), 'query'].map(lambda x: f'"{x}"')
df.loc[range(63, 72), 'query'] = df.loc[range(63, 72), 'query'].map(lambda x: f'"{x}"')
df.loc[range(74, 80), 'query'] = df.loc[range(74, 80), 'query'].map(lambda x: f'"{x}"')
df.loc[range(81, 93), 'query'] = df.loc[range(81, 93), 'query'].map(lambda x: f'"{x}"')
df.loc[range(94, 98), 'query'] = df.loc[range(94, 98), 'query'].map(lambda x: f'"{x}"')
df.loc[range(99, 103), 'query'] = df.loc[range(99, 103), 'query'].map(lambda x: f'"{x}"')
df.loc[range(range_lower, range_upper), 'query'] = df.loc[range(range_lower, range_upper), 'query'].map(lambda x: f'"{x}"')



df.at[25, 'micro_files'] = '|'.join(list(df.loc[range(13, 25), 'file']))
df.at[38, 'micro_files'] = '|'.join(list(df.loc[range(26, 38), 'file']))
df.at[72, 'micro_files'] = '|'.join(list(df.loc[range(63, 72), 'file']))
df.at[80, 'micro_files'] = '|'.join(list(df.loc[range(73, 80), 'file']))
df.at[93, 'micro_files'] = '|'.join(list(df.loc[range(81, 93), 'file']))
df.at[98, 'micro_files'] = '|'.join(list(df.loc[range(94, 98), 'file']))
df.at[103, 'micro_files'] = '|'.join(list(df.loc[range(99, 103), 'file']))
df.at[112, 'micro_files'] = '|'.join(list(df.loc[range(104, 112), 'file']))
df.at[range_upper, 'micro_files'] = '|'.join(list(df.loc[range(range_lower, range_upper), 'file']))



df.to_csv('params.csv', index=False)
