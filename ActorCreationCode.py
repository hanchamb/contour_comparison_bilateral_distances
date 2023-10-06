import pyvista as pv
import os

def actor_main(base_dir): 
    sphere = pv.Sphere(radius=9, center=(0, 0, 0), direction=(0, 0, 1), theta_resolution=30, phi_resolution=30, start_theta=0, end_theta=360, start_phi=0, end_phi=180)

    nose = pv.Cone(center=(0.0, 0.0, 9.0), direction=(0.0, 0.0, 1.0), height=7.5, radius=3, capping=True, angle=None, resolution=6)
    nose = nose.rotate_x(90, point=(0, 0, 0), inplace=False)

    eye_1 = pv.Sphere(radius=1, center=(2, 3, 8.8), direction=(0, 0, 1), theta_resolution=30, phi_resolution=30, start_theta=0, end_theta=360, start_phi=0, end_phi=180)
    eye_1 = eye_1.rotate_x(90, point=(0, 0, 0), inplace=False)

    eye_2 = pv.Sphere(radius=1, center=(2, -3, 8.8), direction=(0, 0, 1), theta_resolution=30, phi_resolution=30, start_theta=0, end_theta=360, start_phi=0, end_phi=180)
    eye_2 = eye_2.rotate_x(90, point=(0, 0, 0), inplace=False)

    left_arm = pv.Cylinder(center=(10.0, 15, 0.0), direction=(1.0, 0.0, 0.0), radius=2, height=20.0, resolution=100, capping=True)
    left_arm = left_arm.rotate_z(90, point=(0, 0, 0), inplace=False)
    left_arm = left_arm.rotate_x(90, point=(0, 0, 0), inplace=False)

    right_arm = pv.Cylinder(center=(-10.0, 15, 0.0), direction=(1.0, 0.0, 0.0), radius=2, height=20.0, resolution=100, capping=True)
    right_arm = right_arm.rotate_z(90, point=(0, 0, 0), inplace=False)
    right_arm = right_arm.rotate_x(90, point=(0, 0, 0), inplace=False)

    left_leg = pv.Cylinder(center=(8.0, 35, 0.0), direction=(0.5, 0.8, 0.0), radius=2, height=20.0, resolution=100, capping=True)
    left_leg = left_leg.rotate_z(90, point=(0, 0, 0), inplace=False)
    left_leg = left_leg.rotate_x(90, point=(0, 0, 0), inplace=False)

    left_foot = pv.Cylinder(center=(14.0, 42.5, 2.5), direction=(0.5, 0, 1), radius=2.1, height=7.5, resolution=100, capping=True)
    left_foot = left_foot.rotate_z(90, point=(0, 0, 0), inplace=False)
    left_foot = left_foot.rotate_x(90, point=(0, 0, 0), inplace=False)

    right_leg = pv.Cylinder(center=(-8.0, 35, 0.0), direction=(0.5, -0.8, 0.0), radius=2, height=20.0, resolution=100, capping=True)
    right_leg = right_leg.rotate_z(90, point=(0, 0, 0), inplace=False)
    right_leg = right_leg.rotate_x(90, point=(0, 0, 0), inplace=False)

    right_foot = pv.Cylinder(center=(-14.0, 42.5, 2.5), direction=(-0.5, 0, 1), radius=2.1, height=7.5, resolution=100, capping=True)
    right_foot = right_foot.rotate_z(90, point=(0, 0, 0), inplace=False)
    right_foot = right_foot.rotate_x(90, point=(0, 0, 0), inplace=False)

    body = pv.Superquadric(center=(0.0, 20, 0.0), scale=(0.5, 0.3, 1.2), size=10, theta_roundness=0.1, phi_roundness=0.5, theta_resolution=16, phi_resolution=16, toroidal=False, thickness=0.3333333333333333)
    body = body.rotate_z(90, point=(0, 0, 0), inplace=False)
    body = body.rotate_x(90, point=(0, 0, 0), inplace=False)

    block = pv.MultiBlock([right_arm, left_arm, right_leg, left_leg, sphere, nose, left_foot, right_foot, eye_1, eye_2, body])

    merged = block.combine(merge_points=True)
    merged.n_points
    merged.save(os.path.join(base_dir, "model.vtk"))

    # # # Create plotting object.
    # pv.global_theme.background = 'white'
    # plotter = pv.Plotter()
    # _ = plotter.add_mesh(right_arm, 'r')
    # _ = plotter.add_mesh(left_arm, 'b')
    # _ = plotter.add_mesh(right_leg, 'r')
    # _ = plotter.add_mesh(left_leg, 'b')
    # _ = plotter.add_mesh(sphere, 'b')
    # _ = plotter.add_mesh(nose, 'b')
    # _ = plotter.add_mesh(left_foot, 'b')
    # _ = plotter.add_mesh(right_foot, 'r')
    # _ = plotter.add_mesh(eye_1, 'b')
    # _ = plotter.add_mesh(eye_2, 'b')
    # _ = plotter.add_mesh(body, 'b')
    # #marker_args = dict(cone_radius=0.6, shaft_length=0.7, tip_length=0.3, ambient=1, label_size=(0.4, 0.16))
    # #actor = plotter.add_axes(line_width=5, marker_args=marker_args)
    # _ = plotter.add_camera_orientation_widget()
    # actor = plotter.add_orientation_widget(pv.Arrow(), color='g')
    # plotter.camera_position= 'yx'
    # #plotter.camera.azimuth = -120
    # #plotter.camera.elevation = 15
    # camera_pos = plotter.show(return_cpos= True)
    # print(camera_pos)

