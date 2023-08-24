#################
##Libraries#####
################
library(dplyr, warn.conflicts = FALSE)
library(ggplot2)
library(grid)
library(gridExtra, warn.conflicts = FALSE)
library(tidyverse, warn.conflicts = FALSE)
library(extrafont)
library(ggcorrplot)
library(ggstatsplot)
################
survey_data = read.csv("data/df_survey_results.csv", stringsAsFactors = FALSE)
main_data = read.csv("data/df_main_analysis.csv", stringsAsFactors = FALSE)
full_data = read.csv("data/merged_df.csv", stringsAsFactors = FALSE)
centrality_data = read.csv("data/df_centrality.csv", stringsAsFactors = FALSE)
global_data = read.csv("df_global.csv", stringsAsFactors = FALSE)
font <- 'Helvetica'
loadfonts(device = "pdf")
windowsFonts(Helvetica = windowsFont("Helvetica"))
windowsFonts()

################
## Survey results 
df <- data.frame(item=rep(c('Survey 1', 'Survey 2', 'Intermedial 1', 
                            'Intermedial 2','Visualisation 1', 'Visualisation 2', 
                            'Farming 1','Farming 2' ), each=3),
                 group=rep(c('Unguided', 'Guided', 'Average'), times=8),
                 score=c(46.7, 63.0, 54.9, 65.3, 55.0, 60.2, 43.3, 55.7, 49.5, 
                         62.5,52.3,57.4,57.0,69.4,63.2,78.8,59.0,68.9,43.3,
                         55.0,49.2,57.5,48.3,52.9),
                 questions=c(NA, NA, NA, NA, NA, NA, 4.9, 5.3, 5.1, 
                             4.0,4.7,4.4,NA, NA, NA, NA, NA, NA,NA, NA, NA, NA, NA, NA))
df_average <- data.frame(Control=c('Survey', 'Vis Survey', 
                                   'Farming Survey'),
                         score=c(47, 67.1, 40.3))
df$item <- factor(df$item , levels = c('Survey 1', 'Survey 2', 'Intermedial 1', 
                                       'Intermedial 2','Visualisation 1', 'Visualisation 2', 
                                       'Farming 1','Farming 2'))
df$group <- factor(df$group, levels = c('Unguided', 'Guided', 'Average'))
df_average$Control <- factor(df_average$Control , levels = df_average$Control)

df2 <- data.frame(item=rep(c('Survey', 'Intermedial', 
                             'Visualisation', 
                             'Farming' ), each=2),
                  group=rep(c('Unguided', 'Guided'), times=4),
                  score=c(56.0, 59.0, 52.9, 54.0, 67.9, 64.2, 50.4, 51.7),
                  questions=c(NA, NA, 4.5, 5.0,NA, NA, NA, NA))
df_average <- data.frame(Control=rep(c('Survey', 'Visualisation', 
                                       'Farming')),
                         score=c(47, 67.1, 40.3))
df2$item <- factor(df2$item , levels = c('Survey','Intermedial',
                                         'Visualisation','Farming'))
df2$group <- factor(df2$group, levels = c('Unguided', 'Guided'))

par(mfrow = c(1,1))
par(family = font, cex.axis=2.4, cex.lab=2.4, cex.main=2.6)
par(oma = c(1, 1, 0, 0))
par(mar = c(2, 2, 2, 2))

ggplot(df, aes(fill=group, y=score, x=item)) + 
  geom_bar(position='dodge', stat='identity', show.legend = F)  +
  scale_fill_manual('', values=c('#bebada', '#fdc086', '#7fc97f'))+
  scale_y_continuous(name="", limits=c(0, 100), 
                     labels=c(47, 67.1, 40.3), breaks=c(47, 67.1, 40.3)) +
  geom_abline(data = df_average, aes(slope=0, intercept=score, 
                                     linetype=Control), show.legend = F) +
  geom_text(aes(label=score, y = 1), size=4, fontface = "bold", vjust = -0.4, 
            position = position_dodge(1)) +
  geom_text(aes(label=questions, y = 18), color='#4C4E52', size=4, fontface = "bold", vjust = 1.3,
            position = position_dodge(1)) +
  labs(x='', y='', title='') +      
  theme(axis.text.y = element_text(size = 14, face='bold'),
        axis.ticks.y = element_blank(),
        axis.text.x = element_text(size = 14, face='bold'),
        legend.text = element_text(size = 14), 
        legend.title = element_text(size = 14, face='bold'),
        panel.grid = element_blank(), 
        panel.background = element_blank(),
        axis.line.x = element_line(color='black'),
        axis.line.y = element_blank())


ggplot(df2, aes(fill=group, y=score, x=item)) + 
  geom_bar(position='dodge', stat='identity')  +
  scale_fill_manual('', limits=c('Unguided', 'Guided', 'Average'),
                    values=c('Unguided'='#bebada', 'Guided'='#fdc086', 
                             'Average'='#7fc97f'))+
  scale_y_continuous(name="", limits=c(0, 68), 
                     labels=c(47, 67.1, 40.3), breaks=c(47, 67.1, 40.3)) +
  geom_abline(data = df_average, aes(slope=0, intercept=score, 
                                     linetype=Control)) +
  geom_text(aes(label=score,  y = 1), size=4, fontface = "bold", vjust = -0.4, 
            position = position_dodge(1)) +
  geom_text(aes(label=questions,  y = 14), color='#4C4E52', size=4, fontface = "bold", 
            vjust = 1.5,
            position = position_dodge(1)) +
  labs(x='', y='', title='', linetype = 'Survey 0 Score') +      
  theme(axis.text.y = element_text(size = 14, face='bold'),
        axis.ticks.y = element_blank(),
        axis.text.x = element_text(size = 14, face='bold'),
        legend.text = element_text(size = 14), 
        legend.title = element_text(size = 14, face='bold'),
        panel.grid = element_blank(), 
        panel.background = element_blank(),
        axis.line.x = element_line(color='black'),
        axis.line.y = element_blank())



#######
# Local Topology
#############
#ONLY USE IF YOU WANT TO EXCLUDE CV1 BV1 and AV1 from ANALYSIS
#####
centrality_data <- subset(centrality_data,action!='c_v1')
centrality_data <- subset(centrality_data,action!='b_v1')
centrality_data <- subset(centrality_data,action!='a_v1')
#######
centrality_data_g <- subset(centrality_data, guidance==1)
centrality_data_u <- subset(centrality_data, guidance==0)

fs_g_b <- (centrality_data_g
           %>% group_by(action, guidance)
           %>% select(action, guidance, betweenness)
           %>% nest()
           %>% mutate(across(data, map, \(x) mean_sdl(x, mult = 0.2)))
           %>% unnest(cols = c(data))
)
fs_g_d <- (centrality_data_g
           ## partition data
           %>% group_by(action, guidance)
           %>% select(action, guidance, degree)
           ## convert value to a list-column
           %>% nest()
           ## summarise each entry
           %>% mutate(across(data, map, \(x) mean_sdl(x, mult = 0.2)))
           ## collapse back to a vector
           %>% unnest(cols = c(data))
)


fs_u_b <- (centrality_data_u
           ## partition data
           %>% group_by(action, guidance)
           %>% select(action, guidance, betweenness)
           ## convert value to a list-column
           %>% nest()
           ## summarise each entry
           %>% mutate(across(data, map, \(x) mean_sdl(x, mult = 0.2)))
           ## collapse back to a vector
           %>% unnest(cols = c(data))
)
fs_u_d <- (centrality_data_u
           ## partition data
           %>% group_by(action, guidance)
           %>% select(action, guidance, degree)
           ## convert value to a list-column
           %>% nest()
           ## summarise each entry
           %>% mutate(across(data, map, \(x) mean_sdl(x, mult = 0.2)))
           ## collapse back to a vector
           %>% unnest(cols = c(data))
)

fs_betweenness <- rbind(fs_g_b, fs_u_b)
fs_degree <- rbind(fs_g_d, fs_u_d)
fs_betweenness$guidance[fs_betweenness$guidance == 1] <- "Guided"
fs_betweenness$guidance[fs_betweenness$guidance == 0] <- "Unguided"
fs_degree$guidance[fs_degree$guidance == 1] <- "Guided"
fs_degree$guidance[fs_degree$guidance == 0] <- "Unguided"

# x axis treated as continuous variable
fs_betweenness$action <- as.factor(fs_betweenness$action)
fs_betweenness$guidance<- as.factor(fs_betweenness$guidance)
fs_degree$action <- as.factor(fs_degree$action)
fs_degree$guidance<- as.factor(fs_degree$guidance)

guide_color = c('#fdc086', '#bebada')
b_plot <- ggplot(data=fs_betweenness,
                 aes(x=action, y=y, group=guidance, 
                     color=guidance)) +
  scale_color_manual(values=guide_color, guide=FALSE)+
  scale_fill_manual(values = guide_color, guide=FALSE) +
  geom_line(size=1, alpha=0.75) + geom_point(size=1.5)+
  geom_ribbon(aes(x = action, ymax = ymax, ymin = ymin, fill=guidance), alpha = 0.3) +
  scale_y_continuous(breaks = c(0.01, 0.05,0.1, 0.15,0.2))+
  theme_minimal()+labs(x="", y='Betweenness')+
  theme(axis.text = element_text(size = 26, family = font),
        axis.title= element_text(size = 36, family = font),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank(),
        legend.position = "none")

d_plot <- ggplot(data=fs_degree, 
                 aes(x=action, y=y, group=guidance,
                     color=guidance)) +
  geom_line(size=1, alpha=0.75) + geom_point(size=1.5)+
  geom_ribbon(aes(x = action, ymax = ymax, ymin = ymin, fill=guidance), alpha = 0.3) +
  scale_color_manual(values=guide_color)+
  scale_fill_manual(values = guide_color) +
  theme_minimal()+labs(x="Actions", y='Degree')+
  scale_y_continuous(breaks = c(0.01, 0.05,0.1, 0.15,0.2))+
  theme(legend.key.width = unit(1, "cm"), legend.title = element_blank(), 
        axis.text = element_text(size = 26, family = font),
        axis.title= element_text(size = 36, family = font),
        legend.text = element_text(size = 26, family = font),
        legend.position = "top")


grid.arrange(b_plot, d_plot, heights=c(0.9, 1.1))

########
# Cut points 
##############
cut_point_data = read.csv("df_cut_points.csv", stringsAsFactors = FALSE)

cut_point_data_g<- cut_point_data %>%
  group_by(Guidance, Actions) %>%
  tally()

cut_point_data_s<- cut_point_data %>%
  group_by(Session, Actions) %>%
  tally()

cut_point_data_s_g<- cut_point_data %>%
  group_by(Session, Guidance, Actions) %>%
  tally()

cut_point_data_g <- as.data.frame(cut_point_data_g)
cp_g <- cut_point_data_g[cut_point_data_g$Guidance=='g',]
cp_u <- cut_point_data_g[cut_point_data_g$Guidance=='u',]
cp_g = cp_g[order(-cp_g$n),]
cp_u = cp_u[order(-cp_u$n),]
cp_g
cp_u
#######
# Times heat map # Global Characteristics
#######
main_data <- subset(main_data,Participant!=42864671 )

names(main_data)

main_analysis_guided <- data.frame(Participant = main_data$Participant[main_data$Guidance == 'guided'], 
                                   Total_Time = round(main_data$Total.Time[main_data$Guidance == 'guided']/60, 2),
                                   A_Time = round(main_data$A.Time[main_data$Guidance == 'guided']/60, 2),
                                   B_Time = round(main_data$B.Time[main_data$Guidance == 'guided']/60, 2),
                                   C_Time = round(main_data$C.Time[main_data$Guidance == 'guided']/60, 2),
                                   D_Time = round(main_data$D.Time[main_data$Guidance == 'guided']/60, 2))



main_analysis_unguided <- data.frame(Participant = main_data$Participant[main_data$Guidance == 'unguided'], 
                                     Total_Time = round(main_data$Total.Time[main_data$Guidance == 'unguided']/60, 2),
                                     A_Time = round(main_data$A.Time[main_data$Guidance == 'unguided']/60, 2),
                                     B_Time = round(main_data$B.Time[main_data$Guidance == 'unguided']/60, 2),
                                     C_Time = round(main_data$C.Time[main_data$Guidance == 'unguided']/60, 2),
                                     D_Time = round(main_data$D.Time[main_data$Guidance == 'unguided']/60, 2))
main_analysis_both <- data.frame(Participant = main_data$Participant, 
                                 Total_Time = round(main_data$Total.Time/60, 2),
                                 A_Time = round(main_data$A.Time/60, 2),
                                 B_Time = round(main_data$B.Time/60, 2),
                                 C_Time = round(main_data$C.Time/60, 2),
                                 D_Time = round(main_data$D.Time/60, 2))

rownames(main_analysis_guided) <- main_analysis_guided$Participant
main_analysis_guided <- main_analysis_guided[,-1]

rownames(main_analysis_unguided) <- main_analysis_unguided$Participant
main_analysis_unguided <- main_analysis_unguided[,-1]

main_analysis_both <- main_analysis_both[-1]


Guided <- colMeans(main_analysis_guided)
Unguided <- colMeans(main_analysis_unguided)
All <- colMeans(main_analysis_both)
main_comparison  <- rbind(Guided, Unguided, All) 
main_comparison <- as.data.frame(main_comparison)
mean_per_cluster <- mean(main_comparison$Total_Time)

heatmap_main <- main_comparison %>%
  rownames_to_column() %>%
  gather(colname, value, -rowname)
heatmap_main[heatmap_main == "A_Time"] <- "Cluster A"
heatmap_main[heatmap_main == "B_Time"] <- "Cluster B"
heatmap_main[heatmap_main == "C_Time"] <- "Cluster C"
heatmap_main[heatmap_main == "D_Time"] <- "Cluster D"
heatmap_main[heatmap_main == "Total_Time"] <- "Total Time"

ggplot(heatmap_main, aes(x = colname, y = rowname, fill = ifelse(value>20, value/4, value))) +
  geom_tile() +
  geom_text(size = 26, family = font, 
            aes(label = ifelse(value>20, format(round(value, 2), nsmall = 2), 
                               format(round(value, 2), nsmall = 2)) )) +
  scale_fill_gradient2(high = "#ef8a62",
                       low = "#67a9cf",
                       guide = "colourbar",  
                       midpoint=mean_per_cluster/4,
                       breaks=seq(0,16.66,4),
                       limits=c(0, 16.66))+
  theme(axis.title.x=element_blank(), 
        legend.title = element_text(size = 48, family = font),
        axis.text = element_text(size = 48, family = font),
        axis.title.y=element_blank(), 
        axis.ticks.x = element_blank(),
        axis.ticks.y = element_blank(),
        legend.position="top",legend.justification="center", 
        legend.direction="horizontal", legend.key.width = unit(3, "cm"))+ 
  scale_x_discrete(position = "top")+ 
  guides(fill=guide_colourbar(title="Average Minutes Per Cluster", reverse=F, label=F))




##########
#box_plot
########

survey_data <- subset(survey_data,Participant!=42864671 )

time_guided <- data.frame(Participant = main_data$Participant[main_data$Guidance == 'guided'], 
                          Guided = main_data$Total.Time[main_data$Guidance == 'guided']/60)
time_unguided <- data.frame(Participant = main_data$Participant[main_data$Guidance == 'unguided'], 
                            Unguided = main_data$Total.Time[main_data$Guidance == 'unguided']/60)  
time_both <- data.frame(Participant = main_data$Participant, 
                        Both = main_data$Total.Time/60) 

time_merge <- merge(time_unguided,time_guided,by="Participant")

rownames(time_merge) <- time_merge$Participant
time_merge <- time_merge[,-1]
time_both <- time_both[2]

actions_guided <- data.frame(Participant = main_data$Participant[main_data$Guidance == 'guided'], 
                             Guided = main_data$Actions[main_data$Guidance == 'guided'])
actions_unguided <- data.frame(Participant = main_data$Participant[main_data$Guidance == 'unguided'], 
                               Unguided = main_data$Actions[main_data$Guidance == 'unguided'])    
actions_both <- data.frame(Participant = main_data$Participant, 
                           Both = main_data$Actions) 

actions_merge <- merge(actions_unguided,actions_guided,by="Participant")

rownames(actions_merge) <- actions_merge$Participant
actions_merge <- actions_merge[,-1]
actions_both <- actions_both[2]

time_means <- data.frame(Guidance = c('Unguided', 'Guided'),
                         x = c(mean(time_merge$Unguided),
                               mean(time_merge$Guided)))  
action_means <- data.frame(Guidance = c('Unguided', 'Guided'),
                           x = c(mean(actions_merge$Unguided),
                                 mean(actions_merge$Guided)))  
time_sd <- data.frame(Guidance = c('Unguided', 'Guided'),
                      x = c(sd(time_merge$Unguided),
                            sd(time_merge$Guided)))  
action_sd <- data.frame(Guidance = c('Unguided', 'Guided'),
                        x = c(sd(actions_merge$Unguided),
                              sd(actions_merge$Guided))) 
########
par(mfrow = c(1, 2))
par(family = font, cex.axis=2.4, cex.lab=2.4, cex.main=2.6)
par(oma = c(5, 1, 1, 1))
par(mar = c(5, 2, 2, 2))

proportion <- c(0.5,0.5)

boxplot(time_merge,main='Time (minutes)',
        col = c('#bebada', '#fdc086'), ylab="",xaxt='n')
invisible(lapply(1:nrow(time_means),
                 function(i) segments(x0 = i - 0.8*proportion[i],
                                      y0 = time_means$x[i],
                                      x1 = i + 0.8*proportion[i],
                                      y1 = time_means$x[i],
                                      col = "#e41a1c", lwd = 2)))


text(x = 1:nrow(time_means)-0.25, cex=2.5, family =font,                   
     y = 37,
     labels =  paste('\u{0078}\u{0304} = ', round(time_means$x, 1)),
     col = "#e41a1c")

text(x = 1:nrow(time_sd)+0.25, cex=2.5, family =font,                           
     y = 37,
     labels =  paste("\u03C3 = ",(round(time_sd$x,2))),
     col = "black")

legend('bottomright',legend = c("Unguided"), border="black", 
       fill = c('#bebada'), lwd = 1, xpd = TRUE, horiz = TRUE,
       cex = 2.5, seg.len=0, bty = 'n', inset= c(-0.25, -0.15), x.intersp = 0.1)


boxplot(actions_merge, main="Number of Actions", 
        col = c('#bebada', '#fdc086'), ylab="",xaxt='n')

invisible(lapply(1:nrow(action_means),
                 function(i) segments(x0 = i - 0.8*proportion[i],
                                      y0 = action_means$x[i],
                                      x1 = i + 0.8*proportion[i],
                                      y1 = action_means$x[i],
                                      col = "#e41a1c", lwd = 2)))

text(x = 1:nrow(action_means)-0.25, family =font,  
     cex=2.5,                    
     y = 210, 
     labels = paste('\u{0078}\u{0304} = ', round(action_means$x, 1)),
     col = "#e41a1c")


text(x = 1:nrow(action_sd)+0.25, family =font,  
     y = 210, cex=2.5,
     labels = paste("\u03C3 = ",(round(action_sd$x,2))),
     col = "black")
legend('bottomleft',legend = c("Guided"), border="black", 
       fill = c('#fdc086'),lwd = 1, xpd = TRUE, horiz = TRUE,
       cex = 2.5, seg.len=0, bty = 'n', inset= c(-0.1, -0.15), x.intersp = 0.1)


############
survey_guided <- data.frame(Participant = survey_data$Participant[survey_data$Guidance == 'guided'], 
                            Guided = survey_data$All.Score[survey_data$Guidance == 'guided'])
survey_unguided <- data.frame(Participant = survey_data$Participant[survey_data$Guidance == 'unguided'], 
                              Unguided = survey_data$All.Score[survey_data$Guidance == 'unguided'])   
survey_both <- data.frame(Participant = survey_data$Participant[survey_data$Session != 'Control'], 
                          All = survey_data$All.Score[survey_data$Session != 'Control']) 

survey_merge <- merge(survey_unguided,survey_guided, by="Participant")

rownames(survey_merge) <- survey_merge$Participant
survey_merge <- survey_merge[,-1]
survey_both <- survey_both[2]

Vis_survey_guided <- data.frame(Participant = survey_data$Participant[survey_data$Guidance == 'guided'], 
                                Guided = survey_data$Vis.Score[survey_data$Guidance == 'guided'])
Vis_survey_unguided <- data.frame(Participant = survey_data$Participant[survey_data$Guidance == 'unguided'], 
                                  Unguided = survey_data$Vis.Score[survey_data$Guidance == 'unguided'])   
vis_survey_both <- data.frame(Participant = survey_data$Participant[survey_data$Session != 'Control'], 
                              All = survey_data$Vis.Score[survey_data$Session != 'Control']) 

vis_survey_merge <- merge(Vis_survey_unguided,Vis_survey_guided, by="Participant")

rownames(vis_survey_merge) <- vis_survey_merge$Participant
vis_survey_merge <- vis_survey_merge[,-1]
vis_survey_both <- vis_survey_both[2]

farm_survey_guided <- data.frame(Participant = survey_data$Participant[survey_data$Guidance == 'guided'], 
                                 Guided = survey_data$Farming.Score[survey_data$Guidance == 'guided'])
farm_survey_unguided <- data.frame(Participant = survey_data$Participant[survey_data$Guidance == 'unguided'], 
                                   Unguided = survey_data$Farming.Score[survey_data$Guidance == 'unguided'])  
farm_survey_both <- data.frame(Participant = survey_data$Participant[survey_data$Session != 'Control'], 
                               All = survey_data$Farming.Score[survey_data$Session != 'Control']) 

farm_survey_merge <- merge(farm_survey_unguided,farm_survey_guided, by="Participant")

rownames(farm_survey_merge) <- farm_survey_merge$Participant
farm_survey_merge <- farm_survey_merge[,-1]
farm_survey_both <- farm_survey_both[2]

inter_survey_guided <- data.frame(Participant = survey_data$Participant[survey_data$Guidance == 'guided'], 
                                  Guided = survey_data$Inter_survey_Score[survey_data$Guidance == 'guided'])
inter_survey_unguided <- data.frame(Participant = survey_data$Participant[survey_data$Guidance == 'unguided'], 
                                    Unguided = survey_data$Inter_survey_Score[survey_data$Guidance == 'unguided'])  
inter_survey_both <- data.frame(Participant = survey_data$Participant[survey_data$Session != 'Control'], 
                                All = survey_data$Inter_survey_Score[survey_data$Session != 'Control']) 

inter_survey_merge <- merge(inter_survey_unguided,inter_survey_guided, by="Participant")

rownames(inter_survey_merge) <- inter_survey_merge$Participant
inter_survey_merge <- inter_survey_merge[,-1]
inter_survey_both <- inter_survey_both[2]

survey_means <- data.frame(Guidance = c('Unguided', 'Guided'),
                           x = c(mean(survey_merge$Unguided),
                                 mean(survey_merge$Guided)))  
vis_survey_means <- data.frame(Guidance = c('Unguided', 'Guided'),
                               x = c(mean(vis_survey_merge$Unguided),
                                     mean(vis_survey_merge$Guided))) 
farm_survey_means <- data.frame(Guidance = c('Unguided', 'Guided'),
                                x = c(mean(farm_survey_merge$Unguided),
                                      mean(farm_survey_merge$Guided)
                                )) 

inter_survey_means <- data.frame(Guidance = c('Unguided', 'Guided'),
                                 x = c(mean(inter_survey_merge$Unguided),
                                       mean(inter_survey_merge$Guided))) 


survey_sd <- data.frame(Guidance = c('Unguided', 'Guided'),
                        x = c(sd(survey_merge$Unguided),
                              sd(survey_merge$Guided)))  
vis_survey_sd <- data.frame(Guidance = c('Unguided', 'Guided'),
                            x = c(sd(vis_survey_merge$Unguided),
                                  sd(vis_survey_merge$Guided))) 
farm_survey_sd <- data.frame(Guidance = c('Unguided', 'Guided'),
                             x = c(sd(farm_survey_merge$Unguided),
                                   sd(farm_survey_merge$Guided))) 

inter_survey_sd <- data.frame(Guidance = c('Unguided', 'Guided'),
                              x = c(sd(inter_survey_merge$Unguided),
                                    sd(inter_survey_merge$Guided))) 


#############
par(mfrow = c(2, 2))
par(family = font, cex.axis=2.4, cex.lab=2.4, cex.main=2.6)
par(oma = c(5, 8, 1, 1))
par(mar = c(5, 2, 2, 2))

proportion <- c(0.5,0.5)

boxplot(survey_merge, main="Survey", width = proportion,
        col = c('#bebada', '#fdc086'),xaxt='n')

invisible(lapply(1:nrow(survey_means),
                 function(i) segments(x0 = i - 0.8*proportion[i],
                                      y0 = survey_means$x[i],
                                      x1 = i + 0.8*proportion[i],
                                      y1 = survey_means$x[i],
                                      col = "#e41a1c", lwd = 2)))

text(x = 1:nrow(survey_means)-0.25, family =font,  
     cex=2.5,                             
     y = 71,
     labels =  paste('\u{0078}\u{0304} = ', round(survey_means$x, 1)),
     col = "#e41a1c")
text(x = 1:nrow(survey_sd)+0.25,  family =font,  
     cex=2.5,                              
     y = 71,
     labels =  paste("\u03C3 = ",(round(survey_sd$x,2))),
     col = "black")

##############

boxplot(inter_survey_merge, main="Inter Survey", 
        width = proportion,
        col = c('#bebada', '#fdc086'),xaxt='n')
invisible(lapply(1:nrow(inter_survey_means),
                 function(i) segments(x0 = i - 0.8*proportion[i],
                                      y0 = inter_survey_means$x[i],
                                      x1 = i + 0.8*proportion[i],
                                      y1 = inter_survey_means$x[i],
                                      col = "#e41a1c", lwd = 2)))


text(x = 1:nrow(inter_survey_means)-0.25, family =font,  
     cex=2.5, y = 80,
     labels =  paste('\u{0078}\u{0304} = ', round(inter_survey_means$x, 1)),
     col = "#e41a1c")

text(x = 1:nrow(inter_survey_sd)+0.25,family =font,  
     cex=2.5, y = 80,
     labels =  paste("\u03C3 = ",(round(inter_survey_sd$x,2))),
     col = "black")

####################
boxplot(vis_survey_merge, main="Visualization Survey", 
        width = proportion,
        col = c('#bebada',  '#fdc086'),xaxt='n')

invisible(lapply(1:nrow(vis_survey_means),
                 function(i) segments(x0 = i - 0.8*proportion[i],
                                      y0 = vis_survey_means$x[i],
                                      x1 = i + 0.8*proportion[i],
                                      y1 = vis_survey_means$x[i],
                                      col = "#e41a1c", lwd = 2)))


text(x = 1:nrow(vis_survey_means)-0.25, family =font,  
     cex=2.5, y = 80,
     labels =  paste('\u{0078}\u{0304} = ', round(vis_survey_means$x, 1)),
     col = "#e41a1c")

text(x = 1:nrow(vis_survey_sd)+0.25, family =font,  
     cex=2.5, y = 80,
     labels =  paste("\u03C3 = ",(round(vis_survey_sd$x,2))),
     col = "black")


legend('bottomright',legend = c("Unguided"), border="black", 
       fill = c('#bebada'), lwd = 1, xpd = TRUE, horiz = TRUE,
       cex = 2.5, seg.len=0, bty = 'n', inset= c(-0.23, -0.25), x.intersp = 0.1)


##############
boxplot(farm_survey_merge, main="Farming Survey", 
        width = proportion,
        col = c('#bebada',  '#fdc086'),xaxt='n')

invisible(lapply(1:nrow(farm_survey_means),
                 function(i) segments(x0 = i - 0.8*proportion[i],
                                      y0 = farm_survey_means$x[i],
                                      x1 = i + 0.8*proportion[i],
                                      y1 = farm_survey_means$x[i],
                                      col = "#e41a1c", lwd = 2)))


text(x = 1:nrow(farm_survey_means)-0.25, family =font,  
     cex=2.5, y = 70,
     labels =  paste('\u{0078}\u{0304} = ', round(farm_survey_means$x, 1)),
     col = "#e41a1c")

text(x = 1:nrow(farm_survey_sd)+0.25, family =font,  
     cex=2.5, y = 70,
     labels =  paste("\u03C3 = ",(round(farm_survey_sd$x,2))),
     col = "black")

legend('bottomleft',legend = c("Guided"), border="black", 
       fill = c('#fdc086'),lwd = 1, xpd = TRUE, horiz = TRUE,
       cex = 2.5, seg.len=0, bty = 'n', inset= c(-0.09, -0.25), x.intersp = 0.1)

mtext('Score (Percentile)', side = 2, outer = TRUE, line = 1, cex = 2.6)
#####################
# Correlation for Hypothesis 1
#########################
names(full_data)
full_data[,c(2:14)] <- lapply(full_data[,c(2:14)], as.numeric)

# Remove outlier
full_data <- subset(full_data,Participant!=42864671)
apply(full_data[,c(5:14)],2,shapiro.test)

colnames(full_data) <- c("Participant", "Session", "Guidance", 
                         "Inter Survey Qs", "Inter Survey", "Survey", 
                         "Vis Survey", "Farming Survey", "Actions", "Time", 
                         "Cluster A","Cluster B","Cluster C","Cluster D")

# H1a
#############

corr_var <- c('Survey', 'Inter Survey', 'Actions','Time')
full_data_cor <- cor(full_data[corr_var], full_data[corr_var],  
                     method = "spearman", use = "complete.obs")


spearman_corr <- cor.test(full_data$Actions, full_data$`Inter Survey`,  
                          method = "spearman", exact= FALSE)
spearman_corr
round(p.adjust(spearman_corr$p.value, method = 'bonferroni', n = 4), 3)


spearman_corr <- cor.test(full_data$Time, full_data$`Inter Survey`,  
                          method = "spearman", exact= FALSE)
spearman_corr
round(p.adjust(spearman_corr$p.value, method = 'bonferroni', n = 4), 3)



spearman_corr <- cor.test(full_data$Actions, full_data$`Survey`,  
                          method = "spearman", exact= FALSE)
spearman_corr
round(p.adjust(spearman_corr$p.value, method = 'bonferroni', n = 4), 3)



spearman_corr <- cor.test(full_data$Time, full_data$`Survey`,  
                          method = "spearman", exact= FALSE)
spearman_corr
round(p.adjust(spearman_corr$p.value, method = 'bonferroni', n = 4), 3)


corrp.mat <- cor_pmat(full_data[corr_var],  
                      method = "spearman", exact= FALSE)
corrp.mat<- corrp.mat[-1:-2,-3:-4]
full_data_cor<- full_data_cor[-1:-2,-3:-4]
ggcorrplot(full_data_cor, p.mat = corrp.mat*4,
           type = "full", lab = TRUE, tl.cex = 30, 
           outline.color = "white", tl.srt = 0,
           ggtheme = ggplot2::theme_bw, pch.cex = 80, lab_size = 15, 
           colors = c("#6D9EC1", "white", "#E46726") 
)+
  theme(legend.title = element_text(size=22))


############
# H1b
#################

model <- aov(Time ~ Guidance, data = full_data)
summary(model)
summary(model)[[1]][["Pr(>F)"]][1]

model <- aov(Time ~ Guidance, data = full_data)
summary(model)
summary(model)[[1]][["Pr(>F)"]][1]

model <- aov(Actions ~ Guidance, data = full_data)
summary(model)
summary(model)[[1]][["Pr(>F)"]][1]

model <- aov(Time ~ Session, data = full_data)
summary(model)
summary(model)[[1]][["Pr(>F)"]][1]

model <- aov(Actions ~ Session, data = full_data)
summary(model)
summary(model)[[1]][["Pr(>F)"]][1]

plot(full_data[,c(5,6,9,10)])



###########
# H2a Global Topology
############

global_data$Guidance[global_data$Guidance == 'g'] <- 1
global_data$Guidance[global_data$Guidance == 'u'] <- 0
global_data[] <- lapply(global_data[], as.numeric)
# Remove outlier
global_data <- subset(global_data, Participant!=42864671)
mean(global_data$Centralization)
mean(global_data$Density)

apply(global_data[,c(4:5)],2,shapiro.test)

full_data_new = merge(full_data, global_data, by=c('Participant', 'Session', 'Guidance'))

write.csv(full_data_new[,c(1:3,5:6, 9:10, 15:16)], "df_comparison.csv", row.names=FALSE)

centralization_guided <- data.frame(Participant = global_data$Participant[global_data$Guidance == 1], 
                                    Guided = global_data$Centralization[global_data$Guidance == 1])
centralization_unguided <- data.frame(Participant = global_data$Participant[global_data$Guidance == 0], 
                                      Unguided = global_data$Centralization[global_data$Guidance == 0])  
centralization_both <- data.frame(Participant = global_data$Participant, 
                                  Both = global_data$Centralization) 

centralization_merge <- merge(centralization_unguided,centralization_guided,by="Participant")

rownames(centralization_merge) <- centralization_merge$Participant
centralization_merge <- centralization_merge[,-1]
centralization_both <- centralization_both[2]

density_guided <- data.frame(Participant = global_data$Participant[global_data$Guidance == 1], 
                             Guided = global_data$Density[global_data$Guidance == 1])
density_unguided <- data.frame(Participant = global_data$Participant[global_data$Guidance == 0], 
                               Unguided = global_data$Density[global_data$Guidance == 0])    
density_both <- data.frame(Participant = global_data$Participant, 
                           Both = global_data$Density) 

density_merge <- merge(density_unguided,density_guided,by="Participant")

rownames(density_merge) <- density_merge$Participant
density_merge <- density_merge[,-1]
density_both <- density_both[2]

centralization_means <- data.frame(Guidance = c('Unguided', 'Guided'),
                                   x = c(mean(centralization_merge$Unguided),
                                         mean(centralization_merge$Guided)))  
density_means <- data.frame(Guidance = c('Unguided', 'Guided'),
                            x = c(mean(density_merge$Unguided),
                                  mean(density_merge$Guided)))  
centralization_sd <- data.frame(Guidance = c('Unguided', 'Guided'),
                                x = c(sd(centralization_merge$Unguided),
                                      sd(centralization_merge$Guided)))  
density_sd <- data.frame(Guidance = c('Unguided', 'Guided'),
                         x = c(sd(density_merge$Unguided),
                               sd(density_merge$Guided))) 

##########
# Box plots
########
par(mfrow = c(1, 2))
par(family = font, cex.axis=2.4, cex.lab=2.4, cex.main=2.6)
par(oma = c(5, 1, 0, 0))
par(mar = c(5, 2, 2, 2))

proportion <- c(0.5,0.5)
boxplot(centralization_merge, main="Centralization", 
        width = proportion,
        col = c('#bebada',  '#fdc086'), ylab="",xaxt='n')
invisible(lapply(1:nrow(centralization_means),
                 function(i) segments(x0 = i - 0.8*proportion[i],
                                      y0 = centralization_means$x[i],
                                      x1 = i + 0.8*proportion[i],
                                      y1 = centralization_means$x[i],
                                      col = "#e41a1c", lwd = 2)))


text(x = 1:nrow(centralization_means)-0.25, cex=2.5, family =font,                     
     y = 0.42,
     labels =  paste('\u{0078}\u{0304} = ', round(centralization_means$x, 3)),
     col = "#e41a1c")

text(x = 1:nrow(centralization_sd)+0.25, cex=2.5, family =font,                           
     y = 0.42,
     labels =  paste("\u03C3 = ",(round(centralization_sd$x,3))),
     col = "black")

legend('bottomright',legend = c("Unguided"), border="black", 
       fill = c('#bebada'), lwd = 1, xpd = TRUE, horiz = TRUE,
       cex = 2.5, seg.len=0, bty = 'n', inset= c(-0.25, -0.15), x.intersp = 0.1)


boxplot(density_merge, main="Density", width = proportion,
        col = c('#bebada', '#fdc086'), ylab="Density",xaxt='n')

invisible(lapply(1:nrow(density_means),
                 function(i) segments(x0 = i - 0.8*proportion[i],
                                      y0 = density_means$x[i],
                                      x1 = i + 0.8*proportion[i],
                                      y1 = density_means$x[i],
                                      col = "#e41a1c", lwd = 2)))

text(x = 1:nrow(density_means)-0.25, family =font,  
     cex=2.5,                    
     y = 0.2, 
     labels = paste('\u{0078}\u{0304} = ', round(density_means$x, 3)),
     col = "#e41a1c")


text(x = 1:nrow(density_sd)+0.25, family =font,  
     y = 0.2, cex=2.5,
     labels = paste("\u03C3 = ",(round(density_sd$x,3))),
     col = "black")

legend('bottomleft',legend = c("Guided"), border="black", 
       fill = c('#fdc086'),lwd = 1, xpd = TRUE, horiz = TRUE,
       cex = 2.5, seg.len=0, bty = 'n', inset= c(-0.1, -0.15), x.intersp = 0.1)


########
# Correlations
###################
library(car)
scatterplotMatrix(full_data_new[,c(8, 15,16)],
                  smooth=FALSE, col = 'black',
                  regLine = c(col='red'), cex.axis = 2.6,
                  cex.labels = 5, cex.main = 2)
plot(full_data_new[,c(8, 15,16)])
abline(lm(full_data_new[,c(8, 15,16)]),col='red')
apply(full_data_new[,c(8, 15,16)],2,shapiro.test)

mr <- lm(`Farming Survey`~Centralization+Density, data=full_data_new)
summary(mr)


####################
# Does a combination of session and Guidance affect Centralization, density, or combination 
test_aov <- aov(Density+Centralization~Guidance, full_data_new)
summary(test_aov)


###############
names(full_data_new)

full_data_new_guided <- data.frame(Participant = full_data_new$Participant[full_data_new$Guidance == 1], 
                                   Centralization = round(full_data_new$Centralization[full_data_new$Guidance == 1], 2),
                                   Density = round(full_data_new$Density[full_data_new$Guidance == 1], 2))



full_data_new_unguided <- data.frame(Participant = full_data_new$Participant[full_data_new$Guidance == 0], 
                                     Centralization = round(full_data_new$Centralization[full_data_new$Guidance == 0], 2),
                                     Density = round(full_data_new$Density[full_data_new$Guidance == 0], 2))

rownames(full_data_new_guided) <- full_data_new_guided$Participant
full_data_new_guided <- full_data_new_guided[,-1]

rownames(full_data_new_unguided) <- full_data_new_unguided$Participant
full_data_new_unguided <- full_data_new_unguided[,-1]



Guided <- colMeans(full_data_new_guided)
Unguided <- colMeans(full_data_new_unguided)
full_data_new_comparison  <- rbind(Guided, Unguided) 
full_data_new_comparison <- as.data.frame(full_data_new_comparison)

heatmap_new <- full_data_new_comparison %>%
  rownames_to_column() %>%
  gather(colname, value, -rowname)


ggplot(heatmap_new, aes(x = colname, y = rowname, fill = value)) +
  geom_tile() +
  geom_text(size = 6, family = font, 
            aes(label = format(round(value, 2), nsmall = 2))) +
  scale_fill_gradient2(high = "#E46726",
                       low = "#e0ecf4",
                       guide = "colourbar",  
                       breaks=seq(0,1,0.1),
                       limits=c(0, 1))+
  theme(axis.title.x=element_blank(), 
        legend.title = element_text(size = 14, family = font),
        axis.text = element_text(size = 16, family = font),
        axis.title.y=element_blank(), 
        axis.ticks.x = element_blank(),
        axis.ticks.y = element_blank(),
        legend.position="top",legend.justification="center", 
        legend.direction="horizontal", legend.key.width = unit(1, "cm"))+ 
  scale_x_discrete(position = "top")+ 
  guides(fill=guide_colourbar(title="Average value (0-1)", reverse=F, label=F))


full_data_new_s2 <- data.frame(Participant = full_data_new$Participant[full_data_new$Session == 2], 
                               Centralization = round(full_data_new$Centralization[full_data_new$Session == 2], 2),
                               Density = round(full_data_new$Density[full_data_new$Session == 2], 2))



full_data_new_s1 <- data.frame(Participant = full_data_new$Participant[full_data_new$Session == 1], 
                               Centralization = round(full_data_new$Centralization[full_data_new$Session == 1], 2),
                               Density = round(full_data_new$Density[full_data_new$Session == 1], 2))

rownames(full_data_new_s2) <- full_data_new_s2$Participant
full_data_new_s2 <- full_data_new_s2[,-1]

rownames(full_data_new_s1) <- full_data_new_s1$Participant
full_data_new_s1 <- full_data_new_s1[,-1]



Session2 <- colMeans(full_data_new_s2)
Session1 <- colMeans(full_data_new_s1)
full_data_new_comparison  <- rbind(Session2, Session1) 
full_data_new_comparison <- as.data.frame(full_data_new_comparison)

heatmap_new_2 <- full_data_new_comparison %>%
  rownames_to_column() %>%
  gather(colname, value, -rowname)
ggplot(heatmap_new_2, aes(x = colname, y = rowname, fill = value)) +
  geom_tile() +
  geom_text(size = 6, family = font, 
            aes(label = format(round(value, 2), nsmall = 2))) +
  scale_fill_gradient2(high = "#E46726",
                       low = "#e0ecf4",
                       guide = "colourbar",  
                       breaks=seq(0,1,0.1),
                       limits=c(0, 1))+
  theme(axis.title.x=element_blank(), 
        legend.title = element_text(size = 14, family = font),
        axis.text = element_text(size = 16, family = font),
        axis.title.y=element_blank(), 
        axis.ticks.x = element_blank(),
        axis.ticks.y = element_blank(),
        legend.position="top",legend.justification="center", 
        legend.direction="horizontal", legend.key.width = unit(1, "cm"))+ 
  scale_x_discrete(position = "top")+ 
  guides(fill=guide_colourbar(title="Average value (0-1)", reverse=F, label=F))



heatmap_new_3 <- rbind(heatmap_new, heatmap_new_2)
col_order <- c("Guided", "Unguided", "Session2", "Session1")
heatmap_new_3$rowname <- factor(heatmap_new_3$rowname, levels = col_order)
ggplot(heatmap_new_3, aes(x = colname, y = rowname, fill = value)) +
  geom_tile() +
  geom_text(size = 6, family = font, 
            aes(label = format(round(value, 2), nsmall = 2))) +
  scale_fill_gradient2(high = "#E46726",
                       low = "#e0ecf4",
                       guide = "colourbar",  
                       breaks=seq(0,1,0.1),
                       limits=c(0, 1))+
  theme(axis.title.x=element_blank(), 
        legend.title = element_text(size = 12, family = font),
        axis.text = element_text(size = 14, family = font),
        axis.title.y=element_blank(), 
        axis.ticks.x = element_blank(),
        axis.ticks.y = element_blank(),
        legend.position="top",legend.justification="center", 
        legend.direction="horizontal", legend.key.width = unit(0.7, "cm"))+ 
  scale_x_discrete(position = "top")+ 
  guides(fill=guide_colourbar(title="Average value (0-1)", reverse=F, label=F))







