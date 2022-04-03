import numpy as np
import time
from binary_network_coder import BinaryCoder

if __name__ == "__main__":
    ## Parameter
    num_symbols = 4
    num_bit_packet = 5
    rng_seed = 1
    print_packets = False

    ## Initialization
    np.random.seed(rng_seed)

    encoder = BinaryCoder(num_symbols, num_bit_packet)
    decoder = BinaryCoder(num_symbols, num_bit_packet)

    # initalize encoder with random bit packets
    for packet_id in range(encoder.num_symbols):
        # create a random packet with random bits
        packet = np.random.randint(0, 2, (1, encoder.num_bit_packet))
        # create an encoding vector
        coefficients = np.zeros((encoder.num_symbols,), dtype=encoder.NUM_D_TYPE)
        # set the symbolic bit
        coefficients[packet_id] = 1
        # add packet to encoder
        encoder.consume_packet(coefficients, packet)
    encoder.solve() # for good measures

    print(f"# Setup complete.")
    if print_packets:
        print(f"## Encoder packets: \n{encoder.packet_vector}.")
        print(f"## Decoder packets: \n{decoder.packet_vector}.")

    ## Start
    # add new coded packet until system fully decoded
    necessary_messages = 0
    print(f"\n# Running scenario with {num_symbols} symbols and packets of size {num_bit_packet} ...")

    tic = time.time()
    while not decoder.is_fully_decoded():
        # create new encoded packet
        coefficient, packet = encoder.get_new_coded_packet()
        # add packet to decoder
        decoder.consume_packet(coefficient, packet)
        necessary_messages += 1
        # (partially) solve
        decoder.solve()

    ## Stats
    print(f"# Finished !!!")
    print(f"## Succesfully decoded all packets at the receiver after {necessary_messages} messages.")
    print(f"## Whole process took %.2f ms." % ((time.time()-tic)*1000))
    if print_packets:
        print(f"## Encoder packets: \n{encoder.packet_vector}.")
        print(f"## Decoder packets: \n{decoder.packet_vector}.")

    
