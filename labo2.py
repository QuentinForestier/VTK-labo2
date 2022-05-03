#!/usr/bin/env python
#
# Labo 2 from VTK.
#
# Goal: Achieve to reproduce a topographic map from a part of switzerland
#
# Authors: Forestier Quentin & Herzig Melvyn
#
# Date: 03.05.2022

import vtk
import math
import numpy as np
from skimage import measure, morphology

# --------- constants ---------

FILENAME = "altitudes.txt"

EARTH_RADIUS = 6_371_009

CAMERA_DISTANCE = 500_000

# North latitude
LAT_MIN = 45
LAT_MAX = 47.5

# East longitude
LON_MIN = 5
LON_MAX = 7.5

# Sea level
SEA_LEVEL = 0


# Spherical to cartesian
def to_cartesian(radius: float, latitude: float, longitude: float):
    """
    Translate spherical coordinate to cartesian coordinate
    inclination and azimuth must be in radian
    https://en.wikipedia.org/wiki/Spherical_coordinate_system
    """
    x = radius * math.sin(latitude) * math.sin(longitude)
    y = radius * math.cos(latitude)
    z = radius * math.sin(latitude) * math.cos(longitude)
    return x, y, z


# StructuredGrid use vtkPoints to be placed in the scene.
points = vtk.vtkPoints()

# Will store the attributes of the above points to define which color to use.
altitudes = vtk.vtkIntArray()

# First line contain size of grid
# Then it contains a grid of elevations.
with open(FILENAME) as file:
    rows, cols = map(int, file.readline().strip().split(" "))

    interval_azimuth = (LAT_MAX - LAT_MIN) / (rows - 1)
    interval_inclination = (LON_MAX - LON_MIN) / (cols - 1)

    elevations = np.array([[int(x) for x in line.strip().split(" ")] for line in file])

# For each point, we transform the spherical coordinate into cartesian coordinates in order to place them in the world
for i, elevs in enumerate(elevations):
    for j, elev in enumerate(elevs):
        (x, y, z) = to_cartesian(elev + EARTH_RADIUS,
                                 math.radians(LAT_MIN + i * interval_azimuth),
                                 math.radians(LON_MIN + j * interval_inclination))

        points.InsertNextPoint(x, y, z)

# Here we detect water surfaces.
labels = measure.label(elevations, connectivity=1)  # connectivity=1 -> to compare only adjacent cells.
# Then, we remove regions where area is too small.
lakes = morphology.remove_small_objects(labels, 512) > 0
# Use an arbitrary value to represent water
elevations[lakes] = 0

# For each point, we set his attribute (altitude) that will define his color. The altitude attribute is not necessary of
# the real world altitude. To color water we have defined that the altitude attribute should be 0. For example, for the
# points of the lakes, their attributes are set to 0 but their real altitude is not 0.
#
# Note: Here we make a second pass on each point. Another way to achieve this in one pass would have required to use
# a copy of the altitudes array. Without the copy or without the second pass, the lake points on the scene would have
# use the 0 altitude to determine their cartesian coordinates.
for i in range(0, rows):
    for j in range(0, cols):
        if elevations[i, j] < SEA_LEVEL:
            altitudes.InsertNextValue(0)
        else:
            altitudes.InsertNextValue(elevations[i, j])

# Create grid
# We had the choice between multiple data structures:
# - Image data (Not adapted because our point are not fully aligned)
# - Rectilinear grid (Not adapted for altitude)
# - Structured grid (Perfect for storing array of coordinates)
grid = vtk.vtkStructuredGrid()
grid.SetDimensions(rows, cols, 1)
grid.SetPoints(points)
grid.GetPointData().SetScalars(altitudes)

ctf = vtk.vtkColorTransferFunction()
ctf.AddRGBPoint(0, 0.513, 0.49, 1)  # Water, Blue (0x827CFF) for water
ctf.AddRGBPoint(1, 0.157, 0.325, 0.141)  # Grass, Dark green (0x285223) for low altitude
ctf.AddRGBPoint(500, 0.219, 0.717, 0.164)  # Grass, Light green (0x37B629) for middle (low) altitude
ctf.AddRGBPoint(900, 0.886, 0.721, 0.364)  # Rock, Sort of yellow/brown (0xE1B75C)) for middle (high) altitude
ctf.AddRGBPoint(1600, 1, 1, 1)  # Snow, White (0xFFFFFF) for high altitude (for cliffs)

# --------- Mapper - Actor ---------
mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(grid)
mapper.SetLookupTable(ctf)

gridActor = vtk.vtkActor()
gridActor.SetMapper(mapper)

# --------- Render ---------
renderer = vtk.vtkRenderer()
renderer.AddActor(gridActor)

# Setting focal point to center of the displayed area.
fx, fy, fz = to_cartesian(EARTH_RADIUS, math.radians((LAT_MIN + LAT_MAX) / 2), math.radians((LON_MIN + LON_MAX) / 2))
renderer.GetActiveCamera().SetFocalPoint([fx, fy, fz])

# Setting camera position to center of the zone, elevated by CAMERA_DISTANCE (500km currently)
cx, cy, cz = to_cartesian(EARTH_RADIUS + CAMERA_DISTANCE, math.radians((LAT_MIN + LAT_MAX) / 2),
                          math.radians((LON_MIN + LON_MAX) / 2))
renderer.GetActiveCamera().SetPosition([cx, cy, cz])
renderer.GetActiveCamera().SetClippingRange(0.1, 1_000_000)

renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(renderer)
renWin.SetSize(800, 800)

# --------- Interactor ---------
intWin= vtk.vtkRenderWindowInteractor()
intWin.SetRenderWindow(renWin)

style = vtk.vtkInteractorStyleTrackballCamera()
intWin.SetInteractorStyle(style)

# --------- Print image ---------
renWin.Render()
w2if = vtk.vtkWindowToImageFilter()
w2if.SetInput(renWin)
w2if.Update()
filename = "Map_Screenshot_Sea_Level_" + str(SEA_LEVEL) + ".png"
writer = vtk.vtkPNGWriter()
writer.SetFileName(filename)
writer.SetInputData(w2if.GetOutput())
writer.Write()

intWin.Initialize()
intWin.Start()
