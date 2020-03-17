import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdb
'''
Finding Hazard Rates
---------------------------------------
Using flight data from Team Flight:
https://github.com/EpiCoronaHack/Hackathon2020z

Time Series data from Johns Hopkins CSSE:
https://github.com/CSSEGISandData/COVID-19

Using forecast from quickforecasts.csv (CC)

BC case data: BCCDC

Border data: US bureau of transportation and statistics (1996--2019)

TO DO: flights should be W-W not M-M (but prob doesn't matter), add EU..?

'''
#--------SETUP---------------------------------------------------------#
# Look at: China, Iran, SK , WA on their own, then others lumped together

# "Other" Countries 
otherCountries=['Japan', 'Germany', 'France', 'India', 'UK', 'South Korea', 'Taiwan']

# China air traffic
airChina_names=['Beijing', 'Shanghai', 'Guangdong', 'Henan', 'Jiangsu', 'Liaoning', 'Shandong', 'Fujian']
airChina_IDs=['PEK', 'PVG', 'CAN','SZX', 'CGO', 'NKG', 'SHE', 'TAO', 'XMN']
airChina_key={'PEK':'Beijing', 'PVG':'Shanghai','CAN':'Guangdong','SZX':'Guangdong', 'CGO':'Henan',  'NKG':'Jiangsu', 'SHE':'Liaoning', 'TAO':'Shandong', 'XMN':'Fujian'}


# Flight Data 
flight_df=pd.read_csv('data/flight-schedules_affected-countries_to_vancouver.csv')

# Convert true/false to 1/0 for flight schedule
flight_df[['day1','day2','day3','day4', 'day5', 'day6', 'day7']] = flight_df[['day1','day2','day3','day4', 'day5', 'day6', 'day7']].astype(int)


# Use Forecasted data (Jan 28--Mar 16)
forecasts_df=pd.read_csv("quickforecasts.csv")
hazards_df=forecasts_df
# Num days in forecast
numDays=len(forecasts_df.index)
numDaysData=10 #data used

# Prevalence Data
population_df=pd.read_csv('data/population_data.csv')

# WA Data
#WA_outbreaks=['Snohomish County, WA', 'King County, WA', 'Unassigned Location, WA'] #DAILY AVERAGE FOR EACH MONTH (averaged over data from past 5 yrs)
WA_border_traffic=np.loadtxt('data/WA_border_averages.txt') 

# Iran estimates??????? daily volume
est_iran_volume=71
# Iran fudge number?
alpha=12

# BC imported cases *** UPDATED AS OF MAR 8th 
imported={'Japan':{'Cases': 0, 'Hazard': 0}, 'South Korea':{'Cases': 0, 'Hazard':0}, 'Germany':{'Cases': 0, 'Hazard':0}, 'Taiwan':{'Cases': 0, 'Hazard':0}, 'France':{'Cases': 0, 'Hazard':0}, 'India':{'Cases': 0, 'Hazard':0}, 'UK':{'Cases': 0, 'Hazard':0}, 'Hong Kong': {'Cases': 0, 'Hazard':0}, 'Mainland China':{'Cases':3, 'Hazard':0}, 'Iran':{'Cases': 8, 'Hazard':0}, 'Hong Kong':{'Cases':1, 'Hazard':0}, 'US':{'Cases': 1, 'Hazard':0}}

#-----------------------------------------------------------------------#
# HAZARD FROM CHINA
china_risk=[]
for airport in airChina_IDs:
    tmp_df=flight_df[flight_df.departureID==airport]
    schedule=tmp_df[['day1','day2','day3','day4', 'day5', 'day6', 'day7']].to_numpy()
    seats=tmp_df[['totalSeats']].to_numpy()
    volume=np.tile(np.sum(schedule*seats, axis=0),7)[0:numDays]
    region=airChina_key[airport]
    cases=forecasts_df['Mainland China'].to_numpy()
    #cases=forecasts_df[region].to_numpy()
    #pop=population_df[population_df.Province==region][['Population']].to_numpy()[0][0]
    pop=200000 
    china_risk.append(np.divide(cases*volume, pop*10000))
china_risk=sum(china_risk)
plt.scatter(np.arange(0,numDays,1), china_risk, s=10,c ="#FFDB6D", edgecolor = "#C4961A")

# update cumulative hazard 
imported['Mainland China']['Hazard'] = sum(china_risk) #sum over time
hazards_df['Mainland China'] = china_risk

#-------------------------------------------------------------------------#
# HAZARD FROM OTHER INTL COUNTRIES
other_risk=[]
for country in otherCountries:
    tmp_df=flight_df[flight_df.departureCountry==country]
    schedule=tmp_df[['day1','day2','day3','day4', 'day5', 'day6', 'day7']].to_numpy()
    seats=tmp_df[['totalSeats']].to_numpy()
    volume=np.tile(np.sum(schedule*seats, axis=0),7)[0:numDays]
    cases=forecasts_df[country].to_numpy()
    pop=population_df[population_df.Country==country][['Population']].to_numpy()[0][0]
    hazard=np.divide(cases*volume, 10000*pop)
    other_risk.append(hazard)
    imported[country]['Hazard']=sum(hazard)
    hazards_df[country] = hazard

other_risk=sum(other_risk)
plt.scatter(np.arange(0,numDays,1), other_risk, s=10, edgecolor="#52854C", c="#C3D7A4")

#-------------------------------------------------------------------------#
# HAZARD FROM US FLIGHTS FROM CA AND BORDER/FLIGHTS FROM WA
border_travel=0.5 #try reducing border traffic 
flight_travel=0.5 #try reducing flight traffic
US_risk=[]
# first calc total volume out of WA/CA
US_flights= flight_df[(flight_df['departureStateID'] == 'CA') | (flight_df['departureStateID'] == 'WA')]
schedule=US_flights[['day1','day2','day3','day4', 'day5', 'day6', 'day7']].to_numpy()
seats=US_flights[['totalSeats']].to_numpy() 
volume=np.tile(np.sum(schedule*seats, axis=0),7)[0:numDays]
volume=flight_travel*volume + border_travel*WA_border_traffic[2] #just using Mar border data
cases=forecasts_df['US'].to_numpy()
US_prev=np.divide(cases, 10000*population_df[population_df.Country=='USA'][['Population']].to_numpy()[0][0])
US_risk.append(US_prev*volume)
US_risk=sum(US_risk)

plt.scatter(np.arange(0,numDays,1), US_risk, s=10, edgecolor="#00008B", c="#708090")
# update cumulative hazard 
imported['US']['Hazard'] = sum(US_risk) #sum over time
# OUTPUT
hazards_df['US'] = US_risk

#-------------------------------------------------------------------------#
# HAZARD FROM IRAN
# No travel restrictions
#volume=np.repeat(est_iran_volume,numDays)
# With travel restrictions (after ~Mar 8th) assume travel decreases significantly
volume=np.concatenate((np.repeat(est_iran_volume,numDaysData-2), np.repeat(0.01*est_iran_volume,numDays-numDaysData+2)))
cases=forecasts_df['Iran'].to_numpy() 
#pop=population_df[population_df.Country=='Iran'][['Population']].to_numpy()[0][0]
pop=10000000
iran_risk = np.divide(alpha*cases*volume, pop)

# update cumulative hazard 
imported['Iran']['Hazard'] = sum(iran_risk) #sum over time
# OUTPUT
hazards_df['Iran'] = iran_risk
plt.scatter(np.arange(0,numDays,1), iran_risk, s=10, edgecolor="#ff5050", c="#ffb3b3")

#-------------------------------------------------------------------------#
# HAZARD FROM SK
tmp_df=flight_df[flight_df.departureCountry=='South Korea']
schedule=tmp_df[['day1','day2','day3','day4', 'day5', 'day6', 'day7']].to_numpy()
seats=tmp_df[['totalSeats']].to_numpy()
volume=np.tile(np.sum(schedule*seats, axis=0),7)[0:numDays]
cases=forecasts_df['South Korea'].to_numpy()
pop=population_df[population_df.Country=='South Korea'][['Population']].to_numpy()[0][0]
sk_risk = np.divide(cases*volume, pop*10000)

plt.scatter(np.arange(0,numDays,1),sk_risk, s=10, edgecolor="#cc0000", c="#ffb3b3")
# update cumulative hazard 
imported['South Korea']['Hazard'] = sum(sk_risk) #sum over time
# OUTPUT
hazards_df['South Korea'] = sk_risk


# clean up and save
hazards_df=hazards_df.drop(columns=airChina_names)
hazards_df['Total Risk'] = sk_risk+other_risk+china_risk+US_risk+iran_risk
hazards_df.to_csv('output/hazards.csv')
#------------------------------------------------------------------------------#
plt.legend(['China', 'Other', 'US', 'Iran', 'South Korea'])
plt.ylabel('Daily Hazard Rate')
plt.xticks(np.arange(0, numDays),forecasts_df['dates'])
plt.xticks(rotation=70)
plt.tight_layout()
plt.savefig('output/plots/hazard_lowUSTraffic.eps')

#---------------------------------------------------------------------------#
# CUMULATIVE HAZARDS 
#plt.clf()

#for region in imported.keys():
#   x = imported[region]['Hazard']
#   y = imported[region]['Cases']
#   plt.scatter(x,y)
#   plt.annotate(region, (x,y),  textcoords="offset points", xytext=(0,5), ha='center', fontsize=9)

#plt.xlabel('Cumulative Hazard')
#plt.ylabel('Imported Cases')
#plt.savefig('output/plots/cumulative_hazard.eps')

