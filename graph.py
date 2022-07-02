import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#plt.rcParams["figure.figsize"] = [7.50, 3.50]
#plt.rcParams["figure.autolayout"] = True

headers = ["Ubat","Iges","Pges","Ushunt","workTime","workPerc","mainTime","mainPerc","Idle1Time","Idle1Perc","Idle2Time","Idle2Perc","MIN_FREQ","MAX_FREQ"]

df1 = pd.read_csv('noop_test.csv')
df2 = pd.read_csv('add_test.csv')
df3 = pd.read_csv('mul_test.csv')

#sns.lmplot(x='Pges',y='MIN_FREQ',data=df,fit_reg=True) 

# create the figure and axes
fig, ax = plt.subplots(figsize=(6, 6))

# add the plots for each dataframe
sns.regplot(x='MIN_FREQ', y='Pges', data=df1, fit_reg=True, ci=None, ax=ax, label='NOOP')
sns.regplot(x='MIN_FREQ', y='Pges', data=df2, fit_reg=True, ci=None, ax=ax, label='ADD')
sns.regplot(x='MIN_FREQ', y='Pges', data=df3, fit_reg=True, ci=None, ax=ax, label='MUL')

ax.set(ylabel='mA', xlabel='CPU_FREQ')
ax.legend()
plt.show()
