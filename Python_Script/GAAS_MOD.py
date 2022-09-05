#%%
import os, sys
from pathlib import Path
sys.path.append("/opt/lumerical/v212/api/python")
import lumapi
import numpy as np
import time
import logging
from GAAS_MOD_lib import make_wg_base, make_charge, make_nk

#%%
# Global Variables
# basedir = os.path.dirname(__file__)
basedir = os.getcwd()
simdir = basedir + '/GAAS_MOD_SIM'
datadir = basedir + '/result'
iter_count = 0
init_time = time.time()
debug_show = False
# print(basedir)

# Logging setup
logging.basicConfig(filename="test.log", 
					format='%(asctime)s %(message)s', 
					filemode='w') 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Iterables
# 11x11 sweeps, take about 100 minutes to run
# gold_gap = np.linspace(0.55e-6,3e-6,15)
# algaas_gap = np.linspace(8e-7,9e-7,11)

# Run workflow 1x1/2x2 for the demo purpose
gold_gap = np.linspace(0.55e-6,3e-6,2)
algaas_gap = np.linspace(9e-7,9e-7,1)

# Result matrices
delta_loss_mat = np.zeros((np.size(gold_gap),np.size(algaas_gap)))
delta_neff_mat = np.zeros((np.size(gold_gap),np.size(algaas_gap)),dtype=np.complex128)
origin_loss_mat = np.zeros((np.size(gold_gap),np.size(algaas_gap)))
origin_neff_mat = np.zeros((np.size(gold_gap),np.size(algaas_gap)),dtype=np.complex128)
bias_loss_mat = np.zeros((np.size(gold_gap),np.size(algaas_gap)))
bias_neff_mat = np.zeros((np.size(gold_gap),np.size(algaas_gap)),dtype=np.complex128)
v_pi_l = np.zeros((np.size(gold_gap),np.size(algaas_gap)))

# Make a directory for simulation files
Path(basedir + '/GAAS_MOD_SIM').mkdir(parents=True, exist_ok=True)
Path(basedir + '/result').mkdir(parents=True, exist_ok=True)

# Iteration start here
for i, gold_g in enumerate(gold_gap,0):
    for j, algaas_g in enumerate(algaas_gap,0):
        # Timing
        start_time = time.time()
        iter_count = iter_count + 1

        with lumapi.MODE(hide=(not debug_show)) as mode:
            # Make a wg with given geometric parameters
            make_wg_base(mode,gold_gap=gold_g,algaas_gap=algaas_g)
            # Load the created mode
            mode.load(simdir+'/base.lms')
            mode.cleardcard()
            mode.loaddata(basedir+'/target_mode.ldf')
            mode.setanalysis('wavelength',float(1.55e-6))
            mode.setanalysis('number of trial modes',15)
            mode.setanalysis('use max index',False)
            mode.setanalysis('n',float(3.2))
            mode.run()
            mode.findmodes()

            ##Bebugging: make sure everything is right
            # mode.eval("target_mode_origin = bestoverlap('global_mode7');")
            # mode.eval("visual_E = getresult(target_mode_origin,'E');")
            # mode.eval("neff_struct = getdata(target_mode_origin,'neff');")
            # mode.eval("loss_struct = getdata(target_mode_origin,'loss');")
            # print(mode.getv("neff_struct"))
            # print(mode.getv("loss_struct"))
            if (debug_show):
                input("Press Enter to continue...")

            # Save couple variable to datafile for later use
            mode.eval("mname='::model::FDE::data::material';")
            mode.eval("rect_x=getdata(mname,'x');")      # position vectors associated with Ex fields
            mode.eval("rect_y=getdata(mname,'y');")      # position vectors associated with Ex fields
            mode.select("AlGaAs-Bot")
            mode.eval("AlGaAs_index=getindex(get('material'),c/1.55e-6);")
            mode.select("GaAs-Core")
            mode.eval("GaAs_index=getindex(get('material'),c/1.55e-6);")
            mode.savedata(simdir+'/rect_grid')

        with lumapi.DEVICE(hide=(not debug_show)) as device:
            # Make a charge with given geometric parameters
            make_charge(device,gold_gap=gold_g,algaas_gap=algaas_g)
            device.load(simdir+'/charge.ldev')
            device.run()
            device.eval('electro_stats=getresult("::model::CHARGE","electrostatics");')
            device.eval('Ey = pinch(electro_stats.E(:,1,1,2));')
            device.eval('temp = size(Ey);')
            device.eval('L = temp(1);')
            device.eval('vtx = getdata("CHARGE","charge","vertices");')
            device.eval('tri = getdata("CHARGE","charge","elements");')
            device.eval('vtx = vtx(1:L,[1,2]);')
            device.loaddata(simdir+'/rect_grid.ldf')
            device.eval('rect_Ey = interptri(tri,vtx,Ey,rect_x,rect_y);')

            ##Bebugging: make sure everything is right
            if (debug_show):
                input("Press Enter to continue...")

            device.savedata(simdir+'/rect_Ey')

        with lumapi.MODE(simdir+'/base.lms',hide=(not debug_show)) as mode:
            # Save this to new .lms file for later visualize
            mode.save(simdir+"/bias.lms")
            mode.load(simdir+"/bias.lms")

            # Load saved workspace variable
            mode.loaddata(simdir+'/rect_Ey.ldf')
            mode.loaddata

            # Import (n,k) material as original structure and run to get neff and loss
            make_nk(mode)
            
            # Run simulation with only (n,k) origin enabled
            mode.select("nk1_origin")
            mode.set("enabled",True)
            mode.select("nk2_origin")
            mode.set("enabled",True)
            mode.select("nk3_origin")
            mode.set("enabled",True)
            mode.select("nk1_bias")
            mode.set("enabled",False)
            mode.select("nk2_bias")
            mode.set("enabled",False)
            mode.select("nk3_bias")
            mode.set("enabled",False)
            mode.cleardcard()
            mode.loaddata(basedir+'/target_mode.ldf')
            mode.setanalysis('wavelength',float(1.55e-6))
            mode.setanalysis('number of trial modes',15)
            mode.setanalysis('use max index',False)
            mode.setanalysis('n',float(3.2))
            mode.run()
            mode.findmodes()
            mode.eval("target_mode_origin = bestoverlap('global_mode7');")
            mode.eval("neff_origin = getdata(target_mode_origin,'neff');")
            mode.eval("loss_origin = getdata(target_mode_origin,'loss');")
            origin_loss_mat[i,j] = mode.getv("loss_origin")
            origin_neff_mat[i,j] = mode.getv("neff_origin")

            # Run simulation with only (n,k) bias enabled
            mode.switchtolayout()
            mode.select("nk1_origin")
            mode.set("enabled",False)
            mode.select("nk2_origin")
            mode.set("enabled",False)
            mode.select("nk3_origin")
            mode.set("enabled",False)
            mode.select("nk1_bias")
            mode.set("enabled",True)
            mode.select("nk2_bias")
            mode.set("enabled",True)
            mode.select("nk3_bias")
            mode.set("enabled",True)
            mode.setanalysis('wavelength',float(1.55e-6))
            mode.setanalysis('number of trial modes',15)
            mode.setanalysis('use max index',False)
            mode.setanalysis('n',float(3.2))
            mode.run()
            mode.findmodes()
            mode.eval("target_mode_bias = bestoverlap('global_mode7');")
            mode.eval("neff_bias = getdata(target_mode_bias,'neff');")
            mode.eval("loss_bias = getdata(target_mode_bias,'loss');")
            bias_loss_mat[i,j] = mode.getv("loss_bias")
            bias_neff_mat[i,j] = mode.getv("neff_bias")

            # Save delta value and log the results in python console
            end_time = time.time()
            delta_loss_mat[i,j] = bias_loss_mat[i,j] - origin_loss_mat[i,j]
            delta_neff_mat[i,j] = bias_neff_mat[i,j] - origin_neff_mat[i,j]
            v_pi_l[i,j] = 1.55e-6/(2*np.abs(np.real(delta_neff_mat[i,j])))
            str = "Iter: {}| Origin: loss {:.3f} | Bias: loss {:.3f}| Delta: neff {} loss {:.4f}| VpiL {:.5f} Vm| Time: Iter {:.2f}s Elapsed {:.2f}s".format(
                    iter_count,
                    origin_loss_mat[i,j],
                    bias_loss_mat[i,j],
                    delta_neff_mat[i,j],
                    delta_loss_mat[i,j],
                    v_pi_l[i,j],
                    end_time - start_time,
                    end_time - init_time,
                )
            print(str)
            logger.info(str)
            
            mode.save

            # Debugging
            if (debug_show):
                input("Press Enter to continue...")

# Save result as dataframe to 
result_file = datadir+'/result15x11'
np.savez(
    result_file,
    gold_gap=gold_gap,
    algaas_gap=algaas_gap,
    delta_loss_mat=delta_loss_mat,
    delta_neff_mat=delta_neff_mat,
    origin_loss_mat=origin_loss_mat,
    origin_neff_mat=origin_neff_mat,
    bias_loss_mat=bias_loss_mat,
    bias_neff_mat=bias_neff_mat,
    v_pi_l=v_pi_l)
