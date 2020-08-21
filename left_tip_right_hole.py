def left_tip(img):
    ydim, xdim = img.shape
    columns = [(img[:, x] == NEW_BACKGROUND).all() for x in range(xdim)]
    tip_col = columns.index(False)
    tip_row = [e for e, x in enumerate(list(img[:, tip_col])) if x != NEW_BACKGROUND][0]
    return (tip_col, tip_row)

def right_hole(img):
    ydim, xdim = img.shape
    columns = [(img[:, x] != NEW_BACKGROUND).all() for x in range(xdim)]
    hole_col = xdim - list(reversed(columns)).index(True)
    hole_row = list(img[:, hole_col]).index(NEW_BACKGROUND)
    return (hole_col, hole_row)

flatten = lambda ll: [x for l in ll for x in l]

def glue(A, B, ar, ac, br, bc):
    ay, ax = A.shape
    by, bx = B.shape

    A.shape, B.shape

    a1x, a1y = -ac, -ar
    a2x, a2y = a1x + ax, a1y + ay

    b1x, b1y = -bc, -br
    b2x, b2y = b1x + bx, b1y + by

    c1x = min(a1x, b1x)
    c1y = min(a1y, b1y)

    c2x = max(a2x, b2x)
    c2y = max(a2y, b2y)

    a1x, a2x = a1x - c1x, a2x - c1x
    b1x, b2x = b1x - c1x, b2x - c1x
    c1x, c2x = c1x - c1x, c2x - c1x

    a1y, a2y = a1y - c1y, a2y - c1y
    b1y, b2y = b1y - c1y, b2y - c1y
    c1y, c2y = c1y - c1y, c2y - c1y
    
    assert(NEW_BACKGROUND == 0)
    C = np.zeros((c2y, c2x))
    C[a1y:a2y, a1x:a2x] += A
    C[b1y:b2y, b1x:b2x] += B
    
    return C

def glue_blocks(B, A):
    ac, ar = left_tip(A)
    bc, br = right_hole(B)
    glued = glue(
        A=A,
        B=B,
        ar=ar, ac=ac, br=br, bc=bc
    )
    return np.array(glued, dtype=np.uint8)

merged = glue_blocks(standard_blocks["J"], standard_blocks["D"])
img = Image.fromarray(merged, "L")
Image