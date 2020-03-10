library(ggplot2)
library(dplyr)
library(tidyr)
library(ggridges)
library(reshape2)
#------------------------------------------------------------#
# Use hazard data to estimate importations to BC
#------------------------------------------------------------#

# Set-up
today  = '2020-03-08' # last data used
risk <- read.csv('output/hazards.csv')
index = match(today, risk$dates)
risk_data <- risk[c(1:index),]
risk_extrap <-risk[-c(1:index),]

#-----Example Trials...First to validate--------#
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
#--------------------------------------------------#
# Extrapolated imports 
trials <- matrix(-1, nrow=N, ncol=length(risk_extrap$Total.Risk))
ii=1
for (rate in risk_extrap$Total.Risk) {
    trials[,ii] = rpois(N, rate)
    ii=ii+1
}
extrapolate_imports = rowSums(trials)

# VALIDATION
ggplot() + aes(validate_imports)+ geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports")+
            labs(y= " ", x = "Cases")
ggsave('ValidateImports.png')
ggplot() + aes(china_validate_imports)+ geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports")+
            labs(y= " ", x = "Cases")
ggsave('ChinaValidateImports.png')
ggplot() + aes(iran_validate_imports)+ geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports")+
            labs(y= " ", x = "Total Cases")
ggsave('IranValidateImports.png')
ggplot() + aes(US_validate_imports)+ geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports")+
            labs(y= " ", x = "Cases")
ggsave('USValidateImports.png')


# EXTRAPOLATION
ggplot() + aes(extrapolate_imports)+ geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports")+
            labs(y= " ", x = "Cases")
ggsave('ExtrapolateImports.png')


