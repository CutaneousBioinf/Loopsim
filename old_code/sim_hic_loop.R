loop <- read.table("merged_5K_10K.loop")
chr_rg <- read.table("chr_region_hg19")

sim_loop <- function(loop) {
  out_loop <- data.frame(matrix(ncol = 6, nrow = nrow(loop)))
  colnames(out_loop) <- c("V1", "V2", "V3", "V4", "V5", "V6")
  for (i in 1:nrow(loop)) {
    if (i > 1) {
      dist <- loop[i, "V2"] - loop[(i - 1), "V2"]
      chr <- loop[i, "V1"]
      ran <- chr_rg[chr_rg$V1 == chr, 3]
      len <- loop[i, "V5"] - loop[i, "V2"]
      if (loop[i, "V1"] == loop[(i - 1), "V1"] & dist < 1e6 & (out_loop[(i - 1), "V3"] + dist) < ran & (out_loop[(i - 1), "V3"] + dist + len) < ran) {
        out_loop[i, 1] <- out_loop[i - 1, 1]
        out_loop[i, 2] <- out_loop[i - 1, 2] + dist
        out_loop[i, 3] <- out_loop[i - 1, 3] + dist
        out_loop[i, 4] <- out_loop[i - 1, 4]
        out_loop[i, 5] <- out_loop[i - 1, 2] + dist + len
        out_loop[i, 6] <- out_loop[i - 1, 3] + dist + len
      } else {
        chr <- loop[i, "V1"]
        res <- loop[i, "V3"] - loop[i, "V2"]
        len <- loop[i, "V5"] - loop[i, "V2"]
        ran <- chr_rg[chr_rg$V1 == chr, 3]
        end1 <- sample((1 + res / 2):(ran - res / 2 - len), 1)
        end2 <- end1 + len
        out_loop[i, 1] <- chr
        out_loop[i, 2] <- end1 - res / 2
        out_loop[i, 3] <- end1 + res / 2
        out_loop[i, 4] <- chr
        out_loop[i, 5] <- end2 - res / 2
        out_loop[i, 6] <- end2 + res / 2
      }
    } else {
      chr <- loop[i, "V1"]
      res <- loop[i, "V3"] - loop[i, "V2"]
      len <- loop[i, "V5"] - loop[i, "V2"]
      ran <- chr_rg[chr_rg$V1 == chr, 3]
      end1 <- sample((1 + res / 2):(ran - res / 2 - len), 1)
      end2 <- end1 + len
      out_loop[i, 1] <- chr
      out_loop[i, 2] <- end1 - res / 2
      out_loop[i, 3] <- end1 + res / 2
      out_loop[i, 4] <- chr
      out_loop[i, 5] <- end2 - res / 2
      out_loop[i, 6] <- end2 + res / 2
    }
  }
  return(out_loop)
}

loop_sim <- sim_loop(loop)
write.table(loop_sim, "sim_loop.txt", row.names = F, col.names = F, quote = F)
