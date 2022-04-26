#!/usr/bin/env python
#
# Labo 2 from VTK.
#
# Goal: Achieve to reproduce a topographic map from a part of switzerland
#
# Authors: Forestier Quentin & Herzig Melvyn
#
# Date: 26.04.2022

import vtk
import math
import numpy as np
from skimage import measure, morphology

# ****************************************
# *               CONSTANTS              *
# ****************************************

FILENAME = "altitudes.txt"

EARTH_RADIUS = 6_371_009

CAMERA_DISTANCE = 500_000

# North latitude
LAT_MIN = 45
LAT_MAX = 47.5

# East longitude
LON_MIN = 5
LON_MAX = 7.5


def to_cartesian(radius: float, inclination: float, azimuth: float):
    """
    Translate spherical coordinate to cartesian coordinate
    inclination and azimuth must be in radian
    https://en.wikipedia.org/wiki/Spherical_coordinate_system
    """
    x = radius * math.sin(inclination) * math.sin(azimuth)
    y = radius * math.cos(inclination)
    z = radius * math.sin(inclination) * math.cos(azimuth)
    return x, y, z


# StructuredGrid use vtkPoints
points = vtk.vtkPoints()

# Will store the attributes of the above points
altitudes = vtk.vtkIntArray()

# First line contain size of grid
# Then it contains a grid of elevations.
with open(FILENAME) as file:
    rows, cols = map(int, file.readline().strip().split(" "))

    interval_azimuth = (LAT_MAX - LAT_MIN) / (rows - 1)
    interval_inclination = (LON_MAX - LON_MIN) / (cols - 1)

    elevations = np.array([[int(x) for x in line.strip().split(" ")] for line in file])

for i, elevs in enumerate(elevations):
    for j, elev in enumerate(elevs):
        (x, y, z) = to_cartesian(elev + EARTH_RADIUS,
                                 math.radians(LAT_MIN + i * interval_azimuth),
                                 math.radians(LON_MIN + j * interval_inclination))

        points.InsertNextPoint(x, y, z)
        # altitudes.InsertNextValue(elevations_lake[i, j])


labels = measure.label(elevations, connectivity=1)
# removes too small regions
mask = morphology.remove_small_objects(labels, 512) > 0
# Use an arbitrary value to represent water
elevations[mask] = 0

for i in range(0, rows):
    for j in range(0, cols):
        altitudes.InsertNextValue(elevations[i, j])

# Create grid
grid = vtk.vtkStructuredGrid()
grid.SetDimensions(rows, cols, 1)
grid.SetPoints(points)
grid.GetPointData().SetScalars(altitudes)

ctf = vtk.vtkColorTransferFunction()
ctf.AddRGBPoint(0, 0.513, 0.49, 1)
ctf.AddRGBPoint(1, 0.157, 0.325, 0.141)
ctf.AddRGBPoint(500, 0.219, 0.717, 0.164)
ctf.AddRGBPoint(900, 0.886, 0.721, 0.364)
ctf.AddRGBPoint(1600, 1, 1, 1)

mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(grid)
mapper.SetLookupTable(ctf)

gridActor = vtk.vtkActor()
gridActor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
renderer.AddActor(gridActor)
fx, fy, fz = to_cartesian(EARTH_RADIUS, math.radians((LAT_MIN + LAT_MAX) / 2), math.radians((LON_MIN + LON_MAX) / 2))
renderer.GetActiveCamera().SetFocalPoint([fx, fy, fz])

cx, cy, cz = to_cartesian(EARTH_RADIUS + CAMERA_DISTANCE, math.radians((LAT_MIN + LAT_MAX) / 2),
                          math.radians((LON_MIN + LON_MAX) / 2))
renderer.GetActiveCamera().SetPosition([cx, cy, cz])
renderer.GetActiveCamera().SetClippingRange(0.1, 1_000_000)

renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(renderer)
renWin.SetSize(800, 800)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

style = vtk.vtkInteractorStyleTrackballCamera()
iren.SetInteractorStyle(style)

iren.Initialize()
iren.Render()
iren.Start()
