"""
simple scipt to live visualize spectrometer data

Ian Zurutuza -- Wed 31 Dec 2025 01:56:47 PM CST
"""
# https://python-seabreeze.readthedocs.io/en/latest/quickstart.html
BACKEND = None # defaults to cseabreeze

import seabreeze

import sys
# on windows default to python implementation.
if (sys.platform == "win32" or BACKEND == "pyseabreeze"):
    seabreeze.use('pyseabreeze')

from seabreeze.spectrometers import Spectrometer

import threading

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class SpectralAnimation:
    def __init__(self, spec, max_samples: int=10, integration_time_us: int=20000):
        self.spec = spec
        self.max_samples = max_samples
        self.wavelengths = self.spec.wavelengths()  # Retrieve wavelengths once
        self.intensity_data = []  # Store intensity data
        self.integration_time = integration_time_us

        # Initialize the figure and axis
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_xlim(np.min(self.wavelengths), np.max(self.wavelengths))  # Set x-axis limits
        self.ax.set_ylim(1000, 100000)  # Set y-axis limits (adjust as needed)
        self.ax.set_yscale("log")
        self.ax.set_xlabel('Wavelength (nm)')
        self.ax.set_ylabel('Intensity')
        self.ax.set_title('Spectral Intensity')

        self.integration_string = self.ax.text(0.05,0.9, "", bbox={'facecolor':'w', 'alpha':0.5, 'pad':5},
                transform=self.ax.transAxes, ha="left")

        # Create the animation
        self.ani = animation.FuncAnimation(self.fig, self.update, init_func=self.init, frames=np.arange(0, 100), blit=True, interval=100)

        print("INIT")
        self.input_thread = threading.Thread(target=self.get_user_input)
        self.input_thread.daemon = True  # Daemonize thread
        self.input_thread.start()

    def init(self):
        self.line.set_data([], [])
        return self.line,

    def update(self, frame):
        # Get the current intensities
        intensities = self.spec.intensities()
        # TODO: optionally write this data to file here? (probably should be done with button press)

        self.intensity_data.append(intensities)
        
        self.integration_string.set_text(f"integration time: {self.integration_time}us")

        if len(self.intensity_data) > self.max_samples:
            self.intensity_data.pop(0)

        self.line.set_data(self.wavelengths, intensities)
        return self.line, self.integration_string

    def show(self):
        plt.show()
    
    def set_integration_time(self, time_micros):
        """Set the integration time in microseconds."""
        self.spec.integration_time_micros(time_micros)
        self.integration_time = time_micros

    def get_user_input(self):
        while True:
            try:
                integration_time = int(input("Enter integration time in microseconds (or -1 to exit): "))
                if integration_time < 10: 
                    print("Exiting...")
                    break
                self.set_integration_time(integration_time)
                print(f"Integration time set to {integration_time} microseconds.")
            except ValueError:
                print("Invalid input. Please enter an integer.")


if __name__ == "__main__":

    spec = Spectrometer.from_first_available()
    print(type(spec), spec)
    spec.integration_time_micros(20000)
    print(spec.wavelengths())
    print(spec.intensities())

    animation = SpectralAnimation(spec)
    animation.show()



