library(reshape2)
library(ggplot2)
library(dplyr)


## Setup

confirmed = read.csv("data/time_series_19-covid-Confirmed.csv", stringsAsFactors = F)
deaths=read.csv("data/time_series_19-covid-Deaths.csv", stringsAsFactors = F)
recov = read.csv("data/time_series_19-covid-Recovered.csv", stringsAsFactors = F)



colstr=colnames(confirmed)[5:ncol(confirmed)]
dstr=vapply(colstr, function(x) substr(x, start = 2, stop = nchar(x)), FUN.VALUE="hi")
dates=as.Date(dstr, format = "%m.%d.%y")
N=ncol(confirmed)


row=25
plot(dates,confirmed[row,5:N]-recov[row,5:N])


airChina_names=c('Beijing', 'Shanghai', 'Guangdong', 'Henan', 'Jiangsu', 'Liaoning', 'Shandong', 'Fujian')
airCountries=c('Japan', 'South Korea', 'Germany', 'Taiwan', 'France', 'India', 'UK', 'Hong Kong')
china_confirmed = confirmed[which(confirmed$Province %in% airChina_names),]
china_death = deaths[which(confirmed$Province %in% airChina_names),]
china_rec = recov[which(confirmed$Province %in% airChina_names),]


china_total_conf = colSums(china_confirmed[,5:N])
china_total_rec = colSums(china_rec[,5:N])
china_total_death=colSums(china_death[,5:N])
plot(dates,china_total_conf-china_total_rec-china_total_death)


conf = melt(confirmed, id.vars = c("Province", "Region", "Lat","Long"),
                measure.vars = colnames(confirmed)[5:N])
recsimp = melt(recov, id.vars = c("Province", "Region", "Lat","Long"),
                measure.vars = colnames(confirmed)[5:N])
deathsimp = melt(deaths, id.vars = c("Province", "Region", "Lat","Long"),
                measure.vars = colnames(confirmed)[5:N])
conf$variable=as.Date(conf$variable, format = "X%m.%d.%y")
colnames(conf)=c("Province","Region","Lat","Long","date","cases")
allsimp=conf; allsimp$prev = conf$cases-recsimp$value - deathsimp$value
allsimp$deaths = deathsimp$value
allsimp$recovered = recsimp$value

ggplot(data=filter(allsimp,Region %in% "South Korea"), aes(x=date, y=prev, colour=Region))+geom_point()

extractPrevRegion = function(thisname) {

if (thisname %in% confirmed$Region) {
    conftmp=confirmed[which(confirmed$Region %in% thisname), ] 
    rectmp=recov[which(confirmed$Region %in% thisname), ] 
    deathtmp=deaths[which(confirmed$Region %in% thisname), ] 
} 
else {if (thisname %in% confirmed$Province) {
    conftmp=confirmed[which(confirmed$Province %in% thisname), ] 
    rectmp=recov[which(confirmed$Province %in% thisname), ] 
    deathtmp=deaths[which(confirmed$Province %in% thisname), ] 
}}
if (nrow(conftmp) > 1) { 
  cases=colSums(conftmp[,5:ncol(conftmp)]) 
  recs = colSums(rectmp[,5:ncol(rectmp)]) 
  deas=colSums(deathtmp[,5:ncol(deathtmp)]) 
} else {cases=conftmp[5:ncol(conftmp)]
  recs=rectmp[5:ncol(rectmp)]
  deas=deathtmp[5:ncol(deathtmp)]
}
return(prevs=cases-recs-deas)
}

getForecast=function(prevs, nDays=10, lastDay=55,mode="poly") {
  nDays=10
  lastDay=55 

# take last 10 days of the data
x = (length(prevs)-nDays+1):length(prevs) # was 38:47, for  last nDays 
ind=x # index to pull last 10 days of prevalence
y=vector()
y[1:nDays]=prevs[ind] # cases[ind]-recs[ind]-deas[ind]
mydf=data.frame(t=x, n=unlist(y)+0.01)
xx <- seq(min(ind),lastDay,by=1)

#  and  make the fit 
if (mode == "poly") { fit2 <- lm(formula = n~poly(t,2), data=mydf) 
fitline=predict(object=fit2, newdata =data.frame(t= xx))}

if (mode == "exp"){ fit2 <- lm(formula = log(n) ~ t, data=mydf)
fitline=exp(predict(object=fit2, newdata =data.frame(t= xx)))}

myfore=data.frame(t=xx,n=pmax(fitline,0*fitline))

return(list(thedata =mydf, myfore=myfore))
}


# return forecast with date, forecasted prevalence

# a few tests 
thisname="Mainland China"
thisname="US"
prevs = extractPrevRegion(thisname)

myfore=getForecast(prevs,mode="exp")

ggplot(data=myfore$thedata,aes(x=t,y=n))+geom_point() +
  geom_line(data=myfore$myfore, aes(x=t,y=n))

allnames = c(airChina_names, airCountries, "Mainland China", "US")
allfores = lapply( allnames,
        function(thisone) {prevs=extractPrevRegion(thisone)
        return(getForecast(prevs,mode="exp"))})

plotlist=list()
for (k in 1:length(allnames)) {
plotlist[[k]] = ggplot(data=allfores[[k]]$thedata,aes(x=t,y=n))+geom_point() +
  geom_line(data=allfores[[k]]$myfore, aes(x=t,y=n))+ggtitle(allnames[k])}

plot_grid(plotlist=plotlist, ncol = 3)
ggsave(file="quickforecasts.pdf", width=8,height=11)

forecastdf = data.frame(days=allfores[[1]]$myfore$t,
        dates=seq.Date(from=dates[min(allfores[[1]]$myfore$t)],
                       by=1, length.out=length(allfores[[1]]$myfore$t)))
for (k in 1:length(allnames)) {
  forecastdf[,k+2]=allfores[[k]]$myfore$n
}
colnames(forecastdf)[3:ncol(forecastdf)] = allnames
write.csv(forecastdf, file = "quickforecasts.csv")





















