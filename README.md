# Observing bandwidth consumption between containers under various network modes
I found that an application within a container environment poorly performs with reduced communication bandwidth, not leveraing the physical limit of a hosting mahcine bandwidth resources. This repository provides experimental data for seeing how the in-between docker-based container communication bandwidth changes using the iperf3.
iperf3's client and server are deployed over the following environments. For two different machines A and B:
- Local:  A <-->  A // 34.7 Gbits/sec
- No Container: A <--> B // 9.22 Gbits/sec
- Host Network: A <--> B // 9.19 Gbits/sec
- Overlay Network: A <--> B // 1.49 Gbits/sec
- Bridge Network: A <--> B // 8.53 Gbits/sec