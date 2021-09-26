import numpy as np
south =-2.795 #n3m/s
east = 10.878 #10m/s
center = [-66.38,45.25]

v= np.diff([south,east])
print(v)