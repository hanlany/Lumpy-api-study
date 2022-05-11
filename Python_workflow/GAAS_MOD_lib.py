import os, sys
from pathlib import Path
from unicodedata import name
sys.path.append("/opt/lumerical/v212/api/python")
import lumapi
import numpy as np
import scipy as sp

# Global Variables
# basedir = os.path.dirname(__file__)
basedir = os.getcwd()
simdir = basedir + '/GAAS_MOD_SIM'
datadir = basedir + '/result'

def make_wg_base(mode,gold_gap = 2e-6,wg_width = 1e-6,algaas_gap = 8e-7):
    # Define some fix variables
    geo1 = "GaAs-Base"
    geo2 = "AlGaAs-Bot"
    geo3 = "GaAs-Core"
    geo4 = "AlGaAs-Top"
    geo5 = "Gold-Top"
    geo6 = "Gold-Side"
    geo1_x = 1e-3
    geo1_y = 3e-4
    geo2_x = 1e-3
    geo2_y = 1e-6
    geo3_x = wg_width
    geo3_y = 4e-7
    geo4_x = wg_width
    geo4_y = algaas_gap
    geo5_x = wg_width
    geo5_y = 1e-7
    geo6_x = 1e-6
    geo6_y = 1e-7

    # Add a meterials - AlxGa(1-x)As-0.41
    mode.importmaterialdb(basedir+'/AlGaAs-41.mdf')

    # Setup Geometries
    # Geometry 1
    mode.addrect(name = geo1, 
                x = 0.0, 
                x_span = geo1_x, 
                y = -(geo1_y/2 + geo2_y),
                y_span = geo1_y, 
                z = 0.0, 
                z_span = 10e-6)
    mode.set('material','GaAs - Palik')
    # Geometry 2
    mode.addrect(name = geo2, 
                x = 0.0, 
                x_span = geo2_x, 
                y = -(geo2_y/2),
                y_span = geo2_y, 
                z = 0.0, 
                z_span = 10e-6)
    mode.set('material','AlxGa(1-x)As-0.41')
    # Geometry 3
    mode.addrect(name = geo3, 
                x = (gold_gap+wg_width)/2, 
                x_span = geo3_x, 
                y = (geo3_y/2),
                y_span = geo3_y, 
                z = 0.0, 
                z_span = 10e-6)
    mode.set('material','GaAs - Palik')
    # Geometry 4
    mode.addrect(name = geo4, 
                x = (gold_gap+wg_width)/2, 
                x_span = geo4_x, 
                y = (geo4_y/2+geo3_y),
                y_span = geo4_y, 
                z = 0.0, 
                z_span = 10e-6)
    mode.set('material','AlxGa(1-x)As-0.41')
    # Geometry 5
    mode.addrect(name = geo5, 
                x = (gold_gap+wg_width)/2, 
                x_span = geo5_x, 
                y = (geo5_y/2+geo4_y+geo3_y),
                y_span = geo5_y, 
                z = 0.0, 
                z_span = 10e-6)
    mode.set('material','Au (Gold) - Palik')
    # Geometry 6
    mode.addrect(name = geo6, 
                x = -(gold_gap+wg_width)/2, 
                x_span = geo6_x, 
                y = geo6_y/2,
                y_span = geo6_y, 
                z = 0.0, 
                z_span = 10e-6)
    mode.set('material','Au (Gold) - Palik')

    # Add mesh
    mode.addmesh(name="mesh_wg")
    mode.set('based on a structure',True)
    mode.set('structure',geo3)
    mode.set('override x mesh',True)
    mode.set('override y mesh',True)
    mode.set('override z mesh',True)
    mode.set('set maximum mesh step', True)
    mode.set('dx', 10e-9)
    mode.set('dy', 10e-9)

    # Add solver
    mode.addfde(solver_type = '2D Z Normal', 
                x = 0.0, 
                x_span = 10.0e-6,
                y_min = -1.0e-6,
                y_max = 2.0e-6,
                z = 0.0)

    # Save lms file
    mode.save(simdir+"/base.lms")
    #input("Press Enter to continue...")

def make_charge(device,gold_gap = 2e-6,wg_width = 1e-6,algaas_gap = 8e-7):
    # Define some fix variables
    geo1 = "GaAs-Base"
    geo2 = "AlGaAs-Bot"
    geo3 = "GaAs-Core"
    geo4 = "AlGaAs-Top"
    geo5 = "Gold-Top"
    geo6 = "Gold-Side"
    geo1_x = 1e-3
    geo1_y = 3e-4
    geo2_x = 1e-3
    geo2_y = 1e-6
    geo3_x = wg_width
    geo3_y = 4e-7
    geo4_x = wg_width
    geo4_y = algaas_gap
    geo5_x = wg_width
    geo5_y = 1e-7
    geo6_x = 1e-6
    geo6_y = 1e-7

    # Setup Materials
    # AlGaAs
    device.addmodelmaterial(name = 'AlxGa(1-x)As-0.41')
    device.addmaterialproperties("CT","AlGaAs (Aluminium Gallium Arsenide)")
    device.select("materials::AlxGa(1-x)As-0.41")
    device.addmaterialproperties("HT","AlGaAs (Aluminium Gallium Arsenide)")
    device.select("materials::AlxGa(1-x)As-0.41")
    device.set("color",np.array([0,1,0,1]))
    # GaAs
    device.addmodelmaterial(name = 'GaAs - Palik')
    device.addmaterialproperties("CT","GaAs (Gallium Arsenide)")
    device.select("materials::GaAs - Palik")
    device.addmaterialproperties("HT","GaAs (Gallium Arsenide)")
    device.select("materials::GaAs - Palik")
    device.set("color",np.array([0.6,0,0,0]))
    # Gold
    device.addmodelmaterial(name = 'Au (Gold) - Palik')
    device.addmaterialproperties("CT","Au (Gold) - CRC")
    device.select("materials::Au (Gold) - Palik")
    device.addmaterialproperties("HT","Au (Gold) - CRC")
    device.select("materials::Au (Gold) - Palik")
    device.set("color",np.array([0,0,0,1]))
    # Air
    device.addmodelmaterial(name = 'Air')
    device.addmaterialproperties("CT","Air")
    device.select("materials::Air")
    device.addmaterialproperties("HT","Air")

    # Setup Geometries
    # Geometry 1
    device.addrect(name = geo1, 
                x = 0.0, 
                x_span = geo1_x, 
                y = -(geo1_y/2 + geo2_y),
                y_span = geo1_y, 
                z = 0.0, 
                z_span = 10e-6)
    device.set('material','GaAs - Palik')
    # Geometry 2
    device.addrect(name = geo2, 
                x = 0.0, 
                x_span = geo2_x, 
                y = -(geo2_y/2),
                y_span = geo2_y, 
                z = 0.0, 
                z_span = 10e-6)
    device.set('material','AlxGa(1-x)As-0.41')
    # Geometry 3
    device.addrect(name = geo3, 
                x = (gold_gap+wg_width)/2, 
                x_span = geo3_x, 
                y = (geo3_y/2),
                y_span = geo3_y, 
                z = 0.0, 
                z_span = 10e-6)
    device.set('material','GaAs - Palik')
    # Geometry 4
    device.addrect(name = geo4, 
                x = (gold_gap+wg_width)/2, 
                x_span = geo4_x, 
                y = (geo4_y/2+geo3_y),
                y_span = geo4_y, 
                z = 0.0, 
                z_span = 10e-6)
    device.set('material','AlxGa(1-x)As-0.41')
    # Geometry 5
    device.addrect(name = geo5, 
                x = (gold_gap+wg_width)/2, 
                x_span = geo5_x, 
                y = (geo5_y/2+geo4_y+geo3_y),
                y_span = geo5_y, 
                z = 0.0, 
                z_span = 10e-6)
    device.set('material','Au (Gold) - Palik')
    # Geometry 6
    device.addrect(name = geo6, 
                x = -(gold_gap+wg_width)/2, 
                x_span = geo6_x, 
                y = geo6_y/2,
                y_span = geo6_y, 
                z = 0.0, 
                z_span = 10e-6)
    device.set('material','Au (Gold) - Palik')

    # Simulation Region
    device.select("simulation region")
    device.set("dimension", '2D Z-Normal')
    device.set("background material",'Air')
    device.set('x', 0.0)
    device.set("x span",10e-6)
    device.set("y min",-1e-6)
    device.set("y max",2e-6)
    device.set('z', 0.0)

    # Add Charge solver
    device.addchargesolver()
    device.addefieldmonitor(
        name='E_field',
        monitor_type=7,
        x = 0.0,
        x_span = 10.0e-6,
        y_min = -1.0e-6,
        y_max = 2.0e-6,
        z = 0.0
    )
    device.set('record electrostatic potential',True)
    device.set('record electric field',True)
    # Boundary conditions
    device.addelectricalcontact()
    device.set("name","anode")
    device.set("bc mode","steady state")
    device.set("sweep type","single")
    device.set("voltage",0.143507)  # setting the voltage to 0 V
    device.set("surface type","solid")
    device.set("solid","Gold-Side")
    device.addelectricalcontact()
    device.set("name","cathode")
    device.set("bc mode","steady state")
    device.set("sweep type","single")
    device.set("voltage",1+0.143507)  # setting the voltage to 1 V
    device.set("surface type","solid")
    device.set("solid","Gold-Top")

    device.select('CHARGE')
    device.set('min edge length',5e-9)
    device.set('max edge length',1e-6)

    # Save lms file
    device.save(simdir+"/charge.ldev")
    # input("Press Enter to continue...")

# Helper
def n_given_ey_AlGaAs(n0,Ey):
    return 0.5*(n0**3)*(-1.28e-12)*Ey

def n_given_ey_GaAs(n0,Ey):
    return 0.5*(n0**3)*(-1.5e-12)*Ey

def make_nk(mode):
    # Get some variable from Lumerical workspace
    rect_z = np.array(([-5e-6],[6e-6]))
    mode.eval('x_size = size(rect_x,1);')
    mode.eval('y_size = size(rect_y,1);')
    x_size = mode.getv('x_size')
    y_size = mode.getv('y_size')
    mode.select("AlGaAs-Bot")
    mode.eval('x_min_1 = get("x min");')
    mode.eval('x_max_1 = get("x max");')
    mode.eval('y_min_1 = get("y min");')
    mode.eval('y_max_1 = get("y max");')
    x_min_1 = mode.getv('x_min_1')
    x_max_1 = mode.getv('x_max_1')
    y_min_1 = mode.getv('y_min_1')
    y_max_1 = mode.getv('y_max_1')
    mode.select("GaAs-Core")
    mode.eval('x_min_2 = get("x min");')
    mode.eval('x_max_2 = get("x max");')
    mode.eval('y_min_2 = get("y min");')
    mode.eval('y_max_2 = get("y max");')
    x_min_2 = mode.getv('x_min_2')
    x_max_2 = mode.getv('x_max_2')
    y_min_2 = mode.getv('y_min_2')
    y_max_2 = mode.getv('y_max_2')
    mode.select("AlGaAs-Top")
    mode.eval('x_min_3 = get("x min");')
    mode.eval('x_max_3 = get("x max");')
    mode.eval('y_min_3 = get("y min");')
    mode.eval('y_max_3 = get("y max");')
    x_min_3 = mode.getv('x_min_3')
    x_max_3 = mode.getv('x_max_3')
    y_min_3 = mode.getv('y_min_3')
    y_max_3 = mode.getv('y_max_3')
    nk_1_x_size = 0
    nk_1_y_size = 0
    nk_2_x_size = 0
    nk_2_y_size = 0
    nk_3_x_size = 0
    nk_3_y_size = 0
    rect_x_1 = np.zeros((1,))
    rect_y_1 = np.zeros((1,))
    rect_x_2 = np.zeros((1,))
    rect_y_2 = np.zeros((1,))
    rect_x_3 = np.zeros((1,))
    rect_y_3 = np.zeros((1,))
    # Get save variables
    AlGaAs_index = mode.getv('AlGaAs_index')
    GaAs_index = mode.getv('GaAs_index')
    rect_x = mode.getv('rect_x')
    rect_y = mode.getv('rect_y')
    rect_Ey = mode.getv('rect_Ey')

    # Findout size of three nk-materials
    for i in range(0,int(y_size)):
        if rect_y[i]>=y_min_1 and rect_y[i]<=y_max_1:
            nk_1_y_size = nk_1_y_size + 1
            rect_y_1 = np.append(rect_y_1,rect_y[i])
            if nk_1_y_size == 1:
                for j in range(0,int(x_size)):
                    if rect_x[j]>=x_min_1 and rect_x[j]<=x_max_1:
                        nk_1_x_size = nk_1_x_size + 1
                        rect_x_1 = np.append(rect_x_1,rect_x[j])
        elif rect_y[i]>=y_min_2 and rect_y[i]<=y_max_2:
            nk_2_y_size = nk_2_y_size + 1
            rect_y_2 = np.append(rect_y_2,rect_y[i])
            if nk_2_y_size == 1:
                for j in range(0,int(x_size)):
                    if rect_x[j]>=x_min_2 and rect_x[j]<=x_max_2:
                        nk_2_x_size = nk_2_x_size + 1
                        rect_x_2 = np.append(rect_x_2,rect_x[j])
        elif rect_y[i]>=y_min_3 and rect_y[i]<=y_max_3:
            nk_3_y_size = nk_3_y_size + 1
            rect_y_3 = np.append(rect_y_3,rect_y[i])
            if nk_3_y_size == 1:
                for j in range(0,int(x_size)):
                    if rect_x[j]>=x_min_3 and rect_x[j]<=x_max_3:
                        nk_3_x_size = nk_3_x_size + 1
                        rect_x_3 = np.append(rect_x_3,rect_x[j])

    # Define n for these three nk structures
    rect_x_1 = rect_x_1[1:np.size(rect_x_1)]
    rect_y_1 = rect_y_1[1:np.size(rect_y_1)]
    rect_x_2 = rect_x_2[1:np.size(rect_x_2)]
    rect_y_2 = rect_y_2[1:np.size(rect_y_2)]
    rect_x_3 = rect_x_3[1:np.size(rect_x_3)]
    rect_y_3 = rect_y_3[1:np.size(rect_y_3)]
    n_nk_1 = np.ones((nk_1_x_size,nk_1_y_size,2,3),dtype=np.complex128)
    n_nk_2 = np.ones((nk_2_x_size,nk_2_y_size,2,3),dtype=np.complex128)
    n_nk_3 = np.ones((nk_3_x_size,nk_3_y_size,2,3),dtype=np.complex128)
    nk_1_x_size = 0
    nk_1_y_size = 0
    nk_2_x_size = 0
    nk_2_y_size = 0
    nk_3_x_size = 0
    nk_3_y_size = 0

    for i in range(0,int(y_size)):
        if(rect_y[i]>=y_min_1 and rect_y[i]<=y_max_1):
            nk_1_y_size = nk_1_y_size + 1
            nk_1_x_size = 0
            for j in range(0,int(x_size)):       
                if(rect_x[j]>=x_min_1 and rect_x[j]<=x_max_1):
                    nk_1_x_size = nk_1_x_size + 1
                    n_nk_1[nk_1_x_size-1,nk_1_y_size-1,0,0] = AlGaAs_index
                    n_nk_1[nk_1_x_size-1,nk_1_y_size-1,1,0] = AlGaAs_index
                    n_nk_1[nk_1_x_size-1,nk_1_y_size-1,0,1] = AlGaAs_index
                    n_nk_1[nk_1_x_size-1,nk_1_y_size-1,1,1] = AlGaAs_index
                    n_nk_1[nk_1_x_size-1,nk_1_y_size-1,0,2] = AlGaAs_index
                    n_nk_1[nk_1_x_size-1,nk_1_y_size-1,1,2] = AlGaAs_index
        elif(rect_y[i]>=y_min_2 and rect_y[i]<=y_max_2):
            nk_2_y_size = nk_2_y_size + 1
            nk_2_x_size = 0
            for j in range(0,int(x_size)):
                if(rect_x[j]>=x_min_2 and rect_x[j]<=x_max_2):
                    nk_2_x_size = nk_2_x_size + 1
                    n_nk_2[nk_2_x_size-1,nk_2_y_size-1,0,0] = GaAs_index
                    n_nk_2[nk_2_x_size-1,nk_2_y_size-1,1,0] = GaAs_index
                    n_nk_2[nk_2_x_size-1,nk_2_y_size-1,0,1] = GaAs_index
                    n_nk_2[nk_2_x_size-1,nk_2_y_size-1,1,1] = GaAs_index
                    n_nk_2[nk_2_x_size-1,nk_2_y_size-1,0,2] = GaAs_index
                    n_nk_2[nk_2_x_size-1,nk_2_y_size-1,1,2] = GaAs_index
        elif(rect_y[i]>=y_min_3 and rect_y[i]<=y_max_3):
            nk_3_y_size = nk_3_y_size + 1
            nk_3_x_size = 0
            for j in range(0,int(x_size)):
                if(rect_x[j]>=x_min_3 and rect_x[j]<=x_max_3):
                    nk_3_x_size = nk_3_x_size + 1
                    n_nk_3[nk_3_x_size-1,nk_3_y_size-1,0,0] = AlGaAs_index
                    n_nk_3[nk_3_x_size-1,nk_3_y_size-1,1,0] = AlGaAs_index
                    n_nk_3[nk_3_x_size-1,nk_3_y_size-1,0,1] = AlGaAs_index
                    n_nk_3[nk_3_x_size-1,nk_3_y_size-1,1,1] = AlGaAs_index
                    n_nk_3[nk_3_x_size-1,nk_3_y_size-1,0,2] = AlGaAs_index
                    n_nk_3[nk_3_x_size-1,nk_3_y_size-1,1,2] = AlGaAs_index

    # Import (n,k) material for original structure
    mode.addimport()
    mode.set('name','nk1_origin')
    mode.importnk2(n_nk_1,rect_x_1,rect_y_1,rect_z)
    mode.addimport()
    mode.set('name','nk2_origin')
    mode.importnk2(n_nk_2,rect_x_2,rect_y_2,rect_z)
    mode.addimport()
    mode.set('name','nk3_origin')
    mode.importnk2(n_nk_3,rect_x_3,rect_y_3,rect_z)

    # Structure with bias 
    nk_1_x_size = 0
    nk_1_y_size = 0
    nk_2_x_size = 0
    nk_2_y_size = 0
    nk_3_x_size = 0
    nk_3_y_size = 0

    for i in range(0,int(y_size)):
        if(rect_y[i]>=y_min_1 and rect_y[i]<=y_max_1):
            nk_1_y_size = nk_1_y_size + 1
            nk_1_x_size = 0
            for j in range(0,int(x_size)):       
                if(rect_x[j]>=x_min_1 and rect_x[j]<=x_max_1):
                    nk_1_x_size = nk_1_x_size + 1
                    n_nk_1[nk_1_x_size-1,nk_1_y_size-1,0,0] = AlGaAs_index+n_given_ey_AlGaAs(AlGaAs_index,rect_Ey[j,i])
                    n_nk_1[nk_1_x_size-1,nk_1_y_size-1,1,0] = AlGaAs_index+n_given_ey_AlGaAs(AlGaAs_index,rect_Ey[j,i])
                    n_nk_1[nk_1_x_size-1,nk_1_y_size-1,0,1] = AlGaAs_index
                    n_nk_1[nk_1_x_size-1,nk_1_y_size-1,1,1] = AlGaAs_index
                    n_nk_1[nk_1_x_size-1,nk_1_y_size-1,0,2] = AlGaAs_index
                    n_nk_1[nk_1_x_size-1,nk_1_y_size-1,1,2] = AlGaAs_index
        elif(rect_y[i]>=y_min_2 and rect_y[i]<=y_max_2):
            nk_2_y_size = nk_2_y_size + 1
            nk_2_x_size = 0
            for j in range(0,int(x_size)):
                if(rect_x[j]>=x_min_2 and rect_x[j]<=x_max_2):
                    nk_2_x_size = nk_2_x_size + 1
                    n_nk_2[nk_2_x_size-1,nk_2_y_size-1,0,0] = GaAs_index+n_given_ey_GaAs(GaAs_index,rect_Ey[j,i])
                    n_nk_2[nk_2_x_size-1,nk_2_y_size-1,1,0] = GaAs_index+n_given_ey_GaAs(GaAs_index,rect_Ey[j,i])
                    n_nk_2[nk_2_x_size-1,nk_2_y_size-1,0,1] = GaAs_index
                    n_nk_2[nk_2_x_size-1,nk_2_y_size-1,1,1] = GaAs_index
                    n_nk_2[nk_2_x_size-1,nk_2_y_size-1,0,2] = GaAs_index
                    n_nk_2[nk_2_x_size-1,nk_2_y_size-1,1,2] = GaAs_index
        elif(rect_y[i]>=y_min_3 and rect_y[i]<=y_max_3):
            nk_3_y_size = nk_3_y_size + 1
            nk_3_x_size = 0
            for j in range(0,int(x_size)):
                if(rect_x[j]>=x_min_3 and rect_x[j]<=x_max_3):
                    nk_3_x_size = nk_3_x_size + 1
                    n_nk_3[nk_3_x_size-1,nk_3_y_size-1,0,0] = AlGaAs_index+n_given_ey_AlGaAs(AlGaAs_index,rect_Ey[j,i])
                    n_nk_3[nk_3_x_size-1,nk_3_y_size-1,1,0] = AlGaAs_index+n_given_ey_AlGaAs(AlGaAs_index,rect_Ey[j,i])
                    n_nk_3[nk_3_x_size-1,nk_3_y_size-1,0,1] = AlGaAs_index
                    n_nk_3[nk_3_x_size-1,nk_3_y_size-1,1,1] = AlGaAs_index
                    n_nk_3[nk_3_x_size-1,nk_3_y_size-1,0,2] = AlGaAs_index
                    n_nk_3[nk_3_x_size-1,nk_3_y_size-1,1,2] = AlGaAs_index

    # Import (n,k) material for bias structure
    mode.addimport()
    mode.set('name','nk1_bias')
    mode.importnk2(n_nk_1,rect_x_1,rect_y_1,rect_z)
    mode.addimport()
    mode.set('name','nk2_bias')
    mode.importnk2(n_nk_2,rect_x_2,rect_y_2,rect_z)
    mode.addimport()
    mode.set('name','nk3_bias')
    mode.importnk2(n_nk_3,rect_x_3,rect_y_3,rect_z)

    # Save mode
    mode.save
    