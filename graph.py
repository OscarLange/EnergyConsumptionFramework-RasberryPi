import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error
from sklearn.linear_model import RidgeCV
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from skspatial.objects import Plane
from skspatial.objects import Points
from skspatial.plotting import plot_3d
from sklearn.tree import export_graphviz
import pydot
import os 
dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"

#headers = ["Ubat","Iges","Pges","Ushunt","workTime","workPerc","mainTime","mainPerc","Idle1Time","Idle1Perc","Idle2Time","Idle2Perc","MIN_FREQ","MAX_FREQ"]

#read training data
# df1 = pd.read_csv('./first_try/training/noop_test.csv')
# df2 = pd.read_csv('./first_try/training/add_test.csv')
# df3 = pd.read_csv('./first_try/training/sub_test.csv')
# df4 = pd.read_csv('./first_try/training/mul_test.csv')
# df5 = pd.read_csv('./first_try/training/div_test.csv')
# df6 = pd.read_csv('./first_try/training/addf_test.csv')
# df7 = pd.read_csv('./first_try/training/subf_test.csv')
# df8 = pd.read_csv('./first_try/training/mulf_test.csv')
# df9 = pd.read_csv('./first_try/training/divf_test.csv')


# #sort training data 
# df1 = df1.sort_values(by=['MIN_FREQ', 'workPerc'])
# df2 = df2.sort_values(by=['MIN_FREQ', 'workPerc'])
# df3 = df3.sort_values(by=['MIN_FREQ', 'workPerc'])
# df4 = df4.sort_values(by=['MIN_FREQ', 'workPerc'])
# df5 = df5.sort_values(by=['MIN_FREQ', 'workPerc'])
# df6 = df6.sort_values(by=['MIN_FREQ', 'workPerc'])
# df7 = df7.sort_values(by=['MIN_FREQ', 'workPerc'])
# df8 = df8.sort_values(by=['MIN_FREQ', 'workPerc'])
# df9 = df9.sort_values(by=['MIN_FREQ', 'workPerc'])

# #read test data
# df1_1 = pd.read_csv('./test/noop_test.csv')
# df1_2 = pd.read_csv('./test/add_test.csv')
# df1_3 = pd.read_csv('./test/sub_test.csv')
# df1_4 = pd.read_csv('./test/mul_test.csv')
# df1_5 = pd.read_csv('./test/div_test.csv')
# df1_6 = pd.read_csv('./test/addf_test.csv')
# df1_7 = pd.read_csv('./test/subf_test.csv')
# df1_8 = pd.read_csv('./test/mulf_test.csv')
# df1_9 = pd.read_csv('./test/divf_test.csv')

# #sort test data
# df1_1 = df1_1.sort_values(by=['MIN_FREQ', 'workPerc'])
# df1_2 = df1_2.sort_values(by=['MIN_FREQ', 'workPerc'])
# df1_3 = df1_3.sort_values(by=['MIN_FREQ', 'workPerc'])
# df1_4 = df1_4.sort_values(by=['MIN_FREQ', 'workPerc'])
# df1_5 = df1_5.sort_values(by=['MIN_FREQ', 'workPerc'])
# df1_6 = df1_6.sort_values(by=['MIN_FREQ', 'workPerc'])
# df1_7 = df1_7.sort_values(by=['MIN_FREQ', 'workPerc'])
# df1_8 = df1_8.sort_values(by=['MIN_FREQ', 'workPerc'])
# df1_9 = df1_9.sort_values(by=['MIN_FREQ', 'workPerc'])

#improved training data
df2_new = pd.read_csv('./training/add_test.csv')

#sort improved training data
df2_new = df2_new.sort_values(by=['MIN_FREQ', 'workPerc'])

#improved test data
df1_2_new = pd.read_csv('./test/add_test.csv')

#sort improved test data
df1_2_new = df1_2_new.sort_values(by=['MIN_FREQ', 'workPerc'])


#add binary columns to indicate the operand type
def combine_with_columns(df1, df2, df3, df4, df5, df6, df7, df8, df9):
    dataframe = [df1, df2, df3, df4, df5, df6, df7, df8, df9]
    for i in range(0,9):
        dataframe[i]["noop"] = 1 if i == 0 else 0
        dataframe[i]["add"] = 1 if i == 1 else 0
        dataframe[i]["sub"] = 1 if i == 2 else 0
        dataframe[i]["mul"] = 1 if i == 3 else 0
        dataframe[i]["div"] = 1 if i == 4 else 0
        dataframe[i]["addf"] = 1 if i == 5 else 0
        dataframe[i]["subf"] = 1 if i == 6 else 0
        dataframe[i]["mulf"] = 1 if i == 7 else 0
        dataframe[i]["divf"] = 1 if i == 8 else 0

    return pd.concat(dataframe)

def combine_training_frames():
    return pd.concat([df1, df2, df3, df4, df5, df6, df7, df8, df9])

def combine_test_frames():
    return pd.concat([df1_1, df1_2, df1_3, df1_4, df1_5, df1_6, df1_7, df1_8, df1_9])

def drop_irrelevant_features(df):
    df = df.drop("Pges", axis = 1)
    df = df.drop("Ubat", axis = 1)
    df = df.drop("Iges", axis = 1)
    df = df.drop("Ushunt", axis = 1)
    df = df.drop("workPerc", axis = 1)
    df = df.drop("mainPerc", axis = 1)
    df = df.drop("Idle1Perc", axis = 1)
    df = df.drop("Idle2Perc", axis = 1)
    df = df.drop("Idle2Time", axis = 1)
    df = df.drop("MAX_FREQ", axis = 1)
    return df


def random_forrest():
    #training_frame = combine_training_frames()
    training_frame = df2_new
    test_frame = df1_2_new
    #test_frame = combine_test_frames()

    labels = np.array(training_frame["Pges"])
    training_frame = drop_irrelevant_features(training_frame)
    print(training_frame)

    feature_list = list(training_frame.columns)
    features = np.array(training_frame)

    rf = RandomForestRegressor(n_estimators=500, random_state=42)
    rf.fit(features, labels)

    predictions = rf.predict(features)

    errors = mean_squared_error(labels, predictions)
    print(errors)

    tree = rf.estimators_[50]
    export_graphviz(tree, out_file="tree.dot", feature_names=feature_list, rounded=True, precision= 1)
    (graph, ) = pydot.graph_from_dot_file(dir_path + 'tree.dot')

    graph.write_png(dir_path + "tree_without_electrical_duplicate2.png")

    labels2 = np.array(test_frame["Pges"])
    test_frame = drop_irrelevant_features(test_frame)
    features_test = np.array(test_frame)

    predictions_test = rf.predict(features_test)

    mse = mean_squared_error(labels2, predictions_test)
    print(mse)
    print(np.sqrt(mse))

    mae = mean_absolute_error(labels2, predictions_test)
    print(mae)

    meae = median_absolute_error(labels2, predictions_test)
    print(meae)


def numpy_polyfit():
    #training_frame = combine_training_frames()
    #test_frame = combine_test_frames()

    #sort for graph of 2nd degree
    #training_frame = training_frame.sort_values(by=['workPerc'])
    #test_frame = test_frame.sort_values(by=['workPerc'])

    training_frame = df2_new
    test_frame = df1_2_new

    df_tmp=training_frame[training_frame["MIN_FREQ"] == 80]
    df_tmp1=training_frame[training_frame["MIN_FREQ"] == 160]
    df_tmp2=training_frame[training_frame["MIN_FREQ"] == 240]


    X = df_tmp["workPerc"].to_numpy()
    X1 = df_tmp1["workPerc"].to_numpy()
    X2 = df_tmp2["workPerc"].to_numpy()

    y = df_tmp["Pges"]
    y1 = df_tmp1["Pges"]
    y2 = df_tmp2["Pges"]

    coefs, residual, _, _, _ = np.polyfit(X, y, 1, full=True)
    coefs1, residual1, _, _, _ = np.polyfit(X1, y1, 1, full=True)
    coefs2, residual2, _, _, _ = np.polyfit(X2, y2, 2, full=True)
    print(residual/len(X))
    print(residual1/len(X1))
    print(residual2/len(X2))

    poly1d = np.poly1d(coefs)
    poly1d1 = np.poly1d(coefs1)
    poly1d2 = np.poly1d(coefs2)

    #test data
    df_tmp1_1=test_frame[test_frame["MIN_FREQ"] == 80]
    df_tmp1_2=test_frame[test_frame["MIN_FREQ"] == 160]
    df_tmp1_3=test_frame[test_frame["MIN_FREQ"] == 240]

    X_test = df_tmp1_1["workPerc"].to_numpy()
    X1_test = df_tmp1_2["workPerc"].to_numpy()
    X2_test = df_tmp1_3["workPerc"].to_numpy()

    y_test = df_tmp1_1["Pges"]
    y1_test = df_tmp1_2["Pges"]
    y2_test = df_tmp1_3["Pges"]

    prediction = np.polyval(poly1d, X_test)
    errors = prediction - y_test
    
    mse = np.mean(np.square(errors))
    print(mse)
    print(np.sqrt(mse))

    mae = np.mean(np.abs(errors))
    print(mae)

    meae = np.median(np.abs(errors))
    print(meae)

    plt.scatter(X_test, y_test, color = 'blue')
    plt.plot(X, poly1d(X), color = 'blue', label="ADD_80")
    plt.scatter(X1_test, y1_test, color = 'orange')
    plt.plot(X1, poly1d1(X1), color = 'orange', label="ADD_160")
    plt.scatter(X2_test, y2_test, color = 'green')
    plt.plot(X2, poly1d2(X2), color = 'green', label="ADD_240")

    plt.xlabel('Work Percentage')
    plt.ylabel('Power Consumption')
    plt.legend()

    plt.show()


def sk_learn_ridge_regression():
    df_tmp=df2[df2["MIN_FREQ"] == 240]
    #df_tmp=df2[df2["MIN_FREQ"] == 160]
    #df_tmp=df2[df2["MIN_FREQ"] == 240]

    X = df_tmp[["workPerc"]]
    y = df_tmp[["Pges"]]

    regressor = LinearRegression()
    regressor.fit(X, y)

    regr_trans = TransformedTargetRegressor(
        regressor=RidgeCV(), func=np.log1p, inverse_func=np.expm1
    )

    regr_trans.fit(X, y)
    y_pred = regr_trans.predict(X)

    print(mean_squared_error(y, y_pred))

    plt.scatter(X, y, color = 'red')
    plt.plot(X["workPerc"], regr_trans.predict(X), color = 'blue')
    plt.title('CPU FRequency and Power Consumption')
    plt.xlabel('CPU FREQ')
    plt.ylabel('Power')
    plt.show()
    
def sk_learn_regression():
    df_tmp=df2[df2["MIN_FREQ"] == 80] 
    #df_tmp=df2[df2["MIN_FREQ"] == 160]
    #df_tmp=df2[df2["MIN_FREQ"] == 240]

    X = df_tmp[["workPerc"]]
    y = df_tmp[["Pges"]]

    regressor = LinearRegression()
    regressor.fit(X, y)

    y_pred = regressor.predict(X)

    print(mean_squared_error(y, y_pred))

    plt.scatter(X, y, color = 'red')
    plt.plot(X["workPerc"], regressor.predict(X), color = 'blue')
    plt.title('CPU FRequency and Power Consumption')
    plt.xlabel('CPU FREQ')
    plt.ylabel('Power')
    plt.show()

def seaborn_regression():
    # create the figure and axes
    fig, ax = plt.subplots(figsize=(6, 6))

    #df_tmp1=df1[df1["workPerc"] > 50] 
    #df_tmp2=df2[df2["workPerc"] > 50]

    #df_tmp1=df2[df2["workPerc"] < 30] 
    #df_tmp2_1=df2[40 < df2["workPerc"]]
    #df_tmp2 = df_tmp2_1[df2["workPerc"] < 60] 
    #df_tmp3_1=df2[70 < df2["workPerc"]]
    #df_tmp3 = df_tmp3_1[df2["workPerc"] < 80] 
    #df_tmp4=df2[df2["workPerc"] > 90] 

    #df_tmp1=df2[df2["MIN_FREQ"] == 80] 
    #df_tmp2=df2[df2["MIN_FREQ"] == 160]
    #df_tmp3=df2[df2["MIN_FREQ"] == 240]

    #df_tmp4=df1[df1["MIN_FREQ"] == 80] 
    #df_tmp5=df1[df1["MIN_FREQ"] == 160]
    #df_tmp6=df1[df1["MIN_FREQ"] == 240]
    
    
    #sns.regplot(x='workPerc', y='Pges', data=df_tmp1, fit_reg=True, ci=None, ax=ax, label='ADD_80')
    #sns.regplot(x='workPerc', y='Pges', data=df_tmp2, fit_reg=True, ci=None, ax=ax, label='ADD_160')
    #sns.regplot(x='workPerc', y='Pges', data=df_tmp3, fit_reg=True, ci=None, ax=ax, label='ADD_240')
    
    #sns.regplot(x='workPerc', y='Pges', data=df_tmp4, fit_reg=True, ci=None, ax=ax, label='NOOP_80')
    #sns.regplot(x='workPerc', y='Pges', data=df_tmp5, fit_reg=True, ci=None, ax=ax, label='NOOP_160')
    #sns.regplot(x='workPerc', y='Pges', data=df_tmp6, fit_reg=True, ci=None, ax=ax, label='NOOP_240')
    
    # add the plots for each dataframe
    #sns.regplot(x='MIN_FREQ', y='Pges', data=df1, fit_reg=True, ci=None, ax=ax, label='NOOP')
    #sns.regplot(x='MIN_FREQ', y='Pges', data=df2, fit_reg=True, ci=None, ax=ax, label='ADD')
    #sns.regplot(x='MIN_FREQ', y='Pges', data=df3, fit_reg=True, ci=None, ax=ax, label='SUB')
    #sns.regplot(x='MIN_FREQ', y='Pges', data=df4, fit_reg=True, ci=None, ax=ax, label='MUL')
    sns.regplot(x='MIN_FREQ', y='Pges', data=df5, fit_reg=True, ci=None, ax=ax, label='DIV')
    #sns.regplot(x='MIN_FREQ', y='Pges', data=df6, fit_reg=True, ci=None, ax=ax, label='ADDF')
    #sns.regplot(x='MIN_FREQ', y='Pges', data=df7, fit_reg=True, ci=None, ax=ax, label='SUBF')
    #sns.regplot(x='MIN_FREQ', y='Pges', data=df8, fit_reg=True, ci=None, ax=ax, label='MULF')
    sns.regplot(x='MIN_FREQ', y='Pges', data=df9, fit_reg=True, ci=None, ax=ax, label='DIVF')
    
    #sns.regplot(x='MIN_FREQ', y='Pges', data=df_tmp1, fit_reg=True, ci=None, ax=ax, label='ADD_25')
    #sns.regplot(x='MIN_FREQ', y='Pges', data=df_tmp2, fit_reg=True, ci=None, ax=ax, label='ADD_50')
    #sns.regplot(x='MIN_FREQ', y='Pges', data=df_tmp3, fit_reg=True, ci=None, ax=ax, label='ADD_75')
    #sns.regplot(x='MIN_FREQ', y='Pges', data=df_tmp4, fit_reg=True, ci=None, ax=ax, label='ADD_100')
    
    #sns.regplot(x='workPerc', y='Pges', data=df_tmp1, fit_reg=True, ci=None, ax=ax, label='ADD_80')
    #sns.regplot(x='workPerc', y='Pges', data=df_tmp2, fit_reg=True, ci=None, ax=ax, label='ADD_160')
    #sns.regplot(x='workPerc', y='Pges', data=df_tmp3, fit_reg=True, ci=None, ax=ax, label='ADD_240')

    ax.set(ylabel='mA', xlabel='CPU FREQ')
    ax.legend()
    plt.show()

def three_dimensional_scatter():
    plot = plt.figure().gca(projection='3d')
    #plot.scatter(df1['MIN_FREQ'], df1['workPerc'], df1['Pges'])
    df_tmp = df2[["MIN_FREQ", "workPerc", "Pges"]]
    df_tmp2 = df_tmp.groupby(['MIN_FREQ', 'workPerc']).mean().reset_index()
    plot.scatter(df_tmp2['MIN_FREQ'], df_tmp2['workPerc'], df_tmp2['Pges'])
    plot.set_xlabel('CPU_FREQ')
    plot.set_ylabel('CPU_UTIL')
    plot.set_zlabel('Pges')
    plt.show()

def three_dimensional_plane():
    df_tmp = df2[["MIN_FREQ", "workPerc", "Pges"]]
    df_tmp2 = df_tmp.groupby(['MIN_FREQ', 'workPerc']).mean().reset_index()
    array = df_tmp2.to_numpy()
    print(df_tmp2)
    points = Points(array)
    plane = Plane.best_fit(points)
    fig, ax = plot_3d(
        points.plotter(c='k', s=50, depthshade=False),
        plane.plotter(alpha=0.2, lims_x=(-5, 5), lims_y=(-5, 5)),
    )
    plt.show()

random_forrest()
#numpy_polyfit()
#sk_learn_regression()
#sk_learn_ridge_regression()
#three_dimensional_scatter()
#three_dimensional_plane()
#seaborn_regression()