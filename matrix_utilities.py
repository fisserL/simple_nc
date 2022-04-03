from numpy import ndarray

def binary_mat_rank(A: ndarray):
    """" Credits to user iddo10: https://gist.github.com/StuartGordonReid/eb59113cb29e529b8105?permalink_comment_id=3268301#gistcomment-3268301 """
    A = A.tolist()
    n = len(A[0])
    rank = 0
    for col in range(n):
        j = 0
        rows = []
        while j < len(A):
            if A[j][col] == 1:
                rows += [j]
            j += 1
        if len(rows) >= 1:
            for c in range(1, len(rows)):
                for k in range(n):
                    A[rows[c]][k] = (A[rows[c]][k] + A[rows[0]][k]) % 2
            A.pop(rows[0])
            rank += 1
    for row in A:
        if sum(row) > 0:
            rank += 1
    return rank