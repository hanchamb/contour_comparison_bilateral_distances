import os
import pandas as pd
import regex as re


##### CLASSES 
class DataframeFile():
    def __init__(self, filename, patient_ID):
        self.patientID = patient_ID
        self.filename = filename
        self.distances = self.set_distance_array()
        self.meanDTA = self.calc_and_set_meanDTA()
        self.hausdorff = self.calc_and_set_HD()
        self.side = self.define_side()
        self.contourer_no = self.define_contourer_no()
        self.contour_type = self.define_contour_type()
        self.heading = self.define_df_heading()
    
    ##### UNSURE IF THIS WILL STILL WORK; CHECK OUTPUTS FROM S4 & S5... 
    def set_distance_array(self):
        dataframe = pd.read_pickle(self.filename)
        dist_series = dataframe['bidir_distance_on_reference']
        return dist_series

    # mean DTA defined as the mean value of the bidir distances (not of the a-to-b and b-to-a values, as that would be biased by smaller values)
    def calc_and_set_meanDTA(self):
        val = self.distances.mean()
        return val;

    # HD defined as the maximum of the bidirecitonal distances
    def calc_and_set_HD(self):
        val = self.distances.max()
        return val
    
    # search filename to find side of the breast referring to 
    def define_side(self):
        if "left" in self.filename:
            return "left"
        elif "right" in self.filename:
            return "right"
        else:
            return "ERROR: SIDE"

    # search file to find contourer_no (i.e Adam is 1, Bernard is 2, Claire is 3, etc...)
    def define_contourer_no(self):
        text = self.filename
        #number = [int(n) for n in text.split("_") if n.isdigit()]
        regex= "\d{1,2}"
        match= re.findall(regex, text)
        try:
            return str(match[0])
        except:
            return ""

    # search the file name for the type of contour (i.e. atlas, deeplearn, manual, unedited)
    # and set contour_type as that word with the first letter alphabetised for use in the creation of headers
    def define_contour_type(self):
        text = self.filename
        if "atlas" in text:
            print("Atlas")
            return "Atlas"
        elif "manual" in text:
            print("Manual")
            return "Manual"
        else:
            return "ERROR: CONTOUR TYPE"

    # create header for the dataframe i.e RefvsManual1 using properties of the class 
    def define_df_heading(self):
        heading = "staple_manual_VS_" + self.contour_type + self.contourer_no
        return heading   

##### MAIN
def s6_main(base_dir, bld_dfs_dir, patient_IDs):
        
    data = []
    for patient in patient_IDs:
        print("                 Working with patient" + str(patient))
        bld_dfs_pts_dir = os.path.join(bld_dfs_dir, patient, "just_BLD_DFs")
        os.chdir(bld_dfs_pts_dir)

        #read in just the .pkl files 
        left_mean_DTA = {'patient_ID': patient, 'Side': "left", 'Metric (mm)': 'Mean DTA'}
        left_HD = {'patient_ID': patient, 'Side': "left", 'Metric (mm)': 'Hausdorff'}
        right_mean_DTA = {'patient_ID': patient, 'Side': "right", 'Metric (mm)': 'Mean DTA'}
        right_HD = {'patient_ID': patient, 'Side': "right", 'Metric (mm)': 'Hausdorff'}

        # read bidir distance file
        for file in os.listdir(bld_dfs_pts_dir):
            if file.endswith(".pkl"): #bidir_sd_mean_at_pt_" + cntset + "_" + side + ".pkl
                if "left" in file:
                    print(file)
                    # calculate the metrics needed from the file (instatiate class makes these, see class definition)
                    temp = DataframeFile(file, patient);
                    # add the value to the dictionary for that metric under the header made by the class
                    left_mean_DTA[temp.heading] = temp.meanDTA
                    left_HD[temp.heading] = temp.hausdorff
                elif "right" in file:
                    print(file)
                    # calculate the metrics needed from the file (instatiate class makes these, see class definition)
                    temp = DataframeFile(file, patient);
                    # add the value to the dictionary for that metric under the header made by the class
                    right_mean_DTA[temp.heading] = temp.meanDTA
                    right_HD[temp.heading] = temp.hausdorff

        # append the dictionary to list of dictionaries (each dictionary is per patient)
        data.append(left_mean_DTA)
        data.append(left_HD)
        data.append(right_mean_DTA)
        data.append(right_HD)

    # convert list of dictionaries to pandas dataframe file 
    df = pd.DataFrame(data)
    # save df to csv 
    dist_metrics_df = os.path.join(base_dir, "dist_metrics")
    if not os.path.exists(dist_metrics_df):
        os.makedirs(dist_metrics_df)
    os.chdir(dist_metrics_df)
    df.to_csv("distance_metrics_full_contours.csv")
    