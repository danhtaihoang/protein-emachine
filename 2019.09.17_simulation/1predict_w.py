import numpy as np
import matplotlib.pyplot as plt
import emachine as EM

from sklearn.preprocessing import OneHotEncoder

np.random.seed(0)
#===========================================================================
# parameters:
m = 4
seqs = np.loadtxt('seqs.txt')

n_var = seqs.shape[1]

#mx = np.array([len(np.unique(s0[:,i])) for i in range(n)])
mx = np.array([m for i in range(n_var)])
mx_cumsum = np.insert(mx.cumsum(),0,0)
i1i2 = np.stack([mx_cumsum[:-1],mx_cumsum[1:]]).T 
mx_sum = mx.sum()
n_linear = n_var*(m-1)

#=============================================================================
# infer w:
onehot_encoder = OneHotEncoder(sparse=False,categories='auto')
seqs_onehot = onehot_encoder.fit_transform(seqs)  # one hot
    
ops = EM.operators(seqs_onehot,n_var,i1i2)

n_ops = ops.shape[1]
eps_list = np.linspace(0.1,0.4,4)
E_eps = np.zeros(len(eps_list))
w_eps = np.zeros((len(eps_list),n_ops))
for i,eps in enumerate(eps_list):
    w_eps[i,:],E_eps[i] = EM.fit(ops,n_var,m,eps=eps,max_iter=100)
    print(eps,E_eps[i])

ieps = np.argmax(E_eps)
w = w_eps[ieps]
print('optimal eps:', eps_list[ieps])
#plt.plot(eps_list,E_eps)

#=============================================================================
# convert w from 1d to 2d
ij2d = EM.ij_2d_from_1d(n_var,m,i1i2)
n_ops = len(w)

w2d = np.zeros((mx_sum,mx_sum))
for iops in range(n_linear,n_ops):
    w2d[int(ij2d[iops,0]),int(ij2d[iops,1])] = w[int(iops)]

#------------------------------------------------
#correct the interaction from/to the last aa:
for i in range(n_var-1):
    i1,i2 = i1i2[i,0],i1i2[i,1]
    for j in range(i+1,n_var):
        j1,j2 = i1i2[j,0],i1i2[j,1]

        w2d[i1:i2,j2-1] = -np.sum(w2d[i1:i2,j1:j2-1],axis=1)
        w2d[i2-1,j1:j2] = -np.sum(w2d[i1:i2-1,j1:j2],axis=0)

#np.savetxt('w.dat',w,fmt='%f')      
np.savetxt('w2d.dat',w2d,fmt='%f') 

## plot
w_true = np.loadtxt('w_true.txt')
print('w2d:')
plt.plot([-2,2],[-2,2])    
plt.scatter(w_true,w2d)
plt.show()  