This repository includes the data and dashboard python code used in the user study (including one example from the study results) and the R code to analyze the provenance. 

**Compile and run the dashboard code** on your server to conduct the study.

To **process the results**, copy all folders in the **results** folder of the **dashboard code** directory to the **results** folder in the **process_data** directory, and run the python file main.py from your environment of choice.

To **analyze the results**:
                
1. copy to the **data** folder in the **analyze_data** directory, from **process_data** directory the following folders: **nodes** and **edges**, and the following files: "**df_main_analysis.csv**" and "**df_survey_results.csv**" and "**merged_df.csv**" and "**df_centrality.csv**"
2. run Part 1 of network_analysis.r code
3. run survey_analysis.r,
4. run Part 2 of network_analysis.r code after editing the lists at # ADD comment (based on the generated df_comparison.csv file)

