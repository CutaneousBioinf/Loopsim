library(data.table)
library(intervals)

loop <- read.table("merged_5K_10K.loop")
# updated function, output indices of overlapped psor loci as well
# use union of end intervals instead of ends
psor_loci <- function(loopfile) {
  uni_inter_out <- data.frame(matrix(ncol = 3, nrow = 0))
  colnames(uni_inter_out) <- c("V1", "V2", "V3")

  for (i in sort(unique(loopfile$V1))) {
    interval1 <- loopfile[loopfile$V1 == i, 2:3]
    colnames(interval1) <- c("V1", "V2")
    interval2 <- loopfile[loopfile$V1 == i, 5:6]
    colnames(interval2) <- c("V1", "V2")
    intervals <- rbind(interval1, interval2)
    idf <- Intervals(intervals)
    uni_inter <- as.data.frame(interval_union(idf))
    uni_inter <- as.data.frame(cbind(i, uni_inter))
    colnames(uni_inter) <- c("V1", "V2", "V3")
    uni_inter_out <- rbind(uni_inter_out, uni_inter)
  }

  ploci <- read.table("95_BCS_psor_loci")
  ploci$V1 <- gsub("chr", "", as.character(ploci$V1))
  ploci$V1 <- as.character(ploci$V1)

  ploci_ref <- data.table(chr = ploci$V1, start = ploci$V2, end = ploci$V3)
  setkey(ploci_ref, chr, start, end)

  loopfile_for_search <- data.table(chr = uni_inter_out$V1, start = uni_inter_out$V2, end = uni_inter_out$V3) # nolint
  print(loopfile_for_search)
  check <- foverlaps(loopfile_for_search, ploci_ref, type = "any", which = TRUE)
  # print(check)
  overlap_indice <- check[!is.na(check$yid), 1]$xid
  psor_indice <- unique(check$yid[!is.na(check$yid)])

  return(list(n_interval = nrow(uni_inter_out), n_overlap = length(overlap_indice), psor_indice = psor_indice)) # nolint
}

res <- psor_loci(loop)
print(res)
