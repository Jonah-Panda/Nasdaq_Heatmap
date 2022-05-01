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

#Sorting the dataframe off sector, then industry, then stock, based off of market capitalization
def Sorting(Column_Name):
    global SectorMarketCapDictionary
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
    if Column_Name == 'Sector':
        SectorMarketCapDictionary = tempDict
    del tempDict
    del Sorted_List
    List = []
    for index, row in df.iterrows():
        List.append(dictionary[row[Column_Name]])
    return List

def rgbspectrum(x):
    RED = [246, 52, 57]
    GRAY = [65, 69, 84]
    GREEN = [48, 204, 90]
    TOP_PERCENT_SCALE = 3 #percent
    BOTTOM_PERCENT_SCALE = -3 #percent
    if x >= TOP_PERCENT_SCALE:
        return GREEN
    elif x <= BOTTOM_PERCENT_SCALE:
        return RED
    elif x > 0:
        R = round((GREEN[0] - GRAY[0])*(x/TOP_PERCENT_SCALE)+GRAY[0],0)
        G = round((GREEN[1] - GRAY[1])*(x/TOP_PERCENT_SCALE)+GRAY[1],0)
        B = round((GREEN[2] - GRAY[2])*(x/TOP_PERCENT_SCALE)+GRAY[2],0)
        return [R, G, B]
    elif x < 0:
        R = round((RED[0] - GRAY[0])*(x/BOTTOM_PERCENT_SCALE)+GRAY[0],0)
        G = round((RED[1] - GRAY[1])*(x/BOTTOM_PERCENT_SCALE)+GRAY[1],0)
        B = round((RED[2] - GRAY[2])*(x/BOTTOM_PERCENT_SCALE)+GRAY[2],0)
        return [R, G, B]
    else:
        return GRAY


#############################################################
#####Getting Access to all the sorted data by market cap#####
path = os.getcwd()
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


os.chdir('{}/df_per_date'.format(path))
for index, row in df_MC.iterrows():
    if index > datetime.datetime(2016, 6, 6):
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

        #Pulls the price movement from the previous trading day for percent change calculation
        LTD_date = O_date
        LTD_date = LTD_date - datetime.timedelta(days=1)
        if LTD_date in df_MC.index:
            print(LTD_date, 'percent change')
        else:
            while LTD_date not in df_MC.index:
                LTD_date = LTD_date - datetime.timedelta(days=1)
            print(LTD_date, 'percent change')

        #Merges the dataframes for tickers
        temp_df = pd.DataFrame()
        temp_df['Ticker'] = df_MC.loc[LTD_date].index
        temp_df.set_index('Ticker', inplace=True)
        temp_df['Market_Cap_Yesterday'] = df_MC.loc[LTD_date]
        df = pd.merge(df, temp_df, on='Ticker',how='left')
        del temp_df
        df['percent_change'] = (df['Market_Cap']-df['Market_Cap_Yesterday'])/df['Market_Cap']*100
        #Getting sector data for yesterday
        Sector_MC_Yesterday = {}
        for index, row in df.iterrows():
            if row['Sector'] not in Sector_MC_Yesterday:
                Sector_MC_Yesterday[row['Sector']] = int(row['Market_Cap_Yesterday'])
            else:
                Sector_MC_Yesterday[row['Sector']] = Sector_MC_Yesterday[row['Sector']] + int(row['Market_Cap_Yesterday'])

        df.drop(columns=['Market_Cap_Yesterday'], inplace=True)
        df['RGB'] = df['percent_change'].apply(rgbspectrum)
        temp_df = pd.DataFrame(df['RGB'].values.tolist(), index=df.index, columns=['R', 'G', 'B'])
        df['R'] = temp_df['R']/255
        df['G'] = temp_df['G']/255
        df['B'] = temp_df['B']/255
        del temp_df
        df.drop(columns=['RGB'], inplace=True)


        SectorMarketCapDictionary = {}
        df['S_Rank'] = Sorting('Sector')
        df['I_Rank'] = Sorting('Industry')
        df['M_Rank'] = Sorting('Market_Cap')
        df['Rank'] = df['M_Rank'] + df['I_Rank'] * 1000 + df['S_Rank'] * 1000000
        df.drop(columns=['S_Rank', 'I_Rank', 'M_Rank'], inplace=True)
        df.sort_values(by=['Rank'], inplace=True)

        df['Temp_Ticker'] = df.index
        df.set_index('Rank', inplace=True)
        df['Ticker'] = df['Temp_Ticker']
        df.drop(columns=['Temp_Ticker'], inplace=True)
        df = df.reindex(['Ticker', 'Sector', 'Industry', 'Market_Cap', 'percent_change', 'R', 'G', 'B'], axis=1)
        
        #SQUARIFY PART##############################
        FirstLayerGroupingDictionary = {}
        FirstLayerTreemapCoordinates = {}
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
                            alpha = 0.5)

        for rect, name in zip(ax.patches, Names):
            (x, y), w, h = rect.get_xy(), rect.get_width(), rect.get_height()
            FirstLayerTreemapCoordinates[name] = (x, y), w-0.25, h-2 #these adjust the padding for the Sectors
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


        #Sorting Second Layer into their subplots (Industry)
        SubSetdict = {}
        TreemapCoordinates = {}
        SubSetdict = sectorgrouping(df.Sector.unique(), 'Sector', 'S_X_Y', 'S_Norm_X', 'S_Norm_Y')
        for key in SubSetdict:
            GroupingDictionary = {}
            for index, row in df.iterrows():
                if key == row['Sector']:
                    if row['Industry'] not in GroupingDictionary:
                        GroupingDictionary[row['Industry']] = int(row['Market_Cap'])
                    else:
                        GroupingDictionary[row['Industry']] = GroupingDictionary[row['Industry']] + int(row['Market_Cap'])
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
                TreemapCoordinates[name] = (x, y), w-0.2, h-0.2
            ax.patches = []
        #Creates Lists for all second layer rectangle coordinates to the dataframe for future reference
        I_X_Y = [] #Establishing the lists
        I_Norm_X = []
        I_Norm_Y = []
        #Itterates through based off of the dataframe
        for key in TreemapCoordinates:
            for index, row in df.iterrows():
                if key == row['Industry']:
                    I_X_Y.append(TreemapCoordinates[key][0])
                    I_Norm_X.append(TreemapCoordinates[key][1])
                    I_Norm_Y.append(TreemapCoordinates[key][2])
        #Appends the completed lists to the dataframe
        df['I_X_Y'] = I_X_Y
        df['I_Norm_X'] = I_Norm_X
        df['I_Norm_Y'] = I_Norm_Y


        #Sorting Third Layer into their subplots (Ticker)
        SubSetdict = {}
        TreemapCoordinates = {}
        SubSetdict = sectorgrouping(df.Industry.unique(), 'Industry', 'I_X_Y', 'I_Norm_X', 'I_Norm_Y')
        for key in SubSetdict:
            GroupingDictionary = {}
            for index, row in df.iterrows():
                if key == row['Industry']:
                    if row['Ticker'] not in GroupingDictionary:
                        GroupingDictionary[row['Ticker']] = int(row['Market_Cap'])
                    else:
                        GroupingDictionary[row['Ticker']] = GroupingDictionary[row['Ticker']] + int(row['Market_Cap'])

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
        #Creates Lists for all second layer rectangle coordinates to the dataframe for future reference
        T_X_Y = [] #Establishing the lists
        T_Width = []
        T_Height = []
        #Itterates through based off of the dataframe
        for key in TreemapCoordinates:
            for index, row in df.iterrows():
                if key == row['Ticker']:
                    T_X_Y.append(TreemapCoordinates[key][0])
                    T_Width.append(TreemapCoordinates[key][1])
                    T_Height.append(TreemapCoordinates[key][2])
        #Appends the completed lists to the dataframe
        df['T_X_Y'] = T_X_Y
        df['T_Width'] = T_Width
        df['T_Height'] = T_Height

        df_date = pd.DataFrame(columns=['Ticker', 'X', 'Y', 'Width', 'Height', 'Market_Cap', 'Pct_Change', 'R', 'G', 'B', 'Sector', 'Industry'])


        plt.clf()
        i = 0
        for index, row in df.iterrows():
            ticker = row['Ticker']
            X = row['S_X_Y'][0]+row['I_X_Y'][0]+row['T_X_Y'][0]
            Y = 100-row['S_X_Y'][1]-row['I_X_Y'][1]-row['T_X_Y'][1]-row['T_Height']-2
            Width = row['T_Width']
            Height = row['T_Height']
            Market_Cap = row['Market_Cap']
            Pct_Change = row['percent_change']
            R = row['R']
            G = row['G']
            B = row['B']
            Sector = row['Sector']
            Industry = row['Industry']
            df_date.loc[i] = [ticker, X, Y, Width, Height, Market_Cap, Pct_Change, R, G, B, Sector, Industry]
            #print(df_date)
            i = i + 1

            rect = Rectangle((X, Y), Width, Height, facecolor=(R, G, B), edgecolor = "black", linewidth = 0.5)
            plt.gca().add_patch(rect)
            plt.text(X+(Width/2), Y+(Height/2), ticker, verticalalignment = 'center', horizontalalignment = 'center', fontsize = 10)


        for key in FirstLayerTreemapCoordinates:
            Sector = key
            X = FirstLayerTreemapCoordinates[key][0][0]
            Y = 98-FirstLayerTreemapCoordinates[key][0][1]
            Width = FirstLayerTreemapCoordinates[key][1]-0.2
            Height = 1.9
            Market_Cap = SectorMarketCapDictionary[key]
            Pct_Change = (SectorMarketCapDictionary[key]-Sector_MC_Yesterday[key])/SectorMarketCapDictionary[key] * 100
            [R, G, B] = rgbspectrum(Pct_Change)
            R = [R, G, B][0]/255
            G = [R, G, B][1]/255
            B = [R, G, B][2]/255

            df_date.loc[i] = [Sector, X, Y, Width, Height, Market_Cap, Pct_Change, R, G, B, Sector, 'NA']
            i = i + 1

            plt.gca().add_patch(Rectangle((X, Y), Width, Height, edgecolor = "black", linewidth = 1, alpha = 0.5))
            plt.text(X+0.25, Y+0.1, Sector, verticalalignment = 'bottom', horizontalalignment='left', fontsize=8, weight='bold')

        df_date.to_csv('{}.csv'.format(O_date))
        plt.clf()



