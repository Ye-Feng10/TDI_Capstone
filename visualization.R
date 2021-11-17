library(zoo)
library(readr)
library(tidyverse)
library(echarts4r)
library(echarts4r.maps)

df_vis <- read_csv("df_vis.csv")
df_vis <- df_vis[,-1]
us <- read.csv("us_state_vaccinations.csv")
sym <- read.csv("long_symptoms.csv")
feature_imp <- read.csv("feature_imp.csv")

# count by date
df_vis$date.vax <- as.Date(df_vis$VAX_DATE, format="%m/%d/%Y")
count <- df_vis %>% group_by(date.vax) %>% summarise(n = n())  %>% distinct()

us$date.vax <- as.Date(us$date,format="%Y-%m-%d")

df_temp <- na.locf(na.locf(us), fromLast = TRUE)

df <- df_temp %>% group_by(date.vax) %>%
  summarise(total = sum(total_vaccinations,na.rm = T), daily = sum(daily_vaccinations_raw,na.rm = T)) %>%
  left_join(count, by = "date.vax")

df <- na.omit(df)
df$rate <-df$n/df$daily


## Plot 1
# visualize daily rate of adverse event
df_l <- gather(df, Number, Value, total:rate, factor_key=TRUE)

df_l[df_l$Number == "total" & df_l$date.vax == "2021/9/28",]$Value <- df_l[df_l$Number == "total" & df_l$date.vax == "2021/9/27",]$Value + df_l[df_l$Number == "daily" & df_l$date.vax == "2021/9/28",]$Value
df_l[df_l$Number == "total" & df_l$date.vax == "2021/10/27",]$Value <- df_l[df_l$Number == "total" & df_l$date.vax == "2021/10/26",]$Value + df_l[df_l$Number == "daily" & df_l$date.vax == "2021/10/27",]$Value
df_l[df_l$Number == "total" & df_l$date.vax == "2021/10/28",]$Value <- df_l[df_l$Number == "total" & df_l$date.vax == "2021/10/27",]$Value + df_l[df_l$Number == "daily" & df_l$date.vax == "2021/10/28",]$Value

p1 <- df_l |> filter(date.vax >= as.Date("2021/01/01")) |>
  filter(Value != 0) |>
  filter(!is.infinite(Value)) |>
  group_by(Number) |> 
  e_charts(date.vax, timeline = TRUE) |> 
  e_line(Value, legend = FALSE) |> 
  e_tooltip(trigger = "axis") |> 
  e_timeline_opts(
    axis_type = "category",
    playInterval = 1500,
    top = 5,
    right = 50,
    left = 200
  ) |> 
  e_datazoom() |> 
  e_timeline_serie(
    title = list(
      list(text = "Total Vaccination"),
      list(text = "Daily Vaccination"),
      list(text = "Total Adverse event report"),
      list(text = "Adverse Event Rate")
    )
  ) 

# plot 2: visualize by manufacturer
df2 <- df_vis %>% group_by(date.vax,VAX_MANU) %>% summarise(n = n())  %>% distinct()
p2 <- df2 |> filter(date.vax >= as.Date("2021/01/01")) |>
  group_by(VAX_MANU) |> 
  filter(VAX_MANU != "UNKNOWN MANUFACTURER") |>
  e_charts(date.vax) |> 
  e_line(n, legend = FALSE) |> 
  e_tooltip(trigger = "axis") |> 
  e_datazoom() |> 
  e_title("Adverse Events report by Manufacturer")

# plot 3: visualize by US.State
# last day is
df3 <- df_vis %>% group_by(STATE) %>% summarise(n = n())  %>% distinct() %>% mutate(location = state.name[match(STATE, state.abb)])
df3 <- df3 %>% left_join(us %>% filter(date.vax == "2021-10-28"),by = "location")
df3 <- na.omit(df3)
df3$rate <- df3$n/df3$people_vaccinated
json <- jsonlite::read_json("https://raw.githubusercontent.com/shawnbot/topogram/master/data/us-states.geojson")

.scl <- function(x){
  (x - min(x)) / (max(x) - min(x))
}

p3 <- df3 |> 
  mutate(
    AE = .scl(n),
    Total = .scl(total_vaccinations),
    Rate = .scl(rate)
  ) |> 
  select(location, AE, Total, Rate) |> 
  group_by(location) |> 
  tidyr::gather("Key",  "Value", AE, Total, Rate) |> 
  group_by(Key) |> 
  e_charts(location, timeline = TRUE) |> 
  e_map_register("USA", json) |> 
  e_map(Value, map = "USA") |> 
  e_visual_map(min = 0, max = 1) |> 
  e_timeline_serie(
    title = list(
      list(text = "AE", subtext = "Total Number of reported AE"),
      list(text = "Rate", subtext = "Adverse event rate"),
      list(text = "Total", subtext = "Total people vaccinated")
    )
  )

# symptoms
cnt <- sym |> 
  group_by(DIED,SYMPTOM) |>
  summarise(n=n()) |>
  group_by(DIED) |>
  top_n(20)

cnt |> filter(DIED == 1) %>%
  filter(SYMPTOM != "Death") %>%
  arrange(n)%>%
  e_charts(x = SYMPTOM, elementId = "Died") %>%
  e_bar(n, legend = TRUE, name = "Died") %>% 
  e_labels(position = "right") %>% 
  e_tooltip(
    trigger = "item",
    axisPointer = list(
      type = "line"
    )
  )  %>% 
  e_title("Died") %>% 
  e_flip_coords() %>% 
  e_y_axis(splitLine = list(show = FALSE), axisLabel = list(
    interval = 0L
  )) %>% 
  e_x_axis(show = FALSE) %>% 
  e_toolbox_feature(
    feature = "saveAsImage",
    title = "Save as image"
  ) -> echrtDied

cnt |> filter(DIED == 0) %>%
  arrange(n)%>%
  e_charts(x = SYMPTOM) %>%
  e_bar(n, legend = TRUE, name = "Not Died") %>% 
  e_labels(position = "right") %>% 
  e_tooltip(
    trigger = "item",
    axisPointer = list(
      type = "line"
    )
  ) %>% 
  e_title("Not Died") %>% 
  e_flip_coords() %>% 
  e_y_axis(splitLine = list(show = FALSE), axisLabel = list(
    interval = 0L
  )) %>% 
  e_x_axis(show = FALSE) %>% 
  e_connect("Died") %>%
  e_toolbox_feature(
    feature = "saveAsImage",
    title = "Save as image"
  ) -> echrtND

cnt2 <- sym |> 
  group_by(HOSPITAL,SYMPTOM) |>
  summarise(n=n()) |>
  group_by(HOSPITAL) |>
  top_n(20)

cnt2 |> filter(HOSPITAL == 1) %>%
  filter(SYMPTOM != "Death") %>%
  arrange(n)%>%
  e_charts(x = SYMPTOM, elementId = "Hospitalized") %>%
  e_bar(n, legend = TRUE, name = "Hospitalized") %>% 
  e_labels(position = "right") %>% 
  e_tooltip(
    trigger = "item",
    axisPointer = list(
      type = "line"
    )
  )  %>% 
  e_title("Hospitalized") %>% 
  e_flip_coords() %>% 
  e_y_axis(splitLine = list(show = FALSE), axisLabel = list(
    interval = 0L
  )) %>% 
  e_x_axis(show = FALSE) %>% 
  e_toolbox_feature(
    feature = "saveAsImage1",
    title = "Save as image"
  ) -> echrtHos

cnt2 |> filter(HOSPITAL == 0) %>%
  arrange(n)%>%
  e_charts(x = SYMPTOM) %>%
  e_bar(n, legend = TRUE, name = "Not Hospitalized") %>% 
  e_labels(position = "right") %>% 
  e_tooltip(
    trigger = "item",
    axisPointer = list(
      type = "line"
    )
  ) %>% 
  e_title("Not Hospitalized") %>% 
  e_flip_coords() %>% 
  e_y_axis(splitLine = list(show = FALSE), axisLabel = list(
    interval = 0L
  )) %>% 
  e_x_axis(show = FALSE) %>% 
  e_connect("Hospitalized") %>%
  e_toolbox_feature(
    feature = "saveAsImage1",
    title = "Save as image"
  ) -> echrtNHos

p_fi <- feature_imp |> arrange(X0) |>
  e_charts(x = index) %>%
  e_bar(X0, legend = TRUE, name = "Importance") %>% 
  e_labels(position = "right") %>% 
  e_tooltip(
    trigger = "item",
    axisPointer = list(
      type = "line"
    )
  ) %>% 
  e_title("Feature Importance in Random Forest") %>% 
  e_flip_coords() %>% 
  e_y_axis(splitLine = list(show = FALSE), axisLabel = list(
    interval = 0L
  )) 

p_hos <- df_vis %>% group_by(HOSPITAL) %>% summarise(n = n()) %>%
  mutate(HOSPITAL = as.factor(HOSPITAL)) %>%
  e_charts(x =HOSPITAL) %>% 
  e_bar(n, legend = TRUE, name = "Hospitalized")