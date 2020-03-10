library(ggplot2)
library(dplyr)
library(tidyr)
library(ggridges)
library(reshape2)
#------------------------------------------------------------#
# Use hazard data to estimate importations to BC (to validate?)
#------------------------------------------------------------#

# Set-up
border_risk <- scan("output/border_risk.txt")
china_risk <- scan("output/china_risk.txt")
iran_risk <- scan("output/iran_risk.txt")
other_risk <- scan("output/other_risk.txt")
sk_risk <- scan("output/sk_risk.txt")

# Fudge prevalences??
alpha_iran = 1.
alpha_china = 1.

# Combine to get total hazard per day
total_risk <- border_risk+alpha_china*china_risk+alpha_iran*iran_risk+other_risk+sk_risk
total_risk <- total_risk

# Example Trials...use to fit alphas??
N = 10000
trials <- matrix(-1, nrow=N, ncol=length(total_risk))
ii=1
for (rate in total_risk) {
    trials[,ii] = rpois(N, rate)
    ii=ii+1
}
# TOTAL UP TO MAR 8
tot_imports = rowSums(trials)
ggplot() + aes(tot_imports)+ geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports (Jan 22 -- Mar 8)")+
            labs(y= " ", x = "Total Cases")
ggsave('totalImportsDistribution.png')


