# MAZE
MAZE is a set of tools for simulating network paths using a variety of different possible routing methods for each hop. The same network hop can be modeled and simulated to go through either a LEO satellite constellation(i.e. Starlink, Kuiper, Lightspeed, etc), conventional fiber infrastructure, etc. In addition to this, MAZE allows you to simulate hybrid network paths where some network hops go through one network(i.e. Starlink) and some go through a different network(i.e. Fiber). MAZE works by essentially acting as a high level manager of sub-simulators, deciding what sub-simulator to simulate a network hop through and delegating the simulation job.


There are two parts:

 * `rtt_simulator`: A python framework for creating mixed network simulations. Currently, only LEO satellite networks and fiber networks are implemented, with LEO network hops being simulated using the subsimulator Hypatia(https://github.com/snkas/hypatia), and Fiber routes being simulated using knowledge of real world ping times. MAZE can be modified to support a variety of other network types(i.e. LTE) by simply choosing a subsimulator and integrating it into MAZE by implementing a new NetworkSimulator child class. The framework provides all the building blocks needed to write mixed network simulators with both ground and LEO space components for different situations(license: MIT)
 
  * `tools`: A set of python tools used for the University of Oregon's research into how the internet can be made more resilient in the event of natural disasters that damage routing infrastructure. `pnw_rtt` is a tool that can perform simulations of mixed networks along the west coast and provide estimated Round Trip Times of such networks(license: MIT)
