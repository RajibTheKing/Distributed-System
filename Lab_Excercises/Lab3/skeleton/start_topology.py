# coding=utf-8
import argparse
import math
import random
import os
import signal
import mininet
from mininet.topo import Topo # Network topology
from mininet.net import Mininet # Mininet environment, simulator
from mininet.link import TCLink, TCIntf, Intf # Customisable links & interfaces
from mininet.log import setLogLevel, info # Logger
from mininet.term import makeTerm, cleanUpScreens # Open xterm from mininet
from mininet.cli import CLI # Command Line Interface


#------------------------------------------------------------------------------------------------------
# DistributedTopology - class inheriting from mininet.topo.Topo, defines the network topology
class DistributedTopology( Topo ):
    "Mininet network topology with distributed servers, based on a star topology"

    # Initialize variables
    def build(self, nb_of_servers, **opts):
        # local configuration parameters
        switch_to_server_rates = [50, 90, 95, 100, 115] # Mbps
        switch_to_server_losses = [0.00001, 0.00002, 0.00005, 0.0001] # 1e-5 up to 1e-4 PER
        switch_to_server_delays = [10, 15, 20, 25, 30] # ms, delay = RTT/2
        # internet configuration parameters
        switch_to_switch_rate = 1000 # Mbps
        switch_to_switch_losses = 0.00001 # 1e-5 PER
        switch_to_switch_delay = 50 # ms, delay = RTT/2
        # arrays
        sw = []
        srv = []
        # We create the network topology
        # We first add a central switch that connects regions; it emulates the Internet
        central_sw = self.addSwitch("s0")
        # For each region
        for srvID in range(1, nb_of_servers+1):
            # create a local switch
            sw.append(self.addSwitch("s{}".format(srvID)))
            # add the server
            srv.append(self.addHost("server{}".format(srvID),
                                    ip=("10.1.0.{}/24".format(srvID))))
            # link server to switch
            self.addLink(sw[srvID-1],
                         srv[srvID-1],
                         bw = random.choice(switch_to_server_rates),
                         loss = random.choice(switch_to_server_losses),
                         delay = "{}ms".format(random.choice(switch_to_server_delays)))
            # connect the regional switch to the central switch
            self.addLink(central_sw,
                         sw[srvID-1],
                         bw=switch_to_switch_rate,
                         loss=switch_to_switch_losses,
                         delay="{}ms".format(switch_to_switch_delay))
#------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------
class Lab():


    def __init__(self, nb_of_servers, path_to_server_code):
        self.nb_of_servers = nb_of_servers
        self.path_to_server_code = path_to_server_code
        self.server_IPs = []
        for srv in range(1,self.nb_of_servers+1):
            self.server_IPs.append("10.1.0.{}".format(srv))


    # Open an xterm and launch a specific command
    def startServer(self, server):
        return makeTerm(node=server,
                        cmd="python {} --id {} --servers {}".format(self.path_to_server_code,
                                                             server.IP().replace('10.1.0.',''),
                                                             ','.join(self.server_IPs)))


    def run(self):
        '''Run the simulation environment'''
        # We create the topology
        topology = DistributedTopology(self.nb_of_servers)
        # We create the simulation
        # Set the topology, the class for links and interfaces, the mininet environment must be cleaned up before launching, we should build now the topology
        simulation = Mininet(topo=topology,
                             link=TCLink,
                             intf=TCIntf,
                             cleanup=True,
                             build=True,
                             ipBase='10.1.0.0/24')
        # We connect the network to Internet
        simulation.addNAT().configDefault()
        terms = []
        # We can start the simulation
        print "Starting the simulation..."
        simulation.start()
        for srv in simulation.hosts:
            if "server" in srv.name:
                # We open a xterm and start the server
                terms.append(self.startServer(srv)[0])
        # We also start the Command Line Interface of Mininet
        CLI(simulation)
        # Once the CLI is closed (with exit), we can stop the simulation
        print "Stopping the simulation NOW!"
        # We close the xterms (mininet.term.cleanUpScreens)
        cleanUpScreens()
        for term in terms:
            os.kill(term.pid, signal.SIGKILL)
        simulation.stop()


#------------------------------------------------------------------------------------------------------
# If the script was directly launched (and that should be the case!)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a distributed system. Launches a Mininet environment composed of multiple servers running your implementation of the lab.')
    parser.add_argument('--nb-servers',
                        nargs='?',
                        dest='nb_srv',
                        default=8,
                        type=int,
                        help='The number of servers that should be running. Default is 8.')
    parser.add_argument('--script',
                        nargs='?',
                        dest='pth_srv',
                        default='server/server.py',
                        help='The relative path to your server implementation. Default is ./server/server.py')
    args = parser.parse_args()
    nb_of_servers =int(args.nb_srv)
    server_path = args.pth_srv

    lab = Lab(nb_of_servers, server_path)
    lab.run()
#------------------------------------------------------------------------------------------------------