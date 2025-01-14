## 2019.10.16: ignore last amino acid

import sys
import numpy as np
from scipy import linalg
from sklearn.preprocessing import OneHotEncoder
import expectation_reflection as ER
from direct_info import direct_info
from joblib import Parallel, delayed
#========================================================================================
np.random.seed(1)
#pfam_id = 'PF00011'
pfam_id = sys.argv[1]

#s0 = np.loadtxt('../pfam_5_100k_badcols09/%s_s0.txt'%(pfam_id)).astype(int)
s0 = np.loadtxt('../pfam_10_100k/%s_s0.txt'%(pfam_id)).astype(int)

n_var = s0.shape[1]
mx = np.array([len(np.unique(s0[:,i])) for i in range(n_var)])
mx_cumsum = np.insert(mx.cumsum(),0,0)
i1i2 = np.stack([mx_cumsum[:-1],mx_cumsum[1:]]).T 

#onehot_encoder = OneHotEncoder(sparse=False,categories='auto')
onehot_encoder = OneHotEncoder(sparse=False)

s = onehot_encoder.fit_transform(s0)

mx_sum = mx.sum()
my_sum = mx.sum() #!!!! my_sum = mx_sum

w = np.zeros((mx_sum,my_sum))
h0 = np.zeros(my_sum)

#=========================================================================================
def predict_w(s,mx,i0,i1i2,niter_max,l2):
    #print('i0:',i0)
    i1,i2 = i1i2[i0,0],i1i2[i0,1]
    n = s.shape[1]
    
    ## find x and y
    #x = np.hstack([s[:,:i1],s[:,i2:]])
    #y = s[:,i1:i2]
    
    mx_cumsum = np.insert(mx.cumsum(),0,0)
    aa_last = mx_cumsum[1:] - 1
    y_col = np.arange(i1,i2)
    aa_del = np.union1d(aa_last,y_col)
    x = np.delete(s,aa_del,axis=1)
    y = s[:,i1:i2-1]

    h01,w1 = ER.fit(x,y,niter_max,l2)

    return h01,w1

#-------------------------------
# parallel
res = Parallel(n_jobs = 32)(delayed(predict_w)\
        (s,mx,i0,i1i2,niter_max=10,l2=500.0)\
        for i0 in range(n_var))

#-------------------------------
for i0 in range(n_var):
    i1,i2 = i1i2[i0,0],i1i2[i0,1]
       
    h01 = res[i0][0]
    w1 = res[i0][1]

    h0[i1:i2-1] = h01    
    #w[:i1,i1:i2] = w1[:i1,:]
    #w[i2:,i1:i2] = w1[i1:,:]

    mx_cumsum = np.insert(mx.cumsum(),0,0)
    aa_last = mx_cumsum[1:] - 1
    y_col = np.arange(i1,i2)
    aa_del = np.union1d(aa_last,y_col)

    mx_sum = mx.sum()
    aa_all = np.arange(mx_sum)

    aa_remain = np.setdiff1d(aa_all,aa_del)

    w[aa_remain,i1:i2-1] = w1

# make w to be symmetric
w = (w + w.T)/2.
di = direct_info(s0,w)
np.savetxt('%s/di.dat'%pfam_id,di,fmt='% 3.8f')

