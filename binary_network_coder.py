import numpy as np
import sympy as sp
from matrix_utilities import binary_mat_rank


class BinaryCoder(object):
    """ Network Coding class allowing for operations on binary field.

    Performance is sacrified by keeping to python, numpy and sympy data types.
    However, this allows for a much more simple implementation which can be easily undestood.
    """
    
    NUM_D_TYPE = int # The datatype of underlying numpy arrays

    def __init__(self, num_symbols, packet_size):
        self.num_symbols = num_symbols
        self.num_bit_packet = packet_size
        self.reset()

    def reset(self):
        self.num_independent = 0
        self.symbol_decoded = [False] * self.num_symbols
        self.coefficient_matrix = np.zeros((self.num_symbols, self.num_symbols), dtype=self.NUM_D_TYPE)
        self.packet_vector = np.zeros((self.num_symbols, self.num_bit_packet), dtype=self.NUM_D_TYPE)
        self.might_need_solving = False
        # Add identity to track transformation of rref
        # See: https://stackoverflow.com/questions/43495305/transformation-matrix-of-reduced-row-echelon-form
        self.aug_coefficient_matrix = sp.Matrix(np.concatenate((self.coefficient_matrix, np.eye(self.num_symbols)), axis=1)).applyfunc(sp.nsimplify)

    def is_symbol_decoded(self, index):
        """Returns the decoding status for a given symbol at index."""
        return self.symbol_decoded[index]

    def get_decoded_symbol(self, index):
        """Returns the symbol if already decoded, otherwise returns None."""
        symbol = None
        if self.is_symbol_decoded(index):
            symbol = self.packet_vector[index, :]
        return symbol

    def is_fully_decoded(self):
        """Returns true, if all symbols are decoded."""
        return all(self.symbol_decoded)

    def seen_encoded_symbols(self):
        """Checks if a specifiy symbol was included in some of the already received encoded symbols."""
        return [np.sum(self.coefficient_matrix, 0) > 0]

    def rank(self):
        """Returns current rank of the coefficient matrix."""
        return self.num_independent

    def consume_packet(self, coefficients, packet):
        """Processes an encoded symbol together with its coefficients."""
        # heuristically add new symbol if not already finished
        if not self.is_fully_decoded():
            self.coefficient_matrix[self.num_independent, :] = coefficients
            # new packet increased coefficient matrix rank
            if binary_mat_rank(self.coefficient_matrix) > self.num_independent:
                # Accept new packet
                self.aug_coefficient_matrix[:,0:self.num_symbols] = self.coefficient_matrix
                self.packet_vector[self.num_independent, :] = packet
                self.num_independent += 1
                self.might_need_solving = True
            else:
                # packet is linear combination, we have to remove it again
                self.coefficient_matrix[self.num_independent, :] = np.zeros((1, self.num_symbols), dtype=self.NUM_D_TYPE)


    def solve(self):
        # we can only (partially) solve if a packet increased the rank of the coefficients matrix
        if self.might_need_solving:
            self.might_need_solving = False # consume flag
            extended_rref, _ = self.aug_coefficient_matrix.rref() # solve
            transformation = extended_rref[:, self.num_symbols:2*self.num_symbols] # pick out transformation matrix from solved augmented matrix
            scaler = transformation.det().q # since sympy.rref() works on floats, we need to convert to ints again using the smallest denominator

            if scaler % 2 != 0: # We can't use even scalers as it would break the mod 2
                transformation = transformation*scaler # Remove normailization to get to ints
                transformation = np.array(transformation.tolist(), dtype=self.NUM_D_TYPE) # switch from sympy to numpy
                rref = (transformation@self.coefficient_matrix) % 2 # appyl the same transformation to the coefficient matrix which was used to generate the rref
                
                self.symbol_decoded = [np.count_nonzero(rref[row_id, :]) == 1 for row_id in range(self.num_symbols)] # check if we succesfully decoded a symbol
                self.coefficient_matrix = rref # save current rref to reduce computational load in the future
                self.packet_vector = (transformation@self.packet_vector) % 2 # apply transformation to the packet vector as well
                self.aug_coefficient_matrix[:,0:self.num_symbols] = self.coefficient_matrix # update aug method so that we don't need to construct it every iteration

    def get_sys_coded_packet(self, index):
        """Returns a uncoded packet, if symbol was already decoded."""
        if self.is_symbol_decoded(index):
            coefficients = np.zeros((self.num_symbols,), dtype=self.NUM_D_TYPE)
            coefficients[index] = 1
            packet = self.packet_vector[index, :]
        else:
            coefficients = None
            packet = None
        return coefficients, packet

    def get_new_coded_packet(self):
        """Select a random number of rows of the coefficient matrix and return the XOR of the associated packets and coefficients."""
        coefficients = 0
        # "lazy-ensure" that coefficient vector is not all zeros (equal to empty information)
        while np.sum(coefficients) == 0:
            to_be_included = [True] * self.num_symbols # default exclude all coefficients
            random_decisions = np.random.choice(a=[False, True], size=(1,self.num_independent,))[0]
            to_be_included[0:self.num_independent] = random_decisions # overide for already received coefficients
            coefficients = np.sum(self.coefficient_matrix[to_be_included], 0) % 2

        packet = np.sum(self.packet_vector[coefficients > 0], 0) % 2
        return coefficients, packet