import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
'''
Finding Hazard Rates
---------------------------------------
Using flight data from Team Flight:
https://github.com/EpiCoronaHack/Hackathon2020z

Time Series data from Johns Hopkins CSSE:
https://github.com/CSSEGISandData/COVID-19

Census data: Madi sources?

Border data: US bureau of transportation and statistics (1996--2019)

TO DO: flights should be W-W not M-M (but prob doesn't matter)   

'''
#--------SETUP---------------------------------------------------------#
# Air traffic: countries considered (SK seems most significant)
airCountries=['Japan', 'South Korea', 'Germany', 'Taiwan', 'France', 'India', 'UK', 'Hong Kong']

# Air traffic: regions considered (province, city etc.) 
airChina_names=['Beijing', 'Shanghai', 'Guangdong', 'Henan', 'Jiangsu', 'Liaoning', 'Shandong', 'Fujian']

airChina_IDs=['PEK', 'PVG', 'CAN','SZX', 'CGO', 'NKG', 'SHE', 'TAO', 'XMN']
airChina_key={'PEK':'Beijing', 'PVG':'Shanghai','CAN':'Guangdong','SZX':'Guangdong', 'CGO':'Henan',  'NKG':'Jiangsu', 'SHE':'Liaoning', 'TAO':'Shandong', 'XMN':'Fujian'}


# Num days since Jan 22 (LAST DATA: Mar 8th)
numDays=46


# Flight Data 
flight_df=pd.read_csv('flight-schedules_affected-countries_to_vancouver.csv')

# Convert true/false to 1/0 for flight schedule
flight_df[['day1','day2','day3','day4', 'day5', 'day6', 'day7']] = flight_df[['day1','day2','day3','day4', 'day5', 'day6', 'day7']].astype(int)

# Case Count Data...
confirmed_df=pd.read_csv('time_series_19-covid-Confirmed.csv')
recovered_df=pd.read_csv('time_series_19-covid-Recovered.csv')
deaths_df=pd.read_csv('time_series_19-covid-Deaths.csv')

# Prevalence Data
population_df=pd.read_csv('population_data.csv')

# WA Data
WA_outbreaks=['Snohomish County, WA', 'King County, WA', 'Unassigned Location, WA'] #DAILY AVERAGE FOR EACH MONTH (averaged over data from past 5 yrs)
WA_population=7535591.0
WA_border_traffic=np.loadtxt('WA_border_averages.txt')


# BC imported cases *** UPDATED AS OF MAR 8th (better sources?)
imported={'Japan':{'Cases': 0, 'Hazard': 0}, 'South Korea':{'Cases': 0, 'Hazard':0}, 'Germany':{'Cases': 0, 'Hazard':0}, 'Taiwan':{'Cases': 0, 'Hazard':0}, 'France':{'Cases': 0, 'Hazard':0}, 'India':{'Cases': 0, 'Hazard':0}, 'UK':{'Cases': 0, 'Hazard':0}, 'Hong Kong': {'Cases': 0, 'Hazard':0}, 'Mainland China':{'Cases':3, 'Hazard':0}, 'Iran':{'Cases': 5, 'Hazard':0}, 'Hong Kong':{'Cases':1, 'Hazard':0}, 'WA':{'Cases': 0, 'Hazard':0}}

#-----------------------------------------------------------------------#
# HAZARD FROM CHINA
china_confirmed=confirmed_df[confirmed_df['Province'].isin(airChina_names)]
china_confirmed=china_confirmed.drop(['Region', 'Lat', 'Long'], axis=1)
china_recovered=recovered_df[recovered_df['Province'].isin(airChina_names)]
china_recovered=china_recovered.drop(['Region', 'Lat', 'Long'], axis=1)
china_deaths=deaths_df[deaths_df['Province'].isin(airChina_names)]
china_deaths=china_deaths.drop(['Region', 'Lat', 'Long'], axis=1)

# Compute risk
china_risk=[]
for airport in airChina_IDs:
    tmp_df=flight_df[flight_df.departureID==airport]
    schedule=tmp_df[['day1','day2','day3','day4', 'day5', 'day6', 'day7']].to_numpy()
    seats=tmp_df[['totalSeats']].to_numpy()
    volume=np.tile(np.sum(schedule*seats, axis=0),7)[0:numDays]
    region=airChina_key[airport]
    cases=china_confirmed[china_confirmed.Province==region].to_numpy()[0][1:-1]-china_recovered[china_recovered.Province==region].to_numpy()[0][1:-1]-china_deaths[china_deaths.Province==region].to_numpy()[0][1:-1]
    pop=population_df[population_df.Province==region][['Population']].to_numpy()[0][0]
    china_risk.append(np.divide(cases*volume, 10000*pop))
china_risk=sum(china_risk)
plt.scatter(np.arange(0,numDays,1), china_risk, s=10,c ="#FFDB6D", edgecolor = "#C4961A")

# update cumulative hazard 
imported['Mainland China']['Hazard'] = sum(china_risk) #sum over time
#-------------------------------------------------------------------------#
# HAZARD FROM OTHER INTL COUNTRIES
other_confirmed=confirmed_df[confirmed_df['Region'].isin(airCountries)]
other_confirmed=other_confirmed.drop(['Province', 'Lat', 'Long'], axis=1)
other_recovered=recovered_df[recovered_df['Region'].isin(airCountries)]
other_recovered=other_recovered.drop(['Province', 'Lat', 'Long'], axis=1)
other_deaths=deaths_df[deaths_df['Region'].isin(airCountries)]
other_deaths=other_deaths.drop(['Province', 'Lat', 'Long'], axis=1)
other_risk=[]
for country in airCountries:
    tmp_df=flight_df[flight_df.departureCountry==country]
    schedule=tmp_df[['day1','day2','day3','day4', 'day5', 'day6', 'day7']].to_numpy()
    seats=tmp_df[['totalSeats']].to_numpy()
    volume=np.tile(np.sum(schedule*seats, axis=0),7)[0:numDays]
    cases=other_confirmed[other_confirmed.Region==country].to_numpy()[0][1:-1]-other_recovered[other_recovered.Region==country].to_numpy()[0][1:-1]-other_deaths[other_deaths.Region==country].to_numpy()[0][1:-1]
    pop=population_df[population_df.Country==country][['Population']].to_numpy()[0][0]
    hazard=np.divide(cases*volume, 10000*pop)
    other_risk.append(hazard)
    imported[country]['Hazard']=sum(hazard)

other_risk=sum(other_risk)
plt.scatter(np.arange(0,numDays,1), other_risk, s=10, edgecolor="#52854C", c="#C3D7A4")

#-------------------------------------------------------------------------#
# HAZARD FROM WA border traffic
border_confirmed=confirmed_df[confirmed_df['Province'].isin(WA_outbreaks)]
border_confirmed=border_confirmed.drop(['Region', 'Lat', 'Long'], axis=1)
border_recovered=recovered_df[recovered_df['Province'].isin(WA_outbreaks)]
border_recovered=border_recovered.drop(['Region', 'Lat', 'Long'], axis=1)
border_deaths=deaths_df[deaths_df['Province'].isin(WA_outbreaks)]
border_deaths=border_deaths.drop(['Region', 'Lat', 'Long'], axis=1)
border_risk=[]
for county in WA_outbreaks:
    volume=np.concatenate((np.repeat(WA_border_traffic[0],10),np.repeat(WA_border_traffic[1],29), np.repeat(WA_border_traffic[2],8))) #manually fix
    cases=border_confirmed[border_confirmed.Province==county].to_numpy()[0][1:]-border_recovered[border_recovered.Province==county].to_numpy()[0][1:]-border_deaths[border_deaths.Province==county].to_numpy()[0][1:]
    border_risk.append(np.divide(cases*volume, WA_population))
border_risk=sum(border_risk)
plt.scatter(np.arange(0,numDays+1,1), border_risk, s=10, edgecolor="#00008B", c="#708090")
# update cumulative hazard 
imported['WA']['Hazard'] = sum(border_risk) #sum over time

# Combined Hazard...
total_risk=border_risk[:-1]+other_risk+china_risk
plt.scatter(np.arange(0,numDays,1), total_risk, s=10, edgecolor="#ff5050", c="#ffb3b3")


#------------------------------------------------------------------------------#
plt.legend(['China', 'International', 'WA Border', 'Total'])
plt.ylabel('Daily Hazard Rate')
plt.xticks([0,numDays],['Jan 22', 'Mar 8'])
plt.savefig('hazard.eps')

#---------------------------------------------------------------------------#
# CUMULATIVE HAZARDS 
plt.clf()

for region in imported.keys():
   x = imported[region]['Hazard']
   y = imported[region]['Cases']
   plt.scatter(x,y)
   plt.annotate(region, (x,y),  textcoords="offset points", xytext=(0,5), ha='center', fontsize=9)

plt.xlabel('Cumulative Hazard (Jan22-Mar8)')
plt.ylabel('Imported Cases')
plt.savefig('cumulative_hazard.eps')

