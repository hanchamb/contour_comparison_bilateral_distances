import numpy as np
import open3d as o3d
import pyvista as pv
import os
import pandas as pd

# class to definte the contours with mesh and name
class Contour:
    def __init__(self, mesh, name):
        self.mesh = mesh;
        self.name = name;

class RegionContour:
    def __init__(self, input_unstructured_grid, name):
        self.input_unstructured_grid = input_unstructured_grid
        self.encl_points = self.convertToNumpyArray();
        self.name = name;
        
    def convertToNumpyArray(self):
        return(np.asarray(self.input_unstructured_grid.points))

class CameraView:
    def __init__(self, name, camera_pos, azimuth, elevation):
        self.name = name;
        self.camera_pos = camera_pos;
        self.azimuth = azimuth
        self.elevation = elevation;

##### FUNCTIONS 
#function for visualising the reference contour on PyVista images
def pyvistarise(mesh):
    return pv.PolyData(np.asarray(mesh.vertices), np.insert(np.asarray(mesh.triangles), 0, 3, axis=1), deep=True, n_faces=len(mesh.triangles))

def pyvistarise_region(region):
    return pv.PolyData(region)

def camera_positions(plotter, direction):
    plotter.camera_position = direction.camera_pos
    plotter.camera.azimuth = direction.azimuth
    plotter.camera.elevation = direction.elevation
    return;

def plot_images(direction, comparison_name, measure, measure_str, scalar_str, actor_human):
    print("Called plot_images")
    plotter = pv.Plotter(off_screen = True)
    print("Called plotter")
    sargs = dict(title_font_size=30, 
                 label_font_size=30, 
                 shadow=True, 
                 n_labels=5,
                 italic=False, 
                 fmt="%.1f", 
                 font_family="arial", 
                 color='black', 
                 position_x=0.3, 
                 position_y=0.075)
    print("Called sargs")
    plotter.add_mesh(measure,
                    scalars=scalar_str, 
                    smooth_shading=True, 
                    clim=[0, 20], 
                    below_color='white', 
                    above_color='black', 
                    scalar_bar_args=sargs, 
                    cmap="viridis", 
                    lighting = False) 
    print("Called add mesh")
    _ = plotter.add_orientation_widget(actor_human)
    print("Called add orientation widget")
    #plotter.store_image = True
    camera_positions(plotter, direction)
    print("Called camera positions")
    camera_pos = plotter.screenshot(filename= f"{comparison_name}_{measure_str}{direction.name}.png", window_size=[500, 500], return_img = False)
    print("Called plotter.show")
    plotter.close()
    

def plotHeatMapImagesOneToOne(comparison_name, plot_on_mesh, dists_to_plot_on_mesh, directions, regions_TF, actor_human):
    # convert to pyvista for visualisation
    if regions_TF == False:
        pyv_plot_on_mesh = pyvistarise(plot_on_mesh.mesh)    
    else: 
        pyv_plot_on_mesh = pyvistarise_region(plot_on_mesh.encl_points) 
    # assign dists
    norms_means = pyv_plot_on_mesh.compute_normals(point_normals=True, cell_normals=False)
    norms_means["BLD (mm)"] = dists_to_plot_on_mesh["bidir_distance_on_reference"] ##### check what the heading is for the summary at points file (might just need to copy the file across) 
    #plot images at all angles
    for direction in directions: 
        plot_images(direction, comparison_name, norms_means, "bidir_", "BLD (mm)", actor_human);
    # plot gif
    #plot_gif(comparison_name, norms_means, "means_", "mean BLD (mm)");

def plotHeatMapImagesOneToMany(comparison_name, plot_on_mesh, dists_to_plot_on_mesh, directions, regions_TF, actor_human):
    # convert to pyvista for visualisation
    if regions_TF == False:
        pyv_plot_on_mesh = pyvistarise(plot_on_mesh.mesh)    
    else: 
        pyv_plot_on_mesh = pyvistarise_region(plot_on_mesh.encl_points) 
    # assign dists
    norms_means = pyv_plot_on_mesh.compute_normals(point_normals=True, cell_normals=False)
    norms_means["mean BLD (mm)"] = dists_to_plot_on_mesh['mean_at_point']
    norms_std = pyv_plot_on_mesh.compute_normals(point_normals=True, cell_normals=False)
    norms_std["std of BLD (mm)"] = dists_to_plot_on_mesh['std_at_point']
    print("read in normals")

    #plot images at all angles
    for direction in directions: 
        # means 
        plot_images(direction, comparison_name, norms_means, "means_", "mean BLD (mm)", actor_human);
        # stddevs
        plot_images(direction, comparison_name, norms_std, "std_", "std of BLD (mm)", actor_human)
    # plot gif
    #plot_gif(comparison_name, norms_means, "means_", "mean BLD (mm)");


##### MAIN 
def s7_main(base_dir, summary_at_pts_dir, mesh_base_dir, patient_IDs):
    # mesh for the orientation widget
    actor_human = pv.read(os.path.join(base_dir, "model.vtk"))
    pv.global_theme.background = 'white'
    # camera views 
    front_view = CameraView('front', 'zx', 180, 0)
    back_view = CameraView('back', 'zx', 0, 0)
    front_left_up_view = CameraView('front_left_up_tilt', 'yx', -60, 15)
    front_left_down_view = CameraView('front_left_up_tilt', 'yx', -60, -15)
    front_right_up_view = CameraView('front_right_down_tilt', 'yx', -120, 15)
    front_right_down_view = CameraView('front_right_down_tilt', 'yx', -120, -15)
    back_left_up_view = CameraView('back_left_up_tilt', 'yx', 60, 15)
    back_left_down_view = CameraView('back_left_up_tilt', 'yx', 60, -15)
    back_right_up_view = CameraView('back_right_down_tilt', 'yx', 120, 15)
    back_right_down_view = CameraView('back_right_down_tilt', 'yx', 120, -15)
    directions = [front_view, back_view, front_left_up_view, front_left_down_view, front_right_up_view, front_right_down_view, back_left_up_view, back_left_down_view, back_right_up_view, back_right_down_view]


    for patient in patient_IDs:
        print("                 Working with patient " + str(patient))
        os.chdir(os.path.join(mesh_base_dir, patient))
        
   
        ##### REFERENCE MESH
        # staple meshes 
        left_staple_manual_mesh = Contour(o3d.io.read_triangle_mesh("left_breast_manual_staple.ply"), "left_staple_manual")
        right_staple_manual_mesh = Contour(o3d.io.read_triangle_mesh("right_breast_manual_staple.ply"), "right_staple_manual")
        
        full_contour_sd_directory = os.path.join(summary_at_pts_dir, patient)
        
        # FULL CONTOURS 
        #location to save images to 
        full_image_directory = os.path.join(base_dir, 'full_images_viridis')
        if not os.path.exists(full_image_directory):
            os.makedirs(full_image_directory)
        
        # read bidir distance file
        for file in os.listdir(full_contour_sd_directory):
            if ("left" in file) and (".pkl" in file):
                df = pd.read_pickle(os.path.join(full_contour_sd_directory, file))
                
                os.chdir(full_image_directory)
                if ("atlas" in file):
                    print(file)
                    plotHeatMapImagesOneToMany("left_atlas", left_staple_manual_mesh, df, [back_view], False, actor_human) # replace [back_view] with directions
                elif ("manual" in file):
                    print(file)
                    plotHeatMapImagesOneToMany("left_manual", left_staple_manual_mesh, df, [back_view], False, actor_human) # replace [back_view] with directions
                 

            elif ("right" in file) and (".pkl" in file):
                df = pd.read_pickle(os.path.join(full_contour_sd_directory, file))

                os.chdir(full_image_directory)
                if ("atlas" in file):
                    print(file)
                    plotHeatMapImagesOneToMany("right_atlas", right_staple_manual_mesh, df, [back_view], False, actor_human)   # replace [back_view] with directions 
                elif ("manual" in file):
                    print(file)
                    plotHeatMapImagesOneToMany("right_manual", right_staple_manual_mesh, df, [back_view], False, actor_human)   # replace [back_view] with directions 