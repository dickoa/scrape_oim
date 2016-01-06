### Bonus
library(rvest)
library(xml2) 
library(dplyr)
library(tidyr)
library(ggplot2)


###
url <- "http://missingmigrants.iom.int/en/latest-global-figures"

### Get the CSS using the browser inspect tool
## xpath can also be used (//*[@id="block-system-main"]/div/div/div/div/table[1])

tab <- url %>%
  read_html() %>%
  html_nodes(css = "table.table:nth-child(8)") %>%
  html_table()

str(tab)
tab <- tab[[1]]

### Some data cleaning
### A name for the first column
str(tab)
names(tab)[1] <- "Area"

test <- tab %>%
  gather(key = month, value = deaths, -Area)

### Non breaking space
pattern <- paste0("\\,|\\*|", intToUtf8(160))

###
tab <- tab %>%
  gather(key = month, value = deaths, -Area) %>%
  mutate(deaths = as.integer(gsub(pattern, "", deaths))) %>%
  spread(key = month, value = deaths)

### Final check
str(tab)
glimpse(tab)
summary(tab)

### Some ploting for fun
tab %>%
  filter(Area != "Total") %>%
  rename(total = `Total to date`) %>%
  ggplot(aes(reorder(Area, total), total, fill = Area)) +
  geom_bar(stat = "identity") +
  labs(x = "", y = "Total deaths") +
  coord_flip() +
  theme(legend.position = "none")

ggsave("deaths.png", last_plot())
