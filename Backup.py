#Sorted healthcare two layered treemap with directional movement
import pandas as pd
import squarify
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.axes
import os
import datetime
import numpy as np
from time import sleep


plt.figure(figsize=(16, 9))
#Returns the (x, y) tuple, plus the width and height of the desired groups
def sectorgrouping (Subset_Unique_List, Subset_Column, Return_X_Y, Return_Norm_X, Return_Norm_Y):
    dictionary = {}
    for element in Subset_Unique_List:
        for index, row in df.iterrows():
            if element == row[Subset_Column]:
                dictionary[element] = [row[Return_X_Y], row[Return_Norm_X], row[Return_Norm_Y]]
    return dictionary


#Sorts the group by Market_Cap, and returns rectangle sizes
def grouping_one(Sector, dictionary, TreemapCoordinates): #Sector should have '' around it
    for index, row in df.iterrows():
        if row['Sector'] not in FirstLayerGroupingDictionary:
            FirstLayerGroupingDictionary[row['Sector']] = int(row['Market_Cap'])
        else:
            FirstLayerGroupingDictionary[row['Sector']] = FirstLayerGroupingDictionary[row['Sector']] + int(row['Market_Cap'])
    Sizes = []
    Names = []
    for key in FirstLayerGroupingDictionary:
        Sizes.append(FirstLayerGroupingDictionary[key])
        Names.append(key)

    ax = squarify.plot(
        sizes = Sizes,
        norm_x = 100,
        norm_y = 100,
        color = None,
        label = Names,
        alpha = 0.5,
        pad=False
    )
    for rect, name in zip(ax.patches, Names):
        (x, y), w, h = rect.get_xy(), rect.get_width(), rect.get_height()
        TreemapCoordinates[name] = (x, y), w-0.25, h-2
    ax.patches = []
    S_X_Y = []
    S_Norm_X = []
    S_Norm_Y = []
    for key in FirstLayerTreemapCoordinates:
        for index, row in df.iterrows():
            if key == row['Sector']:
                S_X_Y.append(FirstLayerTreemapCoordinates[key][0])
                S_Norm_X.append(FirstLayerTreemapCoordinates[key][1])
                S_Norm_Y.append(FirstLayerTreemapCoordinates[key][2])
    df['S_X_Y'] = S_X_Y
    df['S_Norm_X'] = S_Norm_X
    df['S_Norm_Y'] = S_Norm_Y


def grouping_two(column_in_df, Subset_Unique_List, Subset_Column, Return_X_Y, Return_Norm_X, Return_Norm_Y):
    SubSetdict = {}
    TreemapCoordinates = {}
    SubSetdict = sectorgrouping(Subset_Unique_List, Subset_Column, Return_X_Y, Return_Norm_X, Return_Norm_Y)
    for key in SubSetdict:
        GroupingDictionary = {}
        for index, row in df.iterrows():
            if key == row[Subset_Column]:
                if row[column_in_df] not in GroupingDictionary:
                    GroupingDictionary[row[column_in_df]] = int(row['Market_Cap'])
                else:
                    GroupingDictionary[row[column_in_df]] = GroupingDictionary[row[column_in_df]] + int(row['Market_Cap'])

        Sizes = []
        Names = []
        for industrykey in GroupingDictionary:
            Sizes.append(GroupingDictionary[industrykey])
            Names.append(industrykey)

        ax = squarify.plot(
            sizes = Sizes,
            norm_x = SubSetdict[key][1],
            norm_y = SubSetdict[key][2],
            color = None,
            label = Names,
            alpha = 0.5
        )
        for rect, name in zip(ax.patches, Names):
            (x, y), w, h = rect.get_xy(), rect.get_width(), rect.get_height()
            TreemapCoordinates[name] = (x, y), w, h
        ax.patches = []
    print(df)
    if len(df.columns) == 7:
        #Creates Lists for all second layer rectangle coordinates to the dataframe for future reference
        I_X_Y = [] #Establishing the lists
        I_Norm_X = []
        I_Norm_Y = []
        #Itterates through based off of the dataframe
        for key in TreemapCoordinates:
            for index, row in df.iterrows():
                if key == row[column_in_df]:
                    I_X_Y.append(TreemapCoordinates[key][0])
                    I_Norm_X.append(TreemapCoordinates[key][1])
                    I_Norm_Y.append(TreemapCoordinates[key][2])
        #Appends the completed lists to the dataframe
        df['I_X_Y'] = I_X_Y
        df['I_Norm_X'] = I_Norm_X
        df['I_Norm_Y'] = I_Norm_Y
    elif len(df.columns == 10):
        #Creates Lists for all second layer rectangle coordinates to the dataframe for future reference
        T_X_Y = [] #Establishing the lists
        T_Width = []
        T_Height = []
        #Itterates through based off of the dataframe
        for key in TreemapCoordinates:
            for index, row in df.iterrows():
                if key == row[column_in_df]:
                    T_X_Y.append(TreemapCoordinates[key][0])
                    T_Width.append(TreemapCoordinates[key][1])
                    T_Height.append(TreemapCoordinates[key][2])
        #Appends the completed lists to the dataframe
        df['T_X_Y'] = T_X_Y
        df['T_Width'] = T_Width
        df['T_Height'] = T_Height
    else:
        print('There are more than 7 OR 10 columns')



#############################################################
#####Getting Access to all the sorted data by market cap#####
path = os.getcwd()
print(path)
os.chdir('{}/Sorting'.format(path))

#Imports Market Cap historical data (to June 8 2021)
df_MC = pd.read_csv('MC_History.csv')
df_MC['Date'] = pd.to_datetime(df_MC['Date'])
df_MC.set_index('Date', inplace=True)

#Imports the historical changes to the Nasdaq-100
df_US100_Changes_untransposed = pd.read_csv('Nasdaq-100 Company History (2016-2021).csv')
df_Nas = df_US100_Changes_untransposed.transpose()
df_Nas.index.name = 'Date'
df_Nas.index = pd.to_datetime(df_Nas.index)

#Imports the sectors and industries
df_Sectors = pd.read_csv('Sectors_and_Industries.csv')
df_Sectors.set_index('Ticker', inplace=True)

#Establishing the master DF
Master_df = pd.DataFrame()

for index, row in df_MC.iterrows():
    if index > datetime.datetime(2021, 1, 1):
        date = index
        print(date)
        #Establishing the dataframe used for each dat
        df = pd.DataFrame()

        O_date = date

        #Getting the most recent nasdaq index 100 companies
        if date in df_Nas.index:
            print(date, 'Last Change')
        else: 
            while date not in df_Nas.index:
                date = date - datetime.timedelta(days=1)
            print(date, 'Last Change')
        tickers = df_Nas.loc[date]
        df['Ticker'] = tickers
        df.set_index('Ticker', inplace=True)

        #Pulls the sector, industry, and marketcap data for a specific date
        df = pd.merge(df, df_Sectors, on='Ticker', how='left')
        temp_df = pd.DataFrame()
        temp_df['Ticker'] = df_MC.loc[O_date].index
        temp_df.set_index('Ticker', inplace=True)
        temp_df['Market_Cap'] = df_MC.loc[O_date]
        df = pd.merge(df, temp_df, on='Ticker',how='left')
        del temp_df

        #Sorting the dataframe off sector, then industry, then stock, based off of market capitalization
        def Sorting(Column_Name):
            tempDict = {}
            for index, row in df.iterrows():
                #print(index, '\t', 'Sector:', row['Sector'], '\t', 'Industry:', row['Industry'],'\t', 'Market_Cap:', row['Market_Cap'])
                if row[Column_Name] not in tempDict:
                    tempDict[row[Column_Name]] = row['Market_Cap']
                else:
                    tempDict[row[Column_Name]] = tempDict[row[Column_Name]] + row['Market_Cap']

            dictionary = {}
            Sorted_List = sorted(tempDict.items(), key=lambda x: x[1], reverse=True)
            i = 0
            for item in Sorted_List:
                i = i + 1
                dictionary[item[0]] = i
            del tempDict
            del Sorted_List
            List = []
            #print(df.head(50))
            #print(df.tail(50))
            for index, row in df.iterrows():
                List.append(dictionary[row[Column_Name]])
            return List

        df['S_Rank'] = Sorting('Sector')
        df['I_Rank'] = Sorting('Industry')
        df['M_Rank'] = Sorting('Market_Cap')
        df['Rank'] = df['M_Rank'] + df['I_Rank'] * 1000 + df['S_Rank'] * 1000000
        df.drop(columns=['S_Rank', 'I_Rank', 'M_Rank'], inplace=True)
        df.sort_values(by=['Rank'], inplace=True)

        df['Temp_Ticker'] = df.index
        df.set_index('Rank', inplace=True)
        df['Ticker'] = df['Temp_Ticker']
        df.drop(columns=['Temp_Ticker'])
        df = df.reindex(['Ticker', 'Sector', 'Industry', 'Market_Cap'], axis=1)
        print(df)
        #Sorting the first layer dictionary (Sector)
        FirstLayerGroupingDictionary = {}
        FirstLayerTreemapCoordinates = {}
        grouping_one('Sector', FirstLayerGroupingDictionary, FirstLayerTreemapCoordinates)

        #Sorting Second Layer into their subplots (Industry)
        #Industry to be sorted, df.nextlayerout.unique(), nextlayerout, nextlayerout(x,y), norm_x, norm_y
        grouping_two('Industry', df.Sector.unique(), 'Sector', 'S_X_Y', 'S_Norm_X', 'S_Norm_Y')

        #Sorting Third Layer into their subplots (Ticker)
        #Ticker to be sorted, df.nextlayerout.unique(), nextlayerout, nextlayerout(x,y), norm_x, norm_y
        grouping_two('Ticker', df.Industry.unique(), 'Industry', 'I_X_Y', 'I_Norm_X', 'I_Norm_Y')

        print(df)
        plt.clf()
        for index, row in df.iterrows():
            ticker = row['Ticker']
            X = row['S_X_Y'][0]+row['I_X_Y'][0]+row['T_X_Y'][0]
            Y = 100-row['S_X_Y'][1]-row['I_X_Y'][1]-row['T_X_Y'][1]-row['T_Height']-2
            width = row['T_Width']
            height = row['T_Height']
            Market_Cap = row['Market_Cap']
            #pct_change = 'NEEEEDDDDD TO FILLLL IN'#######################
            #R = R
            #G = G
            #B = B
            Sector = row['Sector']
            Industry = row['Industry']

            XY = (X, Y)
            rect = Rectangle(XY, width, height, edgecolor = "black", linewidth = 1, alpha = 0.5)
            plt.gca().add_patch(rect)
            plt.text(XY[0]+(row['T_Width']/2), XY[1]+(row['T_Height']/2), row['Ticker'], verticalalignment = 'center', horizontalalignment = 'center', fontsize = 15)
        
        plt.gca().add_patch(Rectangle((0,98), 47.638, 2))
        plt.text(0, 98, 'Technology', verticalalignment = 'bottom', horizontalalignment='left', fontsize=7)
        plt.xlim([0,100])
        plt.ylim([0,100])
        plt.show()
        break