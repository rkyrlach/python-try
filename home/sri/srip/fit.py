
#	curve fitting   A * x^2 + B * x + C = y
#	solution
#	denom = (x1 - x2)(x1 - x3)(x2 - x3)
#	A = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / denom
#	B = (x3^2 * (y1 - y2) + x2^2 * (y3 - y1) + x1^2 * (y2 - y3)) / denom
#	C = (x2 * x3 * (x2 - x3) * y1 + x3 * x1 * (x3 - x1) * y2 + x1 * x2 * (x1 - x2) * y3) / denom
#	xvertex = -B / (2*A);
#	yvertex = C - B*B / (4*A);

# calculate the formula for a parabola from three x,y coordinate pairs

x1 = 0
y1 = 0

x3 = 3453
y3 = 0

x2 = int(x3/2)
y2 = 8000

denom = (x1 - x2)*(x1 - x3)*(x2 - x3)
a = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / denom
b = (x3^2 * (y1 - y2) + x2^2 * (y3 - y1) + x1^2 * (y2 - y3)) / denom
c = (x2 * x3 * (x2 - x3) * y1 + x3 * x1 * (x3 - x1) * y2 + x1 * x2 * (x1 - x2) * y3) / denom
xvertex = -b / (2*a);
yvertex = c - b*b / (4*a);

print ("a= ",a," b= ",b," c= ",c," vertex = ",xvertex," ",yvertex)


