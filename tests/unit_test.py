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


if __name__ == '__main__':
    unittest.main(verbosity=2)
