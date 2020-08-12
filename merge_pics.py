A = np.array([
[1., 1., 1., 1., 1., 0., 0.],
[1., 1., 1., 1., 0., 0., 0.],
[1., 1., 1., 0., 0., 0., 0.],
[1., 1., 1., 1., 0., 0., 0.],
[1., 1., 1., 0., 0., 0., 0.],
[1., 1., 0., 0., 0., 0., 0.],
[1., 1., 1., 0., 0., 0., 0.]])

B = np.array([
[0., 0., 0., 0., 1., 1.],
[0., 0., 0., 1., 1., 1.],
[0., 0., 1., 1., 1., 1.],
[0., 0., 0., 1., 1., 1.],
[0., 0., 1., 1., 1., 1.],
[0., 1., 1., 1., 1., 1.]])

ar, ac = 3, 4
br, bc = 3, 3

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

C = np.zeros((c2y, c2x))
C[a1y:a2y, a1x:a2x] += A
C[b1y:b2y, b1x:b2x] += B