import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdb
'''
Finding Hazard Rates UPDATED AS OF MARCH 16
---------------------------------------
Using flight data from Team Flight:
https://github.com/EpiCoronaHack/Hackathon2020z

Time Series data from Johns Hopkins CSSE:
https://github.com/CSSEGISandData/COVID-19

Using forecast from quickforecasts.csv (CC)

BC case data: BCCDC

Border data: US bureau of transportation and statistics (1996--2019)

Travel is now restricted from non-CAN or US citizens

'''
#--------SETUP---------------------------------------------------------#

otherCountries=['Japan', 'Germany', 'France', 'India', 'UK', 'South Korea', 'Taiwan', 'Mainland China']


# Flight Data 
flight_df=pd.read_csv('data/flight-schedules_affected-countries_to_vancouver.csv')

# Convert true/false to 1/0 for flight schedule
flight_df[['day1','day2','day3','day4', 'day5', 'day6', 'day7']] = flight_df[['day1','day2','day3','day4', 'day5', 'day6', 'day7']].astype(int)


# Use Forecasted data (Jan 28--Mar 16)
forecasts_df=pd.read_csv("quickforecasts.csv")
US_forecasts_df=pd.read_csv("USforecasts.csv")
hazards_df=forecasts_df
# Num days in forecast
numDays=len(forecasts_df.index)
numDaysData=7 #data used

# Prevalence Data
population_df=pd.read_csv('data/population_data.csv')

# WA Data
#WA_outbreaks=['Snohomish County, WA', 'King County, WA', 'Unassigned Location, WA'] #DAILY AVERAGE FOR EACH MONTH (averaged over data from past 5 yrs)
WA_border_traffic=np.loadtxt('data/WA_border_averages.txt') 

# Iran estimates?
est_iran_volume=71
# Iran fudge number?
alpha=12


# Travel reduction effectiveness
rho=1.

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
    hazards_df[country] = hazard

volume=np.repeat(est_iran_volume,numDays)
cases=forecasts_df['Iran'].to_numpy() 
pop=population_df[population_df.Country=='Iran'][['Population']].to_numpy()[0][0]
iran_risk = rho*np.divide(alpha*cases*volume, 10000*pop)
hazards_df['Iran'] = iran_risk

other_risk=rho*sum(other_risk)+rho*iran_risk
plt.scatter(np.arange(0,numDays,1), other_risk, s=10, edgecolor="#52854C", c="#C3D7A4")

#-------------------------------------------------------------------------#
# HAZARD FROM US
#-------------------------------------------------------------------------#
# WASHINGTON 
border_travel=1. #try reducing border traffic 
flight_travel=1. #try reducing flight traffic
WA_risk=[]
# first calc total volume out of WA
WA_flights=flight_df[(flight_df['departureStateID'] == 'WA')]
schedule=WA_flights[['day1','day2','day3','day4', 'day5', 'day6', 'day7']].to_numpy()
seats=WA_flights[['totalSeats']].to_numpy() 
volume=np.tile(np.sum(schedule*seats, axis=0),7)[0:numDays]
volume=flight_travel*volume + border_travel*WA_border_traffic[2] #just using Mar border data
cases=US_forecasts_df['Washington'].to_numpy()
WA_prev=np.divide(cases, 7536000)
WA_risk.append(WA_prev*volume)
hazards_df['Washington'] = WA_risk[0]
plt.scatter(np.arange(0,numDays,1), WA_risk, s=10, edgecolor="#00008B", c="#708090")

# CALIFORNIA 
CA_risk=[]
# first calc total volume out of CA
CA_flights= flight_df[(flight_df['departureStateID'] == 'CA')]
schedule=CA_flights[['day1','day2','day3','day4', 'day5', 'day6', 'day7']].to_numpy()
seats=CA_flights[['totalSeats']].to_numpy() 
volume=np.tile(np.sum(schedule*seats, axis=0),7)[0:numDays]
volume=flight_travel*volume 
cases=US_forecasts_df['California'].to_numpy()
CA_prev=np.divide(cases, 39560000)
CA_risk.append(CA_prev*volume)
hazards_df['California'] = CA_risk[0]
plt.scatter(np.arange(0,numDays,1), CA_risk, s=10, edgecolor="#cc0000", c="#ffb3b3")

# OTHER US
US_risk=[]
# first calc total volume out of US
US_flights= flight_df[(flight_df['departureCountry'] == 'United States') & (flight_df['departureStateID'] != 'WA') & (flight_df['departureStateID'] != 'CA')]
schedule=US_flights[['day1','day2','day3','day4', 'day5', 'day6', 'day7']].to_numpy()
seats=US_flights[['totalSeats']].to_numpy() 
volume=np.tile(np.sum(schedule*seats, axis=0),7)[0:numDays]
volume=flight_travel*volume 
cases=US_forecasts_df['US'].to_numpy()-US_forecasts_df['Washington'].to_numpy()-US_forecasts_df['California'].to_numpy()
US_prev=np.divide(cases, 279904000)
US_risk.append(US_prev*volume)
hazards_df['US'] = US_risk[0]

plt.scatter(np.arange(0,numDays,1), US_risk, s=10, edgecolor="#ff5050", c="#ffb3b3")
#-----------------------------------------------------------------------------#
# clean up and save
hazards_df['Total Risk'] = other_risk+WA_risk[0]+CA_risk[0]+US_risk[0]
hazards_df.to_csv('output/test_intl.csv')
#------------------------------------------------------------------------------#
plt.legend(['International', 'WA', 'CA', 'Other US'])
plt.ylabel('Daily Hazard Rate')
plt.xticks(np.arange(0, numDays),forecasts_df['dates'])
plt.xticks(rotation=70)
plt.tight_layout()
plt.savefig('output/plots/test_intl.pdf')


