import random
from .matrix_utilities import bin_mat_rref, bin_mat_dot, identity


class BinaryCoder(object):
    """ Network Coding class allowing for operations on binary field.

    Performance is sacrified by keeping to python data types.
    However, this allows for a much more simple implementation which can be easily undestood.
    """
    
    NUM_D_TYPE = int # The datatype of underlying numpy arrays

    def __init__(self, num_symbols, packet_size, rng_seed):
        self.num_symbols = num_symbols
        self.num_bit_packet = packet_size
        self.random = random.Random()
        self.random.seed(rng_seed)
        self.reset()

    def reset(self):
        self.num_independent = 0
        self.symbol_decoded = [False] * self.num_symbols
        self.id = identity(self.num_symbols)
        # Add identity to track transformation of rref
        # See: https://stackoverflow.com/questions/43495305/transformation-matrix-of-reduced-row-echelon-form
        self.coefficient_matrix = [ [0] * self.num_symbols + self.id[k] for k in range(self.num_symbols)] # save current rref to reduce computational load in the future
        self.packet_vector = [ [0] * self.num_bit_packet  for _ in range(self.num_symbols)]

    def is_symbol_decoded(self, index):
        """Returns the decoding status for a given symbol at index."""
        return self.symbol_decoded[index]

    def get_decoded_symbol(self, index):
        """Returns the symbol if already decoded, otherwise returns None."""
        symbol = None
        if self.is_symbol_decoded(index):
            symbol = self.packet_vector[index, :]
        return symbol

    def get_num_decoded(self):
        return sum(self.symbol_decoded)

    def is_fully_decoded(self):
        """Returns true, if all symbols are decoded."""
        return all(self.symbol_decoded)

    def rank(self):
        """Returns current rank of the coefficient matrix."""
        return self.num_independent

    def consume_packet(self, coefficients, packet):
        """Processes an encoded symbol together with its coefficients."""
        if not self.is_fully_decoded():
            # add new symbol to decoder matrix and packet vector
            self.coefficient_matrix[self.num_independent][0:self.num_symbols] = coefficients
            self.packet_vector[self.num_independent] = packet
            # calculate row reduced echolon form
            extended_rref, self.num_independent, self.symbol_decoded = bin_mat_rref(self.coefficient_matrix)
            # extract transformation matrix
            transformation = [row[self.num_symbols:2*self.num_symbols] for row in extended_rref]
            # apply transformation to the packet vector as well
            self.packet_vector = bin_mat_dot(transformation,self.packet_vector)
            # extract rref matrix
            rref = [row[0:self.num_symbols] for row in extended_rref]
            # construct new extended coefficient matrix
            self.coefficient_matrix = [rref[k] + self.id[k] for k in range(self.num_symbols)]

    def get_sys_coded_packet(self, index):
        """Returns an uncoded packet, if symbol was already decoded."""
        if self.is_symbol_decoded(index):
            coefficients = [0] * self.num_symbols
            coefficients[index] = 1
            packet = self.packet_vector[index, :]
        else:
            coefficients = None
            packet = None
        return coefficients, packet

    def get_new_coded_packet(self):
        """Select a random number of rows of the coefficient matrix and return the XOR of the associated packets and coefficients."""
        coefficients = [0] * self.num_symbols
        # "lazy-ensure" that coefficient vector is not all zeros (equal to empty information)
        while sum(coefficients) == 0:
            random_num = self.random.randint(0,self.num_independent)
            random_decisions = self.random.choices(range(self.num_independent), k=random_num)
            coefficients = [0] * self.num_symbols
            for k in range(self.num_symbols):                       
                coefficients[k] = sum([self.coefficient_matrix[selected][k] for selected in random_decisions])%2
            packet = [0] * self.num_bit_packet
            for l in range(self.num_bit_packet):
                packet[l] = sum([self.packet_vector[selected][l] for selected in random_decisions])%2
        return coefficients, packet