# gssimulator
GSSimulator is a set of tools to simulate mixed ground-space networks. This is used to research how routing around damaged areas using LEO constellations could be used in disaster situations to prevent internet down time.

There are two parts:

 * `rtt_simulator`: A python framework for creating mixed network simulations built using the Hypatia(https://github.com/snkas/hypatia) LEO constellation simulator. There are three constellations automatically supported(Starlink, Kuiper, and Telesat), but more can be defined using the framework. The framework provides all the building blocks needed to write mixed network simulators with both ground and LEO space components for different situations(license: MIT)
 
  * `tools`: A set of python tools used for the University of Oregon's research into how the internet can be made more resilient in the event of natural disasters that damage routing infrastructure. `pnw_rtt` is a tool that can perform simulations of mixed networks along the west coast and provide estimated Round Trip Times of such networks(license: MIT)
