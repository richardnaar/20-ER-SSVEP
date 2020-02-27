# Emotion Regulation 2020 - SSVEP study / pilot

library(reshape2)
library(ggplot2)
rm(list = ls())

task1 <- c('Fix (.5 - 1.5 s)', '2018-01-01', '2018-02-01')
task2 <- c('IAPS (12.6 s)', '2018-02-01', '2019-01-01')
task3 <- c('Cue (.2 s)', '2018-08-01', '2018-08-15')
task4 <- c('ITI (2 s)', '2019-01-01', '2019-03-01')

#df <- as.data.frame(t(sapply(ls(pattern = '^task\\d'), function(x) eval(parse(text = x)))), row.names = FALSE)

df <- as.data.frame(rbind(task1, task2, task3, task4))
names(df) <- c('task', 'start', 'end')
df$task <- factor(df$task, levels = df$task)
df$start <- as.Date(df$start)
df$end <- as.Date(df$end)
df_melted <- melt(df, measure.vars = c('start', 'end'))

# starting date to begin plot
start_date <- as.Date('2018-01-01')

p <- ggplot(df_melted, aes(value, task)) + 
  geom_line(size = 10) +
  labs(x = '', y = '', title = '') + # Schematic outline of the task
  theme_bw(base_size = 20) +
  theme(plot.title = element_text(hjust = 0.5),
        panel.grid.major.x = element_line(colour="black", linetype = "dashed"),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        axis.text.x = element_blank()) +
  scale_x_date(date_labels = "none", limits = c(start_date, NA), date_breaks = '20 years')

# see ?strptime if you want your date in a different format
# see http://docs.ggplot2.org/current/scale_date.html if you want to adjust the x-axis

p + annotate("segment", x = as.Date('2018-02-15'), xend = as.Date('2018-08-01'), y = 2, yend = 2,
           colour = "darkorange", size = 1.5, linetype=1) +
  annotate("segment", x = as.Date('2018-08-01'), xend = as.Date('2018-12-27'), y = 2, yend = 2,
           colour = "darkgreen", size = 1.5, linetype=1)
  
