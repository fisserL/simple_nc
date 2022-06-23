import random
import time
from simplenc import BinaryCoder

if __name__ == "__main__":
    ## Parameter
    num_symbols = 4
    num_bit_packet = 5
    rng_seed = 1
    print_packets = False
    print_decoding_process = False

    ## Initialization
    random.seed(rng_seed)

    encoder = BinaryCoder(num_symbols, num_bit_packet, rng_seed)
    decoder = BinaryCoder(num_symbols, num_bit_packet, rng_seed)

    # initalize encoder with random bit packets
    for packet_id in range(encoder.num_symbols):
        # create a random packet with random bits
        packet = random.getrandbits(encoder.num_bit_packet)
        packet = [packet >> i & 1 for i in range(encoder.num_bit_packet - 1,-1,-1)]
        # create an encoding vector
        coefficients = [0] * encoder.num_symbols
        # set the symbolic bit
        coefficients[packet_id] = 1
        # add packet to encoder
        encoder.consume_packet(coefficients, packet)

    print(f"# Setup complete.")
    if print_packets:
        print(f"## Encoder packets: \n{encoder.packet_vector}.")
        print(f"## Decoder packets: \n{decoder.packet_vector}.")

    ## Start
    # add new coded packet until system fully decoded
    necessary_messages = 0
    print(f"\n# Running scenario with {num_symbols} symbols and packets of size {num_bit_packet} ...\n")

    tic = time.time()
    while not decoder.is_fully_decoded():
        # create new encoded packet
        coefficient, packet = encoder.get_new_coded_packet()
        # add packet to decoder
        decoder.consume_packet(coefficient, packet)
        necessary_messages += 1
        # (partially) solve
        if print_decoding_process:
            print(f"## Progress: Already decoded {decoder.get_num_decoded()} out of {decoder.num_symbols}.")
    
    print(f"\n# Finished !!!")

    if decoder.packet_vector == encoder.packet_vector:
        ## Stats
        
        print(f"## Succesfully decoded all packets at the receiver after {necessary_messages} messages.")
        print(f"## Whole process took %.2f ms." % ((time.time()-tic)*1000))
        if print_packets:
            print(f"## Encoder packets: \n{encoder.packet_vector}.")
            print(f"## Decoder packets: \n{decoder.packet_vector}.")
    else:
        print(f"## Error, decoded packet vectors are not equal!!!")
        raise ValueError

    
