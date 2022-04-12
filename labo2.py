import vtk
import math

FILENAME = "altitudes.txt"

EARTH_RADIUS = 6371009

# elevation 0, lon 6.25 lat 46.25
FOCAL_POINT = [501_025, 4_405_635, 4_574_833]

# elavation 300km, lon 6.25 lat 46.25
CAMERA_POSITION = [524_618, 4_613_089, 4_790_254]

# Lat N
LAT_MIN = 45
LAT_MAX = 47.5
# Lon E
LON_MIN = 5
LON_MAX = 7.5

rows = 0
cols = 0


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

# First line contain size of grid
# Then it contains a grid of elevations.
with open(FILENAME) as file:
    rows, cols = map(int, file.readline().strip().split(" "))

    interval_azimuth = (LAT_MAX - LAT_MIN) / (rows - 1)
    interval_inclination = (LON_MAX - LON_MIN) / (cols - 1)

    elevations = [[int(x) for x in line.strip().split(" ")] for line in file]

for i, elevs in enumerate(elevations):
    for j, elev in enumerate(elevs):
        (x, y, z) = to_cartesian(elev + EARTH_RADIUS,
                                 math.radians(LAT_MIN + i * interval_azimuth),
                                 math.radians(LON_MIN + j * interval_inclination))

        points.InsertNextPoint(x, y, z)

# Create grid
grid = vtk.vtkStructuredGrid()
grid.SetDimensions(rows, cols, 1)
grid.SetPoints(points)


mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(grid)

gridActor = vtk.vtkActor()
gridActor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
renderer.AddActor(gridActor)
renderer.GetActiveCamera().SetFocalPoint(*FOCAL_POINT)
renderer.GetActiveCamera().SetPosition(*CAMERA_POSITION)
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