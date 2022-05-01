import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.axes
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation #, writers
import os
import datetime
import numpy as np
from time import sleep
import pandas_datareader.data as web
import sys
import ssl
import squarify
import time

#Start and End dates
START = datetime.datetime(2021, 8, 2)
END = datetime.date.today()
END = datetime.datetime(2021, 8, 26)

for i in range(10):
    print()

#HTTPS Security bypass
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context



def dt_convert(date):
    return int(time.mktime(date.timetuple()))

#Strips webscraped numbers of their B, M, or K rounded abbreviations
def value_to_float(x):
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace('K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        return float(x.replace('B', '')) * 1000000000
    return 0.0

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

def Sorting(Column_Name, df):
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


#Returns the (x, y) tuple, plus the width and height of the desired groups
def sectorgrouping (Subset_Unique_List, Subset_Column, Return_X_Y, Return_Norm_X, Return_Norm_Y):
    dictionary = {}
    for element in Subset_Unique_List:
        for index, row in df.iterrows():
            if element == row[Subset_Column]:
                dictionary[element] = [row[Return_X_Y], row[Return_Norm_X], row[Return_Norm_Y]]
    return dictionary

def webscrape(date):
    global df
    df_date = pd.DataFrame(columns=['Ticker', 'X', 'Y', 'Width', 'Height', 'Market_Cap', 'Pct_Change', 'R', 'G', 'B', 'Sector', 'Industry'])
    payload = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
    df_companies = payload[3]
    df_companies.set_index('Ticker', inplace=True)#.drop(['GOOGL', 'FOX'], inplace=True)
    #print(df_companies)
    df_companies.drop(['GOOGL', 'FOX'], inplace=True)
    df_companies.reset_index(inplace=True)

    df = pd.DataFrame(columns=['Ticker', 'Market_Cap', 'Market_Cap_Yesterday','Pct_Change', 'Sector', 'Industry'])
    i = 0
    for index, row in df_companies.iterrows():
        ticker = row['Ticker']
        #downloads the two tables for the shares outstanding history from ycharts
        payload=pd.read_html('https://ycharts.com/companies/{}/shares_outstanding'.format(ticker),parse_dates=True)
        df1 = payload[0]

        #indexing and datetimeing
        df1.columns = ['Date', 'Shares']
        df1['Date'] = pd.to_datetime(df1['Date'])
        df1.set_index('Date', inplace=True)
        #Stirping the (K,M,B from the shares outstanding number)
        df1['Shares'] = df1['Shares'].apply(value_to_float)

        end = date
        start = df_Nas.loc[date, 'LTD']
        yahooend = end + datetime.timedelta(days=1)

        #Downloads yahoo data
        #price_history = web.DataReader('{}'.format(ticker), 'yahoo', start, end)
        ################################################## ERROR WITH YAHOO
        query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={dt_convert(start)}&period2={dt_convert(yahooend)}&interval=1d&events=history&includeAdjustedClose=true'
        price_history = pd.read_csv(query_string)
        price_history.set_index('Date', inplace=True)
        price_history.index = pd.to_datetime(price_history.index)

        #Merges both dataframes
        price_history['Shares Outstanding'] = np.nan
        for line in price_history.iterrows():
            if line[0] in df1.index:
                price_history.loc[line[0], 'Shares Outstanding'] = df1.loc[line[0], 'Shares']
            else:
                #Fixes dates before start of pricehistory df, and holidays
                tempdate = line[0]
                while tempdate not in df1.index:
                    tempdate = tempdate - datetime.timedelta(days=1)    
                price_history.loc[line[0], 'Shares Outstanding'] = df1.loc[tempdate, 'Shares']
        
        #To fill in all shares outstanding gaps between reporting dates
        price_history['Shares Outstanding'].interpolate(method='linear', inplace = True)

        #Calculates market cap for the company
        price_history['Market Cap'] = price_history['Adj Close'] * price_history['Shares Outstanding']

        #adding all new data to the dataframe for the 'date'
        Market_Cap = price_history.loc[end, 'Market Cap']
        Market_Cap_Yesterday = price_history.loc[start,'Market Cap']
        Pct_Change = (price_history.loc[end, 'Market Cap']-price_history.loc[start, 'Market Cap'])/price_history.loc[start, 'Market Cap']*100
        Sector = row['GICS Sector']
        Industry = row['GICS Sub-Industry']
        df.loc[i] = [ticker, Market_Cap, Market_Cap_Yesterday, Pct_Change, Sector, Industry]
        print(i+1, 'percent complete for ', date, ticker, '\t', end='\r')
        i = i + 1
        

    df['RGB'] = df['Pct_Change'].apply(rgbspectrum)
    temp_df = pd.DataFrame(df['RGB'].values.tolist(), index=df.index, columns=['R', 'G', 'B'])
    df['R'] = temp_df['R']/255
    df['G'] = temp_df['G']/255
    df['B'] = temp_df['B']/255
    del temp_df
    df.drop(columns=['RGB'], inplace=True)

    df['S_Rank'] = Sorting('Sector', df)
    df['I_Rank'] = Sorting('Industry', df)
    df['M_Rank'] = Sorting('Market_Cap', df)
    df['Rank'] = df['M_Rank'] + df['I_Rank'] * 1000 + df['S_Rank'] * 1000000
    df.drop(columns=['S_Rank', 'I_Rank', 'M_Rank'], inplace=True)
    df.sort_values(by=['Rank'], inplace=True)
    df.set_index('Rank', inplace=True)
    df = df.reindex(['Ticker', 'Sector', 'Industry', 'Market_Cap','Market_Cap_Yesterday', 'Pct_Change', 'R', 'G', 'B'], axis=1)

    #Getting sector data for yesterday
    Sector_MC_Yesterday = {}
    for index, row in df.iterrows():
        if row['Sector'] not in Sector_MC_Yesterday:
            Sector_MC_Yesterday[row['Sector']] = int(row['Market_Cap_Yesterday'])
        else:
            Sector_MC_Yesterday[row['Sector']] = Sector_MC_Yesterday[row['Sector']] + int(row['Market_Cap_Yesterday'])

    plt.figure(figsize=(16*2, 9*2))
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

    #Saving everything from this date to the dataframe for this date
    plt.clf()
    i = 0
    for index, row in df.iterrows():
        ticker = row['Ticker']
        X = row['S_X_Y'][0]+row['I_X_Y'][0]+row['T_X_Y'][0]
        Y = 100-row['S_X_Y'][1]-row['I_X_Y'][1]-row['T_X_Y'][1]-row['T_Height']-2
        Width = row['T_Width']
        Height = row['T_Height']
        Market_Cap = row['Market_Cap']
        Pct_Change = row['Pct_Change']
        R = row['R']
        G = row['G']
        B = row['B']
        Sector = row['Sector']
        Industry = row['Industry']
        df_date.loc[i] = [ticker, X, Y, Width, Height, Market_Cap, Pct_Change, R, G, B, Sector, Industry]
        i = i + 1

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

    df_date.to_csv('{}.csv'.format(date))
    plt.clf()

    del df

def dynamic_font(text, width, height, scale):
    dynamic = 0
    if width < 2 or height < 1:
        dynamic = 0
    elif height == 1.9:
        dynamic = 8
    elif len(text) == 2:
        if width < 4 and height < 4:
            dynamic = 8
        elif width > 10 and height > 7:
            dynamic = 15
        else:
            dynamic = 10
    elif len(text) == 3:
        if width < 4 and height < 4:
            dynamic = 8
        elif width > 10 and height > 7:
            dynamic = 15
        else:
            dynamic = 10
    elif len(text) == 4:
        if width < 4 and height < 4:
            dynamic = 8
        elif width > 10 and height > 7:
            dynamic = 15
        else:
            dynamic = 8
    elif len(text) >= 5:
        if width < 4 and height < 4:
            dynamic = 6
        elif width > 10 and height > 7:
            dynamic = 15
        else:
            dynamic = 10
    elif len(text) == 1:
        if width < 4 and height < 4:
            dynamic = 8
        elif width > 10 and height > 7:
            dynamic = 15
        else:
            dynamic = 10
    return dynamic / scale
    






def date_get():
    dateList = []
    for date in df_Nas.index:
        if date >= START and date < END:
            dateList.append(date)
    return dateList


def animate(i):
    if i >= len(dateList):
        sleep(300)
        sys.exit()
    date = dateList[i]
    print(date)
    df = pd.read_csv('{}.csv'.format(date))

    #Diaginoally scaling
    scale_x = (Max_Scale_W)/(np.sqrt((df_Nas.loc[date].Close/Max_Close)*np.sin(angle_B)*1/np.sin(angle_A)))
    scale_y = (Max_Scale_H)/(np.sqrt((df_Nas.loc[date].Close/Max_Close)*np.sin(angle_A)*1/np.sin(angle_B)))

    ax1.cla()
    for index, row in df.iterrows():
        ax1.add_patch(Rectangle((row['X'], row['Y']), row['Width'], row['Height'],facecolor=(row['R'], row['G'], row['B']),  edgecolor = "black", linewidth = 0.5)) #facecolor=(row['R'], row['G'], row['B'])
        ax1.text(row['X']+(row['Width']/2), row['Y']+(row['Height']/2), row['Ticker'], verticalalignment = 'center', horizontalalignment = 'center', fontsize = dynamic_font(row['Ticker'], row['Width'], row['Height'], scale_x))
    ax1.text(100, 100, '{}'.format(round(df_Nas.loc[date].Close, 2)), verticalalignment = 'bottom', horizontalalignment = 'left', fontsize = 10)
    ax1.text(100, 100, '{}'.format(str(date).replace(' 00:00:00', '')), verticalalignment = 'top', horizontalalignment = 'left', fontsize = 10)
    ax1.set_xlim([0, 100 * scale_x])
    ax1.set_ylim([0, 100 * scale_y])
    ax1.axis('off')

    #adding the legend and titles
    
    #Animating the Nasdaq Index overtop
    ax2_y_vals.append(df_Nas.loc[date].Close)
    ax2_x_vals.append(date)
    ax2.cla()
    ax2.plot(ax2_x_vals, ax2_y_vals)
    plt.gca().set_title('Nasdaq-100 Index Over Time', fontsize=8)

    # if os.path.exists('{}.png'.format(date)) == False:
    #     plt.savefig('{}.png'.format(date), dpi=625)
    #     print(date, 'saved')

    



path = os.getcwd()
#getting date range
os.chdir('{}/df_per_date'.format(path))

#df_Nas = web.DataReader('^IXIC', 'yahoo', START, END)
########################################################fixing yahoo error
query_string = f'https://query1.finance.yahoo.com/v7/finance/download/^IXIC?period1={dt_convert(START)}&period2={dt_convert(END)}&interval=1d&events=history&includeAdjustedClose=true'
df_Nas = pd.read_csv(query_string)
df_Nas.set_index('Date', inplace=True)
df_Nas['LTD'] = df_Nas.index
df_Nas['LTD'] = df_Nas.LTD.shift(1)
df_Nas['LTD'] = pd.to_datetime(df_Nas.LTD)
df_Nas.index = pd.to_datetime(df_Nas.index)

for row in df_Nas.iterrows():
    date = row[0]
    if os.path.exists('{}.csv'.format(date)) == False:
        SectorMarketCapDictionary = {}
        print('Webscraping for a the new date', date)
        webscrape(date)

    

#Calculations to scale the diagram accordingly 
Max_Close = df_Nas['Close'].max()
#theta and gamma
angle_B = np.arccos(162/(18*np.sqrt(337)))
angle_A = np.arccos(512/(32*np.sqrt(337)))
#max scale to compare to max height/width
Max_Scale_H = np.sqrt((1)*np.sin(angle_A)*1/np.sin(angle_B))
Max_Scale_W = np.sqrt((1)*np.sin(angle_B)*1/np.sin(angle_A))

dateList = date_get()

fig = plt.figure(figsize=(16,9))
ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)
ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1)

ax2_x_vals = []
ax2_y_vals = []


ani = FuncAnimation(fig, animate, interval=10)
plt.show()

print('Done')