import os, sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

# Global Variables
# basedir = os.path.dirname(__file__)
basedir = os.getcwd()
simdir = basedir + '/GAAS_MOD_SIM'
datadir = basedir + '/result'
resultdir = datadir + '/result15x11.npz'

# Step 1: load saved result.npz data
npzfile = np.load(resultdir)
algaas_gap = npzfile['algaas_gap']
gold_gap = npzfile['gold_gap']
bias_loss_mat = npzfile['bias_loss_mat']
v_pi_l = npzfile['v_pi_l']

# Step 2: Create a surface plot for v_pi_L metric
fig = plt.figure()
Y, X = np.meshgrid(gold_gap*1e6, algaas_gap*1e6)
Z = v_pi_l.T
ax = plt.axes(projection='3d')
ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                cmap='viridis', edgecolor='none')
ax.set_title('VpiL vs (Side Gap, Top Gap)')
ax.set_ylabel('Distance to side electrode (um)')
ax.set_xlabel('Distance to top electrode (um)')
ax.set_zlabel('VpiL (V*m)')

# Step 2: Create a surface plot for bias_loss metric
fig = plt.figure()
Y, X = np.meshgrid(gold_gap*1e6, algaas_gap*1e6)
Z = bias_loss_mat.T
ax = plt.axes(projection='3d')
ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                cmap='viridis', edgecolor='none')
ax.set_title('Waveguid Loss vs (Side Gap, Top Gap)')
ax.set_ylabel('Distance to side electrode (um)')
ax.set_xlabel('Distance to top electrode (um)')
ax.set_zlabel('Loss (db/m)')


# Step 3: Create a surface plot for loss*VpiL metric
fig = plt.figure()
Y, X = np.meshgrid(gold_gap*1e6, algaas_gap*1e6)
Z = bias_loss_mat.T*v_pi_l.T
ax = plt.axes(projection='3d')
ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                cmap='viridis', edgecolor='none')
ax.set_title('Loss*VpiL vs (Side Gap, Top Gap)')
ax.set_ylabel('Distance to side electrode (um)')
ax.set_xlabel('Distance to top electrode (um)')
ax.set_zlabel('Loss*VpiL')
plt.show()

# fig = plt.figure()
# plt.imshow(v_pi_l)
# plt.colorbar()
# plt.show()