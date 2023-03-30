loop <- read.table("pcHiC_loops", header = T)
chr_rg <- read.table("chr_region_hg19")
sim_loop_pchic <- function(loop) {
  loop <- loop[, 4:6]
  out_loop <- data.frame(matrix(ncol = 3, nrow = nrow(loop)))
  colnames(out_loop) <- c("V1", "V2", "V3")
  for (i in 1:nrow(loop)) {
    if (i > 1) {
      dist <- loop[i, "V5"] - loop[(i - 1), "V5"]
      chr <- loop[i, "V4"]
      res <- loop[i, "V6"] - loop[i, "V5"]
      ran <- chr_rg[chr_rg$V1 == chr, 3]
      if (loop[i, "V4"] == loop[(i - 1), "V4"] & dist < 1e6 & (out_loop[(i - 1), "V3"] + dist) < ran) {
        out_loop[i, 1] <- out_loop[i - 1, 1]
        out_loop[i, 2] <- out_loop[i - 1, 2] + dist
        out_loop[i, 3] <- out_loop[i, 2] + res
      } else {
        chr <- loop[i, "V4"]
        res <- loop[i, "V6"] - loop[i, "V5"]
        ran <- chr_rg[chr_rg$V1 == chr, 3]
        end <- sample((1 + res / 2):(ran - res / 2), 1)
        out_loop[i, 1] <- chr
        out_loop[i, 2] <- end - res / 2
        out_loop[i, 3] <- end + res / 2
      }
    } else {
      chr <- loop[i, "V4"]
      res <- loop[i, "V6"] - loop[i, "V5"]
      ran <- chr_rg[chr_rg$V1 == chr, 3]
      end <- sample((1 + res / 2):(ran - res / 2), 1)
      out_loop[i, 1] <- chr
      out_loop[i, 2] <- end - res / 2
      out_loop[i, 3] <- end + res / 2
    }
  }
  return(out_loop)
}
