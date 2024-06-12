d <- readRDS('sh.gb.from.all.regions.rda')
write.csv(d, file='sh_gb.csv')

d <- readRDS('sh.seoul.from.all.regions.rda')
write.csv(d, file='sh_sl.csv')

d <- readRDS('skt.gb.from.all.regions.rda')
write.csv(d, file='skt_gb.csv')

d <- readRDS('skt.seoul.from.all.regions.rda')
write.csv(d, file='skt_sl.csv')
