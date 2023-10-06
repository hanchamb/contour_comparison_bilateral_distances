import os
import pandas as pd

##### CLASSES
class RegionDataframe:
    def __init__(self, df, side, basename, contourer_no):
        self.df = df
        self.side = side
        self.basename = basename
        self.contourer_no = contourer_no

# read in BLD files
#read the dataframes back in
def read_dataframes(contour, individal_BLD_dir, output_dir, side, observers):
    os.chdir(individal_BLD_dir)
    
    dataframes = []
    for n in range(0,len(observers)):
        dataframes.append(pd.read_pickle(f"{side}_{contour}_staple_to_{side}_{contour}_{n+1}.pkl"))
    
    merged_df = dataframes[0]
    for i, df in enumerate(dataframes[1:]):
        merged_df = pd.merge(merged_df, df, how='outer', on = ["reference_X", "reference_Y", "reference_Z"], suffixes=('', f"_{i+2}"))
    # _1 isn't renamed because there aren't any columns with the same name (for all other there is beause of _3, so just rename this one at the end)
    merged_df.rename(columns={"bidir_distance_on_reference": "bidir_distance_on_reference_1"}, inplace = True)

    # calculate mean at that point
    merged_df['mean_at_point'] = merged_df[["bidir_distance_on_reference_1","bidir_distance_on_reference_2","bidir_distance_on_reference_3",
                                  "bidir_distance_on_reference_4","bidir_distance_on_reference_5","bidir_distance_on_reference_6",
                                  "bidir_distance_on_reference_7","bidir_distance_on_reference_8","bidir_distance_on_reference_9",
                                  "bidir_distance_on_reference_10"]].mean(axis = 1)
    
    # calculate SD at that point
    # std population ==> ddof = 0 (if sample, then ddof = 1)
    merged_df['std_at_point'] = merged_df[["bidir_distance_on_reference_1","bidir_distance_on_reference_2","bidir_distance_on_reference_3",
                                 "bidir_distance_on_reference_4","bidir_distance_on_reference_5","bidir_distance_on_reference_6",
                                 "bidir_distance_on_reference_7","bidir_distance_on_reference_8","bidir_distance_on_reference_9",
                                 "bidir_distance_on_reference_10"]].std(axis = 1, ddof=0)
    
    os.chdir(output_dir)
    print(f"Writing bidir_sd_mean_at_pt_{contour}_{side} to file")
    # save to new file
    merged_df.to_pickle(f"bidir_sd_mean_at_pt_{contour}_{side}.pkl")
    merged_df.to_csv(f"bidir_sd_mean_at_pt_{contour}_{side}.csv")

def s5_main(bld_base_dir, summary_at_pts_dir, patient_IDs, observers, sides, contours):

    for patient in patient_IDs:
        patient_BLD_dir = os.path.join(bld_base_dir, patient, "just_BLD_DFs")

        # location to save .pkl files 
        summary_at_pts_pt_dir = os.path.join(summary_at_pts_dir, patient)
        if not os.path.exists(summary_at_pts_pt_dir):
            os.makedirs(summary_at_pts_pt_dir)
                
        print("           Working with patient " + str(patient))

        for side in sides:
            for contour in contours:
                read_dataframes(contour, patient_BLD_dir, summary_at_pts_pt_dir, side, observers) 



