library(ggplot2)
library(cowplot)
library(gridExtra)
library(optparse)

option_list <- list( 
    make_option(c("-i", "--input"),
                help="input filename"),
    make_option(c("-o", "--output"), 
                help="output filename")
)

opt <- parse_args(OptionParser(option_list=option_list))

df <- read.table(opt$input, header = TRUE)

df.plot <- subset(df, Num > 1000 & P_values < 0.05)

df.plot$Specific <- ifelse(df.plot$TF_Activity>0, "Cardiac", "hESC")

p <- ggplot(df.plot, aes(x = reorder(Motif, TF_Activity), y = TF_Activity, fill = Specific)) +
    geom_bar(stat = "identity")+
    coord_flip() +
    xlab("Motifs") +
    ylab("TF activity change") +
    theme_cowplot() +
    theme(legend.title = element_blank())

pdf(file = opt$output, width = 6, height = 6)
print(p)
dev.off()
