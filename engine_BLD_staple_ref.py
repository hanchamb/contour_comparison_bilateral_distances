import os

import s1_dcm_to_nii
import s2_get_staple_contours
import s3_nii_to_meshes 
import s4_calc_BLDs
import s5_calc_SDs
import s6_calc_dist_metrics
import ActorCreationCode
import s7_visualisations

dicom_base_dir = "C:// ....."

output_base_dir = "C://..."
if not os.path.exists(output_base_dir):
    os.mkdir(output_base_dir)
nifti_base_dir = os.path.join(output_base_dir, "nifti_masks")
if not os.path.exists(nifti_base_dir):
    os.mkdir(nifti_base_dir)
mesh_base_dir = os.path.join(output_base_dir, "smoothed_meshes")
if not os.path.exists(mesh_base_dir):
    os.mkdir(mesh_base_dir)
bld_dfs_dir = os.path.join(output_base_dir, "BLD_dataframes")
if not os.path.exists(bld_dfs_dir):
    os.mkdir(bld_dfs_dir)
summary_at_pts_dir = os.path.join(output_base_dir, "summary_at_points")
if not os.path.exists(summary_at_pts_dir):
    os.mkdir(summary_at_pts_dir)



patient_numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
sides = ["left", "right"];
cntset = ["manual", "atlas_edited"]
organ_name = "breast"
observers = [f"_{organ_name}_1_",f"_{organ_name}_2_",f"_{organ_name}_3_",f"_{organ_name}_4_",f"_{organ_name}_5_",f"_{organ_name}_6_",f"_{organ_name}_7_",f"_{organ_name}_8_",f"_{organ_name}_9_",f"_{organ_name}_10_"]

s1_dcm_to_nii.s1_main(dicom_base_dir, nifti_base_dir, patient_numbers, organ_name), 
s2_get_staple_contours.s2_main(nifti_base_dir, patient_numbers, sides, cntset, observers) 
s3_nii_to_meshes.s3_main(nifti_base_dir, mesh_base_dir, patient_numbers)
s4_calc_BLDs.s4_main(mesh_base_dir, bld_dfs_dir, patient_numbers)
s5_calc_SDs.s5_main(bld_dfs_dir, summary_at_pts_dir, patient_numbers)
s6_calc_dist_metrics.s6_main(output_base_dir, bld_dfs_dir, patient_numbers)
ActorCreationCode.actor_main(output_base_dir)
s7_visualisations.s7_main(output_base_dir, summary_at_pts_dir, mesh_base_dir, patient_numbers)

