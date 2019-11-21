from collections import *
import queue
import threading



## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.in_queue = queue.Queue(maxsize)
        self.out_queue = queue.Queue(maxsize)
    
    ##get packet from the queue interface
    # @param in_or_out - use 'in' or 'out' interface
    def get(self, in_or_out):
        try:
            if in_or_out == 'in':
                pkt_S = self.in_queue.get(False)
                # if pkt_S is not None:
                #     print('getting packet from the IN queue')
                return pkt_S
            else:
                pkt_S = self.out_queue.get(False)
                # if pkt_S is not None:
                #     print('getting packet from the OUT queue')
                return pkt_S
        except queue.Empty:
            return None
        
    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param in_or_out - use 'in' or 'out' interface
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, in_or_out, block=False):
        if in_or_out == 'out':
            # print('putting packet in the OUT queue')
            self.out_queue.put(pkt, block)
        else:
            # print('putting packet in the IN queue')
            self.in_queue.put(pkt, block)
            
        
## Implements a network layer packet.
class NetworkPacket:
    ## packet encoding lengths 
    dst_S_length = 5
    prot_S_length = 1
    
    ##@param dst: address of the destination host
    # @param data_S: packet payload
    # @param prot_S: upper layer protocol for the packet (data, or control)
    def __init__(self, dst, prot_S, data_S):
        self.dst = dst
        self.data_S = data_S
        self.prot_S = prot_S
        
    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()
        
    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst).zfill(self.dst_S_length)
        if self.prot_S == 'data':
            byte_S += '1'
        elif self.prot_S == 'control':
            byte_S += '2'
        else:
            raise('%s: unknown prot_S option: %s' %(self, self.prot_S))
        byte_S += self.data_S
        return byte_S
    
    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst = byte_S[0 : NetworkPacket.dst_S_length].strip('0')
        prot_S = byte_S[NetworkPacket.dst_S_length : NetworkPacket.dst_S_length + NetworkPacket.prot_S_length]
        if prot_S == '1':
            prot_S = 'data'
        elif prot_S == '2':
            prot_S = 'control'
        else:
            raise('%s: unknown prot_S field: %s' %(self, prot_S))
        data_S = byte_S[NetworkPacket.dst_S_length + NetworkPacket.prot_S_length : ]        
        return self(dst, prot_S, data_S)
    

    

## Implements a network host for receiving and transmitting data
class Host:
    
    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.intf_L = [Interface()]
        self.stop = False #for thread termination
    
    ## called when printing the object
    def __str__(self):
        return self.addr
       
    ## create a packet and enqueue for transmission
    # @param dst: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst, data_S):
        p = NetworkPacket(dst, 'data', data_S)
        print('%s: sending packet "%s"' % (self, p))
        self.intf_L[0].put(p.to_byte_S(), 'out') #send packets always enqueued successfully
        
    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.intf_L[0].get('in')
        if pkt_S is not None:
            print('%s: received packet "%s"' % (self, pkt_S))
       
    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return
        

## Implements a multi-interface router
class Router:
    
    ##@param name: friendly router name for debugging
    # @param cost_D: cost table to neighbors {neighbor: {interface: cost}}
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, cost_D, max_queue_size):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.intf_L = [Interface(max_queue_size) for _ in range(len(cost_D))]
        #save neighbors and interfeces on which we connect to them
        self.cost_D = cost_D    # {neighbor: {interface: cost}}
        #TODO: set up the routing table for connected hosts
        self.rt_tbl_D = {}
        self.cost_D_duplicate = cost_D
        self.rt_tbl_D = cost_D.copy()
        self.global_rt_tbl_D = defaultdict(dict)
        for key, value in self.cost_D_duplicate.items():
            for null, val in value.items():
                self.global_rt_tbl_D[name][key] = [val]
        self.cost_D.update({self.name: {0: 0}})
     
        for location, null in cost_D.items():
            for nil, item in cost_D[location].items():
                self.rt_tbl_D.update({location: {self.name: item}})
   




        print('%s: Initialized routing table' % self)
        self.print_routes()

    def return_ascii(self, str):
        return ord(str[1]) - ord(str[0])
        
    ## Print routing table
    def print_routes(self):
        # TODO: print the routes as a two dimensional table
        print("ROUTING TABLE FOR: " + self.name)

        col_items = set()
        for col_item in set(self.global_rt_tbl_D.keys()):
            col_items.update(self.global_rt_tbl_D[col_item].keys())

        col_items = sorted(col_items, key=self.return_ascii)


        for i in range(len(col_items)+1):
            print("╒══════", end="")
        print("╕")

        row = "| {}  |".format(self.name)
        for location in col_items:
            row += "  {} |".format(location)
        print(row)

        for i in range(len(col_items) + 1):
            print("╞══════", end="")
        print("|")

        column = ['RA', 'RB']

        item_info = ""

        for item in column:

            item_info += "| {}  |".format(str(item))


            for col in col_items:
                try:
                    item_info += "  {}  |".format(str(self.global_rt_tbl_D[item][col]).strip("[]"))
                except KeyError:
                    pass


            print(item_info)
            item_info = ""

        for i in range(len(col_items)+1):
            print("╘══════", end="")
        print("╛\n")






    ## called when printing the object
    def __str__(self):
        return self.name


    ## look through the content of incoming interfaces and 
    # process data and control packets
    def process_queues(self):
        for i in range(len(self.intf_L)):
            pkt_S = None
            #get packet from interface i
            pkt_S = self.intf_L[i].get('in')
            #if packet exists make a forwarding decision
            if pkt_S is not None:
                p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                if p.prot_S == 'data':
                    self.forward_packet(p,i)
                elif p.prot_S == 'control':
                    self.update_routes(p, i)
                else:
                    raise Exception('%s: Unknown packet type in packet %s' % (self, p))
            

    ## forward the packet according to the routing table
    #  @param p Packet to forward
    #  @param i Incoming interface number for packet p
    def forward_packet(self, p, i):

        intf = None

        try:
            # TODO: Here you will need to implement a lookup into the 
            # forwarding table to find the appropriate outgoing interface
            # for now we assume the outgoing interface is 1

            #GETS INTERFACE NUMBER FROM TABLE
            try:
                for location in self.rt_tbl_D[p.dst].items():
                    try:
                        intf = int(location[0])
                    except ValueError:
                        for item, val in self.cost_D_duplicate[p.dst].items():
                            intf = int(item)
                            #print("Got the interface!: " + str(intf))
                            break

            except KeyError:
                pass

            #print("INTERFACE USED: " + str(intf))

            self.intf_L[intf].put(p.to_byte_S(), 'out', True)
            print('%s: forwarding packet "%s" from interface %d to %d' % \
                (self, p, i, 1))
        except queue.Full:
            print('%s: packet "%s" lost on interface %d' % (self, p, i))
            pass


    ## send out route update
    # @param i Interface number on which to send out a routing update
    def send_routes(self, i):
        # TODO: Send out a routing table update
        #create a routing table update packet

        packet_encoded = "{}--.".format(self.name)

        item_list = self.rt_tbl_D.items()

        #print(item_list)

        for location, value in item_list:

            items = value.items()

            for intf, ncost in items:

                name = str(location)
                interface_name = str(intf)
                node_cost = str(ncost)

                packet_encoded += "{}-{}-{}-{}".format(name, interface_name, node_cost, "--")

        p = NetworkPacket(0, 'control', packet_encoded)
        try:
            print('%s: sending routing update "%s" from interface %d' % (self, p, i))
            self.intf_L[i].put(p.to_byte_S(), 'out', True)
        except queue.Full:
            print('%s: packet "%s" lost on interface %d' % (self, p, i))
            pass


    ## forward the packet according to the routing table
    #  @param p Packet containing routing information
    def update_routes(self, p, i):
        #TODO: add logic to update the routing tables and

        #print(p)
        continueRefresh = False
        fetch_info = p.data_S.split("--.")
        name = fetch_info[0]
        #print("NAME: " + name)
        # interface_name = ""
        for path in fetch_info[1].split("--"):
            if len(str(path)) > 0:
                path_details = path.split("-")
                count = 0
                for i in path_details:
                    if i == '':
                        #print(len(position))
                        if len(path_details) == 2:
                            del path_details

                        else:
                            del path_details[count]
                        break
                    else:
                        count = count + 1

                try:

                    self.global_rt_tbl_D[name][path_details[0]] = [int(path_details[2])]

                    if path_details[0] == self.name:


                        interface1 = list(self.cost_D_duplicate[name].keys())

                        self.rt_tbl_D[path_details[0]] = {int(interface1[0]): 0}

                        self.global_rt_tbl_D[self.name][path_details[0]] = [0]


                    if path_details[0] not in self.rt_tbl_D and path_details[0] not in self.cost_D_duplicate:


                        val1 = list(self.cost_D_duplicate[name].values())

                        interface2 = list(self.cost_D_duplicate[name].keys())

                        self.rt_tbl_D[path_details[0]] = {int(interface2[0]): int(path_details[2]) + val1[0]}

                        self.global_rt_tbl_D[self.name][path_details[0]] = [int(path_details[2]) + val1[0]]

                        continueRefresh = True

                    elif path_details[0] not in self.cost_D_duplicate and path_details[0] in self.rt_tbl_D:


                        val2 = list(self.cost_D_duplicate[name].values())

                        interface3 = list(self.cost_D_duplicate[name].keys())

                        val3 = list(self.rt_tbl_D[path_details[0]].values())

                        if val3[0] > int(val2[0]) + int(path_details[2]):

                            self.rt_tbl_D[path_details[0]] = {int(interface3[0]): int(path_details[2]) + val2[0]}

                            self.global_rt_tbl_D[self.name][path_details[0]] = [int(path_details[2]) + val2[0]]

                            continueRefresh = True


                except UnboundLocalError:
                    pass

                if continueRefresh:


                    for key, value in self.cost_D.items():

                        for inf, path_cost in value.items():

                            # if 'R' in key:
                            #     self.send_routes(inf)
                            if 'H' not in key:
                                self.send_routes(inf)








        # possibly send out routing updates
        #print('%s: Received routing update %s from interface %d' % (self, p, i))

                
    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.process_queues()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return 