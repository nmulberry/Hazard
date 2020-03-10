library(ggplot2)
library(dplyr)
library(tidyr)
library(ggridges)
library(reshape2)
#------------------------------------------------------------#
# Use hazard data to estimate importations to BC
# uses: output/hazards.csv
#       this is output from hazard_rates.py
#------------------------------------------------------------#

startDate='2020-02-28'# first data used
today='2020-03-08' # last data used

# Actual data from BC
BC_imports <- read.csv('data/BC_cases.csv')
BC_imports <- BC_imports[c(10:22),] # **
# read output and sort into data vs extrapolated
risk <- read.csv('output/hazards.csv')
index = match(today, risk$dates)
risk_data <- risk[c(1:index),]
risk_extrap <-risk[-c(1:index),]

#-----Validation Trials--------#
N = 1000
trials <- matrix(-1, nrow=N, ncol=length(risk_data$Total.Risk))
ii=1
for (rate in risk_data$Total.Risk) {
    trials[,ii] = rpois(N, rate)
    ii=ii+1
}
validate_imports = rowSums(trials)
# China
trials <- matrix(-1, nrow=N, ncol=length(risk_data$Mainland.China))
ii=1
for (rate in risk_data$Mainland.China) {
    trials[,ii] = rpois(N, rate)
    ii=ii+1
}
china_validate_imports = rowSums(trials)

# Iran
trials <- matrix(-1, nrow=N, ncol=length(risk_data$Iran))
ii=1
for (rate in risk_data$Iran) {
    trials[,ii] = rpois(N, rate)
    ii=ii+1
}
iran_validate_imports = rowSums(trials)

# US
trials <- matrix(-1, nrow=N, ncol=length(risk_data$US))
ii=1
for (rate in risk_data$US) {
    trials[,ii] = rpois(N, rate)
    ii=ii+1
}
US_validate_imports = rowSums(trials)

#--------------------------------------------------#
# Extrapolated imports 
#--------------------------------------------------#

trials <- matrix(-1, nrow=N, ncol=length(risk_extrap$Total.Risk))
ii=1
for (rate in risk_extrap$Total.Risk) {
    trials[,ii] = rpois(N, rate)
    ii=ii+1
}
extrapolate_imports = rowSums(trials)

#--------------------------------------------------#
#       PLOTS
#--------------------------------------------------#

# Plot trial outcomes and compare to data
# TOTAL
total_imports=length(BC_imports[BC_imports[,"Contact"] != 'Local',]$Case.Number)
ggplot() + aes(validate_imports)+ annotate("point", x = total_imports, y = -0.001, color="red")+
            geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports")+
            labs(y= " ", x = "Cases")
ggsave('output/plots/ValidateImports.png')


#CHINA
china_imports=length(BC_imports[BC_imports[,"Contact"] == 'Mainland China',]$Case.Number)
ggplot() + aes(china_validate_imports)+ annotate("point", x = china_imports, y = -0.001, color="red")+
            geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports")+
            labs(y= " ", x = "Cases")
ggsave('output/plots/ChinaValidateImports.png')

# IRAN
iran_imports=length(BC_imports[BC_imports[,"Contact"] == 'Iran',]$Case.Number)
ggplot() + aes(iran_validate_imports)+ annotate("point", x = iran_imports, y = -0.001, color="red")+
            geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports")+
            labs(y= " ", x = "Total Cases")
ggsave('output/plots/IranValidateImports.png')

# US
US_imports=length(BC_imports[BC_imports[,"Contact"] == 'US',]$Case.Number)
ggplot() + aes(US_validate_imports)+annotate("point", x = US_imports, y = -0.001, color="red")+
            geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports")+
            labs(y= " ", x = "Cases")
ggsave('output/plots/USValidateImports.png')


# EXTRAPOLATION
ggplot() + aes(extrapolate_imports)+ geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports")+
            labs(y= " ", x = "Cases")
ggsave('output/plots/ExtrapolateImports.png')


