
from multiprocessing import Pool
def double(n):
    return n*2

if __name__=='__main__':
    nums=[2,3,6]
pool=Pool(processes=3)
print(pool.map(double,nums))

