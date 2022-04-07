
def bin_mat_rref(A):
    """"Extended from implementation of user iddo10: https://gist.github.com/StuartGordonReid/eb59113cb29e529b8105?permalink_comment_id=3268301#gistcomment-3268301 """
    B = []
    n = len(A[0])

    # forward sweep
    for col in range(n):
        num_cols = len(A)
        j = 0
        rows = []
        # precompute relevant rows
        while j < num_cols:
            if A[j][col] == 1:
                rows += [j]
            j += 1
        
        # process each row
        if len(rows) >= 1:
            for c in range(1, len(rows)):
                for k in range(n):
                    A[rows[c]][k] = (A[rows[c]][k] + A[rows[0]][k]) % 2
            B.append(A[rows[0]]) # Copy for backwards sweep
            A.pop(rows[0])

    n = len(B)
    nk = len(B[0])

    # backwards sweep
    for row in range(n-1,-1,-1):
        # check if the current row contains an identity leading 1
        if B[row][row] == 1:
            # subtract from all other rows which have a 1 at the current row index
            for to_reduce_row in range(row-1,-1,-1):
                if B[to_reduce_row][row] == 1:
                    for k in range(to_reduce_row,nk):
                        B[to_reduce_row][k] = (B[to_reduce_row][k]+B[row][k])%2

    symbol_cutoff = int(len(B[0])/2) # The cutoff where symbols end and the transformation starts   
    row_sums = [sum(row[0:symbol_cutoff]) for row in B]
    rank = sum([row_sum >= 1 for row_sum in row_sums])
    is_decoded = [row_sum == 1 for row_sum in row_sums]

    return B, rank, is_decoded


def bin_mat_dot(K, L):
    result = []
    num_rows = len(K)
    num_cols = len(K[0])
    num_bits = len(L[0])
    
    for row in range(num_rows):
        if sum(K[row])>1 or K[row][row]==0:
            row_solution =  [0]*num_bits
            for k in range(num_cols):
                if K[row][k]:
                    for j in range(num_bits):
                        row_solution[j] = (row_solution[j] + K[row][k]*L[k][j])%2
        else:
            row_solution = L[row]
        result.append(row_solution)
    return result


def identity(n):
    """Credits to user JLT: https://stackoverflow.com/questions/40269725/trying-to-construct-identity-matrix"""
    return [[0]*i + [1] + [0]*(n-i-1) for i in range(n)]