library(dplyr)
library(tidyr)
library(haven)
library(ggplot2)
library(lubridate)

rm(list=ls())
setwd("~/Documents/DC-capstone")
#---------------- read in dataset---------------------------------
d1 <- read.csv("2021VAERSDATA.csv", encoding = "UTF-8")
d2 <- read.csv("2021VAERSVAX.csv", encoding = "UTF-8")
d3 <- read.csv("2021VAERSSYMPTOMS.csv", encoding = "UTF-8")

library(stringr)

df <- d2 %>% filter(VAX_TYPE=="COVID19") %>% left_join(d1, by="VAERS_ID")%>% left_join(d3, by="VAERS_ID")

# sum # of symptoms
# The data only have 5 symptoms
df$sym2 <- ifelse(is.na(df$SYMPTOM2)|
                    df$SYMPTOM2 == '',0,1)
df$sym3 <- ifelse(is.na(df$SYMPTOM3)|
                    df$SYMPTOM3 == '',0,1)
df$sym4 <- ifelse(is.na(df$SYMPTOM4)|
                    df$SYMPTOM4 == '',0,1)
df$sym5 <- ifelse(is.na(df$SYMPTOM5)|
                    df$SYMPTOM5 == '',0,1)
df$sym_sum <- rowSums(df %>% select(sym2,sym3,sym4,sym5),na.rm = T) + 1


# number of doses (only consider 1-3)
df$dose <- ifelse(df$VAX_DOSE_SERIES == 1,1,
                  ifelse(df$VAX_DOSE_SERIES == 2,2,
                         ifelse(df$VAX_DOSE_SERIES == 3,3,NA)))
# summarize # of symptoms 
df %>% filter(!is.na(dose)) %>%
  ggplot(aes(VAX_MANU,sym_sum,color = as.factor(dose))) + 
  geom_boxplot() + 
  facet_grid(SEX ~ .) + 
  xlab("Manufacturer") + 
  ylab("Number of Symptoms") + 
  labs(color = "Number of Doses")

## recode clinical-related variables
df$othermeds <- ifelse(!is.na(df$OTHER_MEDS)&
                         df$OTHER_MEDS!=""&
                         df$OTHER_MEDS!=" "&
                         df$OTHER_MEDS!="na"&
                         df$OTHER_MEDS!="Na"&
                         df$OTHER_MEDS!="NA"&
                         df$OTHER_MEDS!="N/A"&
                         df$OTHER_MEDS!="N/a"&
                         df$OTHER_MEDS!="n/a"&
                         df$OTHER_MEDS!="NONE"&
                         df$OTHER_MEDS!="None"&
                         df$OTHER_MEDS!="none"&
                         df$OTHER_MEDS!="no"&
                         df$OTHER_MEDS!="NO"&
                         df$OTHER_MEDS!="unknown"&
                         df$OTHER_MEDS!="Unknown"&
                         df$OTHER_MEDS!="UNKNOWN",1,0)

table(df$othermeds)

df$curill <- ifelse(!is.na(df$CUR_ILL)&
                        df$CUR_ILL!=""&
                        df$CUR_ILL!=" "&
                        df$CUR_ILL!="na"&
                        df$CUR_ILL!="Na"&
                        df$CUR_ILL!="NA"&
                        df$CUR_ILL!="N/A"&
                        df$CUR_ILL!="N/a"&
                        df$CUR_ILL!="n/a"&
                        df$CUR_ILL!="NONE"&
                        df$CUR_ILL!="None"&
                        df$CUR_ILL!="none"&
                        df$CUR_ILL!="no"&
                        df$CUR_ILL!="NO"&
                        df$CUR_ILL!="unknown"&
                        df$CUR_ILL!="Unknown"&
                        df$CUR_ILL!="UNKNOWN",1,0)
table(df$curill)

df$allergies <- ifelse(!is.na(df$ALLERGIES)&
                         df$ALLERGIES!=""&
                         df$ALLERGIES!=" "&
                         df$ALLERGIES!="na"&
                         df$ALLERGIES!="Na"&
                         df$ALLERGIES!="NA"&
                         df$ALLERGIES!="N/A"&
                         df$ALLERGIES!="N/a"&
                         df$ALLERGIES!="n/a"&
                         df$ALLERGIES!="NONE"&
                         df$ALLERGIES!="None"&
                         df$ALLERGIES!="none"&
                         df$ALLERGIES!="no"&
                         df$ALLERGIES!="NO"&
                         df$ALLERGIES!="unknown"&
                         df$ALLERGIES!="Unknown"&
                         df$ALLERGIES!="UNKNOWN",1,0)
table(df$allergies)

data_m <- df %>% 
  group_by(allergies,curill,othermeds) %>% 
  summarise(M = mean(sym_sum),
            sd = sd(sym_sum),
            med = median(sym_sum)) %>% mutate(curill = recode_factor(curill, '0' = "No Health Problem",
                                                             '1' = "Had Health Problem"))

# how does different clinical variables affect number of symptoms
ggplot(data_m,aes(as.factor(othermeds),M,fill=as.factor(allergies))) + 
    geom_col(position = "dodge") + 
    facet_grid(.~as.factor(curill)) +
    xlab("Yes/No having other medicines") + 
    ylab("Number of symptoms") + 
    labs(fill = "Yes/No allergy history")

# temporary change of number of symptoms (aggregated by counts)
df$onsetdate <- mdy(df$ONSET_DATE)
df$vaxdate <- mdy(df$VAX_DATE)
df$onset <- as.duration(df$onsetdate - df$vaxdate)
df$onset <- as.numeric(df$onset,"days")

# plot counts of year 2021
df %>% filter(onsetdate >= as_date("2021-01-01")) %>%
  mutate(month = month(onsetdate,label = T)) %>% 
  group_by(month,VAX_MANU) %>%
  summarise(count = n()) %>% ggplot(aes(month,count,fill = VAX_MANU)) + 
  geom_col(position = "dodge") +
  xlab("Month of 2021") + 
  ylab("Counts of reports") + 
  labs(fill = "Manufacturer")

