I observed that an application running in a containerized environment exhibits suboptimal performance due to reduced communication bandwidth, failing to fully utilize the physical bandwidth capacity of the host machine. This repository provides experimental data showcasing how communication bandwidth between Docker-based containers varies under different configurations, using iperf3 as the benchmarking tool. The client and server instances of iperf3 were deployed in the following environments across two distinct machines, A and B:

- Local: A <--> A // 34.7 Gbits/sec
- No Container: A <--> B // 9.22 Gbits/sec
- Host Network: A <--> B // 9.19 Gbits/sec
- Overlay Network: A <--> B // 1.49 Gbits/sec
- Bridge Network: A <--> B // 8.53 Gbits/sec
