#####Part 1#######
#################
library(statnet)
library(GGally)
library(ggplot2)
library(dplyr)
library(tidyr)
library(stringr)
library(scales)

getwd()
# reading all node files.
png_nodes_files <- lapply(Sys.glob('data/nodes/png_nodes_*.csv'), read.csv)
png_edges_files <- lapply(Sys.glob('data/edges/png_edges_*.csv'), read.csv)

file_names <- lapply(Sys.glob('data/nodes/png_nodes_*.csv'), basename)

# Reading file names
all_names = c()
for (x in 1:length(file_names)){
  y_n <- str_sub(file_names[x], start=11, end=-5)
  all_names <- append(all_names, y_n)
}


options(dplyr.summarise.inform = FALSE)
df_global = data.frame()
df_cut_points = data.frame()
all_contingency = 0
# Calculate network metrics
for (x in 1:length(all_names)){
  png_nodes <- as.data.frame(do.call(cbind, png_nodes_files[x]))
  png_edges <- as.data.frame(do.call(cbind, png_edges_files[x]))
  
  png_nodes <- png_nodes[order(png_nodes$Node),]
  if("b_d2" %in% list(png_nodes$Node))
  {
    print(file_names[x])
  }
  png_edges <- png_edges[order(png_edges$Source),]
  
  row.names(png_nodes) <- NULL
  row.names(png_edges) <- NULL
  
  times <- png_nodes$Time
  clusters <- png_nodes$Cluster
  nodes <- png_nodes$Node
  opacities <- png_nodes$Opacity
  actions <- png_nodes$Action.Type
  
  list_c = c()
  list_c['a'] = 'A'
  list_c['b'] = 'B'
  list_c['c'] = 'C'
  list_c['d'] = 'D'
  
  # Calculate and write up contingency table for each participant of cluster connections
  png_edges_n <- png_edges[order(png_edges$Source),]
  row.names(png_edges_n) <- NULL
  png_edges_matrix=png_edges_n
  
  
  for(y in 1:length(png_edges_matrix$Source)) {
    first_letter = substr(png_edges_matrix$Source[[y]],1,1)
    second_letter = substr(png_edges_matrix$Target[[y]],1,1)
    png_edges_matrix$Source[[y]] = list_c[first_letter]
    png_edges_matrix$Target[[y]]= list_c[second_letter]
  }
  
  png_edges_matrix$Frequency <- as.numeric(png_edges_matrix$Frequency)
  agg_tbl <- png_edges_matrix %>% group_by(Source, Target) %>% 
    summarise(Freq=sum(Frequency))
  
  
  xtabs(Freq ~ Source+Target, data=agg_tbl)
  cont_tbl <- addmargins(xtabs(Freq ~ Source+Target, agg_tbl))
  all_contingency = all_contingency + cont_tbl
  
  scale_values <- function(x){(x-min(x))/(max(x)-min(x))}

  # Construct Network
  
  png_network <- network(png_edges, directed = T, matrix.type = "edgelist")
  
  p_g_s <- strsplit(all_names[x],split = '_') #participant, guidance, session
  global_metric = c(p_g_s[[1]][1], p_g_s[[1]][2], p_g_s[[1]][3], centralization(png_network, betweenness, mode="digraph"), 
                    network.density(png_network))
  
  df_global = rbind(df_global, global_metric)
  
  # Extract and append Cut points
  cut <- cutpoints (png_network, mode = "digraph", return.indicator = T)
  length (cut [cut==T])
  
  cutpoints_actions <-data.frame (cutpoint = cut [cut==T],  name = (png_network %v% 'vertex.names')[cut==T], 
                                  guide = (png_network %v% 'Guidance')[cut==T]) 
  
  for(i in 1:nrow(cutpoints_actions)) {
    cut_points_m = c(p_g_s[[1]][1], p_g_s[[1]][2], p_g_s[[1]][3], cutpoints_actions$name[i])
    df_cut_points = rbind(df_cut_points, cut_points_m)
  }
} 

write.csv(all_contingency, "ct.csv")

colnames(df_global) <- c('Participant', 'Guidance', 'Session','Centralization', 'Density')
colnames(df_cut_points) <- c('Participant', 'Guidance', 'Session','Actions')
print(df_global)
write.csv(df_global, "df_global.csv", row.names=FALSE)
write.csv(df_cut_points, "df_cut_points.csv", row.names=FALSE)

##### Part 2##############
#########################
con_print_names =c() # ADD: name of users with confident metrics, for example., '62501123_g_1_'
incon_print_names =c() # ADD: name of users with inconfident metrics, for example., '62501123_g_1_'
graph_names <- c(con_print_names, incon_print_names)
all_nodes <- c('a_v1', 'a_f1', 'a_f2', 'a_n1', 'a_f3', 'b_v1', 'b_n1', 'b_c1', 'b_f1', 'b_f2', 'b_f3', 'b_f4', 'b_f5',
               'b_f6', 'b_f7', 'c_v1', 'c_n1', 'c_f1', 'c_f2', 'c_f3', 'c_f4', 'd_a', 'd_b', 'd_c')
# plot selected graphs
for (x in 1:length(all_names)){
  if (all_names[x] %in% graph_names)
  {
  png_nodes <- as.data.frame(do.call(cbind, png_nodes_files[x]))
  png_edges <- as.data.frame(do.call(cbind, png_edges_files[x]))
  
  existing_nodes <- list(png_nodes$Node)
  
  # Add non-connected nodes to the list of nodes and edges
  for (n in 1:length(all_nodes)){
    if (!(all_nodes[n] %in% existing_nodes[[1]])){
      png_nodes[nrow(png_nodes) + 1,] <- c(all_nodes[n], 0, toupper(substr(all_nodes[n], 1, 1)),  'NA', 100)
      png_edges[nrow(png_edges) + 1,] <- c(all_nodes[n], all_nodes[n], 0)
    }
  }
  
  # order lists by name
  png_nodes <- png_nodes[order(png_nodes$Node),]
  png_edges <- png_edges[order(png_edges$Source),]
  
  row.names(png_nodes) <- NULL
  row.names(png_edges) <- NULL
  
  # Extract Node attributes
  times <- png_nodes$Time
  clusters <- png_nodes$Cluster
  nodes <- png_nodes$Node
  opacities <- png_nodes$Opacity
  actions <- png_nodes$Action.Type
  
 
  # Set Cluster color palette 
  cluster_colours <- c('#fbb4ae',  '#b3cde3',  '#ccebc5', '#decbe4')
  names(cluster_colours) <-  (unique(clusters))

  list_c = c()
  list_c['a'] = 'A'
  list_c['b'] = 'B'
  list_c['c'] = 'C'
  list_c['d'] = 'D'
  
  # Extract Edge attribute (Color)
  png_edges$EdgeColor <- with(png_edges,
                              ifelse(substr(png_edges$Source,1,1) != substr(png_edges$Target,1,1), 'gray',
                                     ifelse(substr(png_edges$Source,1,1) == "a", '#fbb4ae',
                                            ifelse(substr(png_edges$Source,1,1) == "b", '#b3cde3',
                                                   ifelse(substr(png_edges$Source,1,1) == "c",'#ccebc5', '#decbe4')))))
  png_edges$Frequency <- as.numeric(png_edges$Frequency)
  
  # Construct Network
  png_network <- network(png_edges, directed = T, matrix.type = "edgelist", loops=TRUE)
  
  # Set Node attributes
  network::set.vertex.attribute (png_network, 'Time', as.numeric(times))
  network::set.vertex.attribute (png_network, 'Cluster', as.character(clusters))
  network::set.vertex.attribute (png_network, 'Action', as.character(actions))
  network::set.vertex.attribute (png_network, 'Opacity', as.numeric(opacities))
  
  # Add adjusted frequency attribute 1-3 to plot
  edge_frequencies <- get.edge.value(png_network,'Frequency')
  adjusted_Frequency <- rescale(as.numeric(edge_frequencies), to=c(1,3))
  network::set.edge.attribute(png_network,'Adjusted_Freq', adjusted_Frequency)
  
  # Plot and save network graphs in two separate folders, conf vs. inconf
  if (all_names[x] %in% con_print_names) {
    ggnet2 (png_network,  arrow.size = 8, arrow.gap = 0.035, node.color = 'Cluster',  
            color.palette = cluster_colours, node.alpha = 'Opacity', 
            edge.color = 'EdgeColor', edge.size = "Adjusted_Freq", label.size=6,
            mode = "circle", label = TRUE, node.size = 20) +
      guides(color = FALSE, size = FALSE)
    f_plot <- paste(all_names[x] , ".png", sep="")
    ggsave(path = "data/confident/", filename = f_plot)

  }
  
  if (all_names[x] %in% incon_print_names) {
    ggnet2 (png_network,  arrow.size = 8, arrow.gap = 0.035, node.color = 'Cluster',  
            color.palette = cluster_colours, node.alpha = 'Opacity', 
            edge.color = 'EdgeColor',  edge.size = "Adjusted_Freq",  label.size=6,
            mode = "circle", label = TRUE, node.size = 20) +
      guides(color = FALSE, size = FALSE)
    
    f_plot <- paste(all_names[x] , ".png", sep="")
    ggsave(path = "data/inconfident/", filename = f_plot)
    
  }
  }
} 

