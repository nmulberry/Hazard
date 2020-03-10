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
trials <- matrix(-1, nrow=N, ncol=length(risk$Total.Risk))
ii=1
for (rate in risk$Total.Risk) {
    trials[,ii] = rpois(N, rate)
    ii=ii+1
}
validate_imports = rowSums(trials)

# Extrapolated imports 
trials <- matrix(-1, nrow=N, ncol=length(risk$Total.Risk))
ii=1
for (rate in risk$Total.Risk) {
    trials[,ii] = rpois(N, rate)
    ii=ii+1
}
extrapolate_imports = rowSums(trials)

# VALIDATION
ggplot() + aes(validate_imports)+ geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports")+
            labs(y= " ", x = "Total Cases")
ggsave('ValidateImports.png')


# EXTRAPOLATION
ggplot() + aes(extrapolate_imports)+ geom_histogram(aes(y=..density..), binwidth=1, colour="black", fill="gray") + 
            theme_minimal()+
            ggtitle("Distribution of Imports")+
            labs(y= " ", x = "Total Cases")
ggsave('ExtrapolateImports.png')


