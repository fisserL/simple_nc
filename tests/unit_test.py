#!/usr/bin/python3

import unittest
import simplenc

class TestMatrixOperators(unittest.TestCase):
    """Tests the matrix utilities necessary for the BinaryCoder."""

    def setUp(self):
        pass

    def test_rref(self):
        tests = self.get_rref_test_cases()
        for test in tests:
            input = test["input"]
            num_symbols = len(input[0])
            identity = simplenc.identity(num_symbols)
            extended_matrix = [input[k] + identity[k] for k in range(num_symbols)]
            extended_rref, rank, is_decoded = simplenc.bin_mat_rref(extended_matrix)
            rref = [row[0:num_symbols] for row in extended_rref]
            self.assertEqual(rref, test["solution_rref"])
            self.assertEqual(rank, test["solution_rank"])
            self.assertEqual(is_decoded, test["solution_is_decoded"])

    def test_identity(self):
        test = self.get_identity_test_cases()
        self.assertEqual(simplenc.identity(
            test["input"]), test["solution_mat"])

    def get_identity_test_cases(self):
        test = {"input": 3,
                "solution_mat": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}
        return test

    def get_rref_test_cases(self):
        tests = []
        # identity should remain as identity
        tests.append({"input": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                      "solution_rref": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                      "solution_rank": 3,
                      "solution_is_decoded": [True, True, True]})

        # First row should be reduced
        tests.append({"input": [[1, 1, 1], [0, 1, 0], [0, 0, 1]],
                      "solution_rref": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                      "solution_rank": 3,
                      "solution_is_decoded": [True, True, True]})

        # First & second row should be reduced
        tests.append({"input": [[1, 1, 1], [0, 1, 1], [0, 0, 1]],
                      "solution_rref": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                      "solution_rank": 3,
                      "solution_is_decoded": [True, True, True]})

        # First & second row should be reduced regardless of order
        tests.append({"input": [[0, 0, 1], [0, 1, 1], [1, 1, 1]],
                      "solution_rref": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                      "solution_rank": 3,
                      "solution_is_decoded": [True, True, True]})

        # underdetermined systesm should still be reduced
        tests.append({"input": [[0, 0, 0], [0, 1, 1], [1, 1, 1]],
                      "solution_rref": [[1, 0, 0], [0, 1, 1], [0, 0, 0]],
                      "solution_rank": 2,
                      "solution_is_decoded": [True, False, False]})
        return tests


class TestBinaryCoder(unittest.TestCase):
    """Tests the BinaryCoder."""

    def setUp(self):
        pass

    def test_coding(self):
        tests = self.get_coding_test_cases()

        for test in tests:
            rng_seed = 1
            # Encoder
            num_symbols = len(test["inputs"][0][0])
            num_bits_packet = len(test["inputs"][0][1])
            encoder = simplenc.BinaryCoder(num_symbols, num_bits_packet, rng_seed)
            for inputs in test["inputs"]:
                encoder.consume_packet(inputs[0],inputs[1])
            self.assertEqual(encoder.rank(),test["solution_rank"])
            self.assertEqual(encoder.get_num_decoded(),test["solution_num_decoded"])
            self.assertEqual(encoder.is_fully_decoded(),test["solution_is_fully_decoded"])
            self.assertEqual(encoder.get_decoded_symbol(0),test["solution_first_decoded_packet"])
            self.assertEqual(encoder.get_sys_coded_packet(0),test["solution_first_sys_encoded_packet"])

            # Decoder
            decoder = simplenc.BinaryCoder(num_symbols, num_bits_packet, rng_seed)
            for _ in range(15): # TODO: Magic number
                decoder.consume_packet(*(encoder.get_new_coded_packet()))
            self.assertEqual(encoder.rank(),test["solution_rank"])
            self.assertEqual(decoder.get_num_decoded(),test["solution_num_decoded"])
            self.assertEqual(decoder.is_fully_decoded(),test["solution_is_fully_decoded"])

            # Check encoder and decoder states
            self.assertEqual(decoder.packet_vector,encoder.packet_vector)


    def get_coding_test_cases(self):
        tests = []

        # An encoder with all symbols fully decoded should create packets for all symbosl
        tests.append({"inputs":[ ([1, 0, 0], [1, 1, 1]), 
                                 ([0, 1, 0], [1, 1, 0]),
                                 ([0, 0, 1], [1, 0, 1])],
                      "solution_num_decoded": 3,
                      "solution_rank": 3,
                      "solution_first_decoded_packet": [1, 1, 1],
                      "solution_first_sys_encoded_packet": ([1, 0, 0],[1, 1, 1]),
                      "solution_is_fully_decoded": True})

        tests.append({"inputs":[ ([1, 1, 1], [1, 1, 1]), 
                                 ([0, 1, 1], [1, 1, 0])],
                      "solution_num_decoded": 1,
                      "solution_rank": 2,
                      "solution_first_decoded_packet": [0, 0, 1],
                      "solution_first_sys_encoded_packet": ([1, 0, 0],[0, 0, 1]),
                      "solution_is_fully_decoded": False})

        tests.append({"inputs":[ ([1, 1, 1], [1, 1, 1]), 
                                 ([0, 0, 1], [1, 1, 0])],
                      "solution_num_decoded": 1,
                      "solution_rank": 2,
                      "solution_first_decoded_packet": None,
                      "solution_first_sys_encoded_packet": (None, None),
                      "solution_is_fully_decoded": False})

        tests.append({"inputs":[ ([1, 1, 1], [1, 1, 1]), 
                                 ([0, 0, 1], [1, 1, 0]),
                                 ([0, 0, 1], [1, 1, 0])],
                      "solution_num_decoded": 1,
                      "solution_rank": 2,
                      "solution_first_decoded_packet": None,
                      "solution_first_sys_encoded_packet": (None, None),
                      "solution_is_fully_decoded": False})
        return tests
