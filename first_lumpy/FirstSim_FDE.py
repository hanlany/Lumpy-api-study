import numpy
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from scipy import interpolate
from collections import OrderedDict

import importlib.util
import sys

#The default paths for windows, linux and mac
#spec_win = importlib.util.spec_from_file_location('lumapi', 'C:\\Program Files\\Lumerical\\2020a\\api\\python\\lumapi.py')
spec_lin=importlib.util.spec_from_file_location("lumapi","/opt/lumerical/v212/api/python/lumapi.py")
#spec_mac = importlib.util.spec_from_file_location('luampi', "/Applications/Lumerical/FDTD Solutions/FDTD Solutions.app/Contents/API/Python/lumapi.py")
#Functions that perform the actual loading
lumapi=importlib.util.module_from_spec(spec_lin)# 
spec_lin.loader.exec_module(lumapi)


def sweep_script(ring_index=2.):
    """ This function makes it convenient to reconstruct the simulation,
        while changing a few key properties, a brand new FDTD will start
        and close within this function
    """
    fdtd = lumapi.FDTD()
    fdtd.addfdtd(dimension="2D", x=0.0e-9, y=0.0e-9, x_span=3.0e-6, y_span=1.0e-6)
    fdtd.addgaussian(x=0., y=-0.4e-6, injection_axis="y", waist_radius_w0=0.2e-6, wavelength_start=0.5e-6, wavelength_stop=0.6e-6)
    fdtd.addring(x=0.0e-9, y=0.0e-9, z=0.0e-9, inner_radius=0.1e-6, outer_radius=0.2e-6, index=float(ring_index))
    fdtd.addmesh(dx=10.0e-9, dy=10.0e-9, x=0., y=0., x_span=0.4e-6, y_span=0.4e-6)

    fdtd.addtime(name="time", x=0.0e-9, y=0.0e-9)
    fdtd.addprofile(name="profile", x=0., x_span=3.0e-6, y=0.)

    # Dict ordering is not guaranteed, so if there properties dependant on other properties an ordered dict is necessary
    # In this case 'override global monitor settings' must be true before 'frequency points' can be set
    props = OrderedDict([("name", "power"),("override global monitor settings", True),("x", 0.),("y", 0.4e-6),("monitor type", "linear x"),("frequency points", 10.0)])
    fdtd.addpower(properties=props)


    fdtd.save("fdtd_file.fsp")
    fdtd.run()

    return fdtd.getresult("power", "T"), fdtd.getresult("profile","E"), fdtd.getresult("time","E")


# Sweep over index
for x in numpy.arange(2,4,1):
    T_dataset, E_image, E_time = sweep_script(ring_index=x)
    
    T=T_dataset['T']
    print("T results, index=", x)
    print(T)
    numpy.save("sweep_data.npy",T)


    # create subplots
    if x==3:
        plt.figure(figsize=[10,7.5])
        ax1 = plt.subplot(221)
        t = E_time["t"]
        Ex = E_time["E"][0,0,0,:,0]
        plt.plot(t*1e15, abs(Ex), 'k')
        ax1.set_xlabel('time (fs)')
        ax1.set_ylabel('abs(Ex)')
        ax1.set_xlim(0, 30)
        ax1.text(2, 0.6, 'a)', fontsize=15)

        ax2 = plt.subplot(222)
        plt.plot(t*1e15, abs(Ex), 'k')
        ax2.set_xlabel('time (fs)')
        ax2.set_ylabel('abs(Ex)')
        ax2.set_xlim(100, 200)
        ax2.set_ylim(0, 0.0003)
        ax2.text(110, 0.00026, 'b)', fontsize=15)
        ax2.ticklabel_format(style="scientific", scilimits=(-3,3))

        ax3 = plt.subplot(212)
        plt.plot(t*1e15, abs(Ex), 'k')
        ax3.set_xlabel('time (fs)')
        ax3.set_ylabel('abs(Ex)')
        ax3.text(100, 0.6, 'c)', fontsize=15)

        plt.savefig("linear_plots.png")
        plt.show()

        # create image
        x  = E_image["x"]*1e6 # data on uniform grid, convert m to um
        y  = E_image["y"]*1e6 # data on uniform grid, convert m to um
        Ex = E_image["E"][:,:,0,0,0] # data on uniform grid, selecting the x-component of first frequency
        Ex_abs = abs(Ex)
        xi = numpy.linspace(numpy.amin(x),numpy.amax(x),len(x))
        yi = numpy.linspace(numpy.amin(y),numpy.amax(y),len(y))
        f= interpolate.interp2d(y,x,Ex_abs)
        Exi_abs = f(yi, xi)
        im = plt.imshow(numpy.transpose(Exi_abs), aspect='equal', interpolation='bicubic', cmap=cm.RdYlGn,
                        origin='lower', extent=[xi.min(), xi.max(), yi.min(), yi.max()],
                        vmax=Exi_abs.max(), vmin=Exi_abs.min())

        plt.colorbar()
        plt.xlabel('x (um)')
        plt.ylabel('y (um)')

        indices=numpy.where(Exi_abs==Exi_abs.max()) # finding the location of max abs(Ex)
        plt.annotate('local max', xy=(xi[indices[0]], yi[indices[1]]), xytext=(0.7, -0.2),
                     arrowprops=dict(arrowstyle="->"))


        plt.savefig("image_plot.png")
        plt.show()
