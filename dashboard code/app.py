from __future__ import print_function
import dash

# import Dash libraries
from dash import Dash, html, dcc, ctx

# from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import os
import glob

# Loading DataFrame libraries
import pandas as pd
import numpy as np
import math
import csv
from datetime import datetime
import json
import random


app = Dash(__name__)

# Initiation of variables
# create provenance dictionary to index actions at the end
provenance_dict = {'start': 'start',
                   'tab-1': 'a_v1', 'yearSlider.value': 'a_f1', 'period.value_Month': 'a_f2', 'tab-1_note': 'a_n1',
                   'period.value_Week': 'a_f3',
                   'select_week': 'a_d1', 'guided_select_week': 'a_d2',
                   'tab-2': 'b_v1', 'tab-2_note': 'b_n1', 'calculate': 'b_c1',
                   'select_crop': 'b_d1', 'guided_select_crop': 'b_d2',
                   'tab-2_month': 'b_f1', 'tab-2_planting': 'b_f2', 'tab-2_growing': 'b_f3', 'tab-2_harvest': 'b_f4',
                   'tab-2_distances': 'b_f5', 'tab-2_yields': 'b_f6', 'tab-2_prices': 'b_f7',
                   'tab-3': 'c_v1', 'tab-3_note': 'c_n1',
                   'tab-3_any': 'c_f1', 'tab-3_insect': 'c_f2', 'tab-3_disease': 'c_f3', 'tab-3_yield': 'c_f4',
                   'select_companion': 'c_d1', 'guided_select_companion': 'c_d2',
                   'end': 'end'}

font_size = 18
font_family = 'Droid, sans-serif'
colors = {'background': '#FFFFFF', 'text': '#000000'}  # Set background and text color to use for plots
showTicks = False
month_week_dict = {'January': [1, 5], 'February': [5, 9], 'March': [9, 13], 'April': [13, 18], 'May': [18, 22],
                   'June': [22, 27], 'July': [27, 31], 'August': [31, 35], 'September': [35, 39], 'October': [40, 43],
                   'November': [43, 47], 'December': [47, 52]}

start_time = datetime.now().strftime("%H:%M:%S")


months_range = {'01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR', '05': 'MAY', '06': 'JUN',
                '07': 'JUL', '08': 'AUG', '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}
beds = 4
height_div = "".join([str((100/beds)), '%'])
height_label_div = "".join([str((100/beds)*2), '%'])

# Decision panel default styling
bed_label_style = {'height': height_label_div}
bed_div_style = {'height': height_div}

# Default styling for the selected(leftDiv) and unselected(leftDiv_hide) view divisions
leftDiv = {'alignContent': 'center', 'width': '100%', 'height': '90%', 'display': 'inline-block'}
leftDiv_hide = {'alignContent': 'center', 'width': '100%', 'height': '90%', 'display': 'none'}

main_page = {'display': 'inline-block'}
main_page_hide = {'display': 'none'}

weather_data_dir = "assets/data/weather/"  # Directory of the weather data of Jerusalem, Palestine
climate_data_files = glob.glob(os.path.join(weather_data_dir, "jerusalem*.csv"))  # Jerusalem, Palestine weather data

survey_data_dir = "assets/survey/"  # Directory of the survey data
survey1_file = os.path.join(survey_data_dir, "survey1.csv")
survey2_file = os.path.join(survey_data_dir, "survey2.csv")
survey3_file = os.path.join(survey_data_dir, "survey3.csv")


crop_data_dir = "assets/data/crops/"  # Directory of the crop data
plant_data_file = os.path.join(crop_data_dir, "crop_info.csv")  # Information about each crop
prices_data_file = os.path.join(crop_data_dir, "prices.csv")  # Vegetable & Fruits timeseries price data
companion_data_file = os.path.join(crop_data_dir, "companion.csv")  # Crop companion data
farming_calendar_file = os.path.join(crop_data_dir, "farming_calendar.csv")  # Farming calendar data
exchange_rate = 3.7

# Read data of crop companion and convert into a numpy array matrix
companion_data = pd.read_csv(companion_data_file, index_col='Crop')

# Read data of farming calendar into a panda dataframe
farming_calendar_data = pd.read_csv(farming_calendar_file, index_col='Crop')

# Read data of farming calendar into a panda dataframe
crop_info_data = pd.read_csv(plant_data_file, index_col='Crop')
crops_name = list(crop_info_data.index.values)

# Read data of crop prices into a panda dataframe, user only data of previous year as an estimation of this year
prices_data = pd.read_csv(prices_data_file, index_col='Crop')
prices_data_current = prices_data.iloc[:, 0:12]

prices_data_current = prices_data_current.rename(columns=lambda c: months_range[c[0:2]])
prices_data_current = prices_data_current / exchange_rate
prices_data_current = prices_data_current.round(decimals=2)


def read_text(file):
    full_text = []
    with open(file) as csv_file:
        file_reader = csv.reader(csv_file, delimiter=';')
        for row in file_reader:
            if row[0] == '<br>':
                full_text.append(html.Br())
            elif '<b>' in row[0]:
                break_text = row[0].replace('</b>', '<b>').split('<b>')
                for position, word in enumerate(break_text):
                    if position % 2 == 1:
                        full_text.append(html.B(word))
                    else:
                        full_text.append(word)

                full_text.append(html.Br())
            else:
                full_text.append(row[0])
                full_text.append(html.Br())

    return full_text


consent_form_file = os.path.join(survey_data_dir, "consent_form.csv")
consent_form = read_text(consent_form_file)

tutorial_data_dir = "assets/tutorial/"  # Directory of the crop data
tutorial_files = glob.glob(os.path.join(tutorial_data_dir, "page*.csv"))

tutorial_pages = dict()
pages_titles_dict = dict()
pages_figures_dict = dict()
pages_answers_dict = dict()
pages_titles_dict[0] = '0'
pages_figures_dict[0] = ['0']
pages_answers_dict[0] = '0'
tutorial_files.sort()
for page_number, data_file in enumerate(tutorial_files):
    page_text = read_text(data_file)
    pages_figures_dict[page_number + 1] = []
    pages_answers_dict[page_number + 1] = []
    for figure_elements in page_text[0].split('=')[1:]:
        pages_figures_dict[page_number + 1].append(figure_elements)
    pages_answers_dict[page_number + 1] = page_text[2].split('=')[1]
    pages_titles_dict[page_number + 1] = page_text[4].split('=')[1]
    del page_text[:6]
    tutorial_pages[page_number+1] = page_text


# Read survey files and generate Survey pages
def read_survey(file):
    survey = dict()
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            survey[row[0]] = [row[1], row[2], row[3], row[4], row[5]]
    return survey


survey1 = read_survey(survey1_file)

survey2 = read_survey(survey2_file)

survey3 = read_survey(survey3_file)

question_items_survey1 = []
survey_1_input_list = []
survey_1_state_list = []
question_items_survey2 = []
survey_2_input_list = []
survey_2_state_list = []
question_items_survey3 = []
survey_3_input_list = []
survey_3_state_list = []


# Randomize order of questions
survey1_keys = [list(survey1.keys())[0:5], list(survey1.keys())[5:]]
survey2_keys = [list(survey2.keys())[0:5], list(survey2.keys())[5:]]
survey3_keys = [list(survey3.keys())[0:5], list(survey3.keys())[5:9], list(survey3.keys())[9:]]
random.shuffle(survey1_keys)
random.shuffle(survey1_keys)
random.shuffle(survey1_keys)

for question_group in survey1_keys:
    random_survey1_keys = list(question_group)
    random.shuffle(random_survey1_keys)
    for index, survey1_key in enumerate(random_survey1_keys):
        key_id = survey1_key.split(' ')[-1][:-1]
        survey1_question = "".join(['survey1_question_', key_id])
        radio_options = {i + 1: survey1[survey1_key][i] for i in range(0, len(survey1[survey1_key]))}
        dd_list = [html.Label(survey1_key, className='survey_questions'),
                   html.Div(dcc.RadioItems(id=survey1_question, options=radio_options, value=0, className='rb',
                                           labelClassName='radio_button_label'))]
        survey_1_input_list.append(Input(survey1_question, 'value'))
        survey_1_state_list.append(State(survey1_question, 'value'))
        question_items_survey1.append(dd_list)

for question_group in survey2_keys:
    random_survey2_keys = list(question_group)
    random.shuffle(random_survey2_keys)
    for index, survey2_key in enumerate(random_survey2_keys):
        key_id = survey2_key.split(' ')[-1][:-1]
        survey2_question = "".join(['survey2_question_', str(key_id )])
        radio_options = {i + 1: survey2[survey2_key][i] for i in range(0, len(survey2[survey2_key]))}
        dd_list = [html.Label(survey2_key, className='survey_questions'),
                   html.Div(dcc.RadioItems(id=survey2_question, options=radio_options, value=0, className='rb',
                                           labelClassName='radio_button_label'))]
        survey_2_input_list.append(Input(survey2_question, 'value'))
        survey_2_state_list.append(State(survey2_question, 'value'))
        question_items_survey2.append(dd_list)

for question_group in survey3_keys:
    random_survey3_keys = list(question_group)
    random.shuffle(random_survey3_keys)
    for index, survey3_key in enumerate(random_survey3_keys):
        q_index = index+1
        key_id = survey3_key.split(' ')[-1][:-1]
        if len(random_survey3_keys) == 2:
            if 'did not' in survey3_key:
                key_id = '_'.join([key_id, '1'])
            else:
                key_id = '_'.join([key_id, '2'])
        survey3_question = "".join(['survey3_question_', key_id])
        radio_options = {i + 1: survey3[survey3_key][i] for i in range(0, len(survey3[survey3_key]))}
        dd_list = [html.Label(survey3_key, className='survey_questions'),
                   html.Div(dcc.RadioItems(id=survey3_question, options=radio_options, value=0, className='rb',
                                           labelClassName='radio_button_label'))]
        survey_3_input_list.append(Input(survey3_question, 'value'))
        survey_3_state_list.append(State(survey3_question, 'value'))
        question_items_survey3.append(dd_list)


def read_climate(files):
    # reading all weather datasets, rows contain the following features:
    # Date (yyyy-mm-dd), maximum temperature (°C), min_temperature (°C), average_temperature (°C), dew (mm),
    # precipitation (mm), precipitation cover (%), precipitation type (rain/hail/snow), wind speed (kph),
    # wind direction angle (360°), cloud cover (%), sunrise time (hh:mm:ss), and sunset time(hh:mm:ss)
    all_data = []

    for data_file in files:
        with open(data_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0

            weather_columns = ['date', 'max_temp', 'min_temp', 'average_temp', 'dew', 'precip', 'precip_cover',
                               'precip_type', 'wind_speed', 'wind_direction', 'cloud_cover', 'sunrise', 'sunset']
            data_clim = []
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    day_list = [row[1], float(row[2]), float(row[3]), float(row[4]), float(row[8]), float(row[10]),
                                float(row[12]), row[13], float(row[17]), float(row[18]), float(row[20]),
                                row[26][-8:], row[27][-8:]]
                    data_clim.append(day_list)

                    line_count += 1
            data_frame = pd.DataFrame(data_clim, columns=weather_columns)
            all_data.append(data_frame)
    full_data = pd.concat(all_data, axis=0).reset_index(drop=True)
    return full_data


weather_data = read_climate(climate_data_files)
years_range = weather_data['date'].str[:4].astype(int)
all_years = years_range.unique()
all_years = sorted(all_years)


# Create weekly averages of all years
def weather_weekly_averaging(climate_data, year_start, year_range):
    # Filter dataframe 'climate_data' to include only selected year range 'year_data' and create the 'years' list
    years = []
    x_axis_tick_angle = 0

    for year in range(year_start, year_start + year_range, 1):
        years.append(str(year))
    year_data = climate_data[climate_data['date'].str.contains('|'.join(years))].reset_index(drop=True)
    # Select certain columns to work with
    year_data = year_data[['date', 'max_temp', 'min_temp', 'average_temp', 'precip']]
    plot = go.Figure()
    # Create and style traces
    # Weekly dataframe
    # Create a copy of the dataframe and add a 'week' column
    weekly_data = year_data.copy()
    weekly_data['week'] = 0
    # Creat a list of the week numbers with 7 dat repetitions
    week_counter = [i for i in range(1, 53) for _ in range(7)]
    # Create variables necessary to process and calculate the week averages and sums
    list_of_df = []
    week_max_temp, week_min_temp = [], []

    # Iterate the selected years
    for y in years:
            # Select the rows from the year iteration
            weekly_data_temp = weekly_data[weekly_data['date'].str.contains(y)].reset_index(drop=True)
            # Check days of year to create a copy of 'weeks_counter', add 1 or 2 52 entry, set last week to 8 or 9 days
            additional_days = len(weekly_data_temp.index) - 364
            add_weeks = [52] * additional_days
            week_counter_updated = week_counter.copy()
            week_counter_updated.extend(add_weeks)
            # Update 'week' column and select the columns to work with, one for averages and one for extremities
            weekly_data_temp['week'] = week_counter_updated
            weekly_data_temp = weekly_data_temp[['max_temp', 'min_temp', 'average_temp', 'precip', 'week']]
            weekly_data_average = weekly_data_temp.groupby('week').mean()
            weekly_data_average['precip'] = weekly_data_average['precip']*7
            list_of_df.append(weekly_data_average)

            weekly_max = weekly_data_temp.groupby('week')['max_temp'].max()
            weekly_min = weekly_data_temp.groupby('week')['min_temp'].min()
            week_max_temp.append(weekly_max)
            week_min_temp.append(weekly_min)
    all_dfs = pd.concat(list_of_df)
    by_row_index = all_dfs.groupby(all_dfs.index)
    weekly_data = by_row_index.mean()

    max_dfs = pd.concat(week_max_temp)
    min_dfs = pd.concat(week_min_temp)

    weekly_data.reset_index(inplace=True)
    weekly_data['week'] = 'Week ' + weekly_data['week'].astype(str)
    return weekly_data


weather_weekly_averaged = weather_weekly_averaging(weather_data, min(years_range), max(years_range)-min(years_range)+1)


# Plot weather plot
def weather_uncertainty(climate_data, year_start, year_range, period, guide):
    # Filter dataframe 'climate_data' to include only selected year range 'year_data' and create the 'years' list
    years = []
    x_axis_tick_angle = 0

    for year in range(year_start, year_start + year_range, 1):
        years.append(str(year))
    year_data = climate_data[climate_data['date'].str.contains('|'.join(years))].reset_index(drop=True)
    # Select certain columns to work with
    year_data = year_data[['date', 'max_temp', 'min_temp', 'average_temp', 'precip']]
    plot = go.Figure()
    # Create and style traces
    if period == 'Week':
        # Weekly dataframe
        # Create a copy of the dataframe and add a 'week' column
        weekly_data = year_data.copy()
        weekly_data['week'] = 0
        # Creat a list of the week numbers with 7 dat repetitions
        week_counter = [i for i in range(1, 53) for _ in range(7)]
        # Create variables necessary to process and calculate the week averages and sums
        list_of_df = []
        week_max_temp, week_min_temp = [], []
        x_axis_tick_angle = 45
        # Iterate the selected years
        for y in years:
            # Select the rows from the year iteration
            weekly_data_temp = weekly_data[weekly_data['date'].str.contains(y)].reset_index(drop=True)
            # Check days of year to create a copy of 'weeks_counter', add 1 or 2 52 entry, set last week to 8 or 9 days
            additional_days = len(weekly_data_temp.index) - 364
            add_weeks = [52] * additional_days
            week_counter_updated = week_counter.copy()
            week_counter_updated.extend(add_weeks)
            # Update 'week' column and select the columns to work with, one for averages and one for extremities
            weekly_data_temp['week'] = week_counter_updated
            weekly_data_temp = weekly_data_temp[['max_temp', 'min_temp', 'average_temp', 'precip', 'week']]
            weekly_data_average = weekly_data_temp.groupby('week').mean()
            weekly_data_average['precip'] = weekly_data_average['precip']*7
            list_of_df.append(weekly_data_average)

            weekly_max = weekly_data_temp.groupby('week')['max_temp'].max()
            weekly_min = weekly_data_temp.groupby('week')['min_temp'].min()
            week_max_temp.append(weekly_max)
            week_min_temp.append(weekly_min)
        all_dfs = pd.concat(list_of_df)
        by_row_index = all_dfs.groupby(all_dfs.index)
        weekly_data = by_row_index.mean()

        max_dfs = pd.concat(week_max_temp)
        min_dfs = pd.concat(week_min_temp)

        weekly_max = max_dfs.groupby(level=0).max()
        weekly_min = min_dfs.groupby(level=0).min()

        weekly_data.reset_index(inplace=True)
        weekly_data['week'] = 'Week ' + weekly_data['week'].astype(str)

        # Weekly plot
        plot.add_trace(go.Bar(x=weekly_data['week'], y=weekly_data['precip'],
                              hovertemplate=['<b>{:.1f} mm</b>'.format(i) for i in weekly_data['precip']],
                              name='Precipitation ',
                              marker=dict(color="rgba(102,194,165, 0.2)")))

        plot.add_trace(go.Scatter(x=weekly_data['week'], y=weekly_data['max_temp'], name='High Temperature',
                                  hovertemplate='<b>%{y:.1f} °C</b>', line=dict(color='#d95f02', width=4)))
        plot.add_trace(go.Scatter(x=weekly_data['week'], y=weekly_data['min_temp'], name='Low Temperature',
                                  hovertemplate='<b>%{y:.1f} °C</b>', line=dict(color='#1f78b4', width=4)))
        plot.add_trace(go.Scatter(x=weekly_data['week'], y=weekly_data['average_temp'], name='Mean Temperature',
                                  hovertemplate='<b>%{y:.1f} °C</b>', line=dict(color='#7570b3', width=2)))

        plot.add_trace(go.Scatter(x=weekly_data['week'], y=weekly_max,
                                  marker=dict(symbol=136, color="#d95f02", size=15),
                                  mode='markers', hovertemplate='<b>%{y:.1f} °C</b>', name='Maximum'))
        plot.add_trace(go.Scatter(x=weekly_data['week'], y=weekly_min, mode='markers',
                                  marker=dict(symbol=135, color="#1f78b4", size=15),
                                  hovertemplate='<b>%{y:.1f} °C</b>', name='Minimum'))
    else:
        # Monthly dataframe
        month = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                 'August', 'September', 'October', 'November', 'December']
        months = ['-01-', '-02-', '-03-', '-04-', '-05-', '-06-', '-07-', '-08-', '-09-', '-10-', '-11-', '-12-']
        days = ['-01', '-02', '-03', '-04', '-05', '-06', '-07', '-08', '-09', '-10', '-11', '-12', '-13', '-14', '-15',
                '-16', '-17', '-18', '-19', '-20', '-21', '-22', '-23', '-24', '-25', '-26', '-27', '-28', '-29', '-30',
                '-31']
        day_max_temp, day_min_temp, day_high_temp, day_low_temp, day_mean_temp, day_precip = [], [], [], [], [], []
        month_max_temp, month_min_temp, month_high_temp, month_low_temp, month_mean_temp = [], [], [], [], []
        month_precip = []

        for x in months:
            month_data = year_data[year_data['date'].str.contains(x)].reset_index(drop=True)
            month_max_temp.append(max(month_data['max_temp']))
            month_min_temp.append(min(month_data['min_temp']))
            total_precip = month_data['precip'].sum() / year_range
            month_precip.append(total_precip / 10)

            month_high_temp.append(month_data['max_temp'].mean())
            month_low_temp.append(month_data['min_temp'].mean())
            month_mean_temp.append(month_data['average_temp'].mean())

            for day in days:
                day_of_month = "".join([x, day[1:]])
                day_data = year_data[year_data['date'].str.contains(day_of_month)].reset_index(drop=True)
                try:
                    day_max_temp.append(max(day_data['max_temp']))
                    day_min_temp.append(min(day_data['min_temp']))
                    day_high_temp.append(day_data['max_temp'].mean())
                    day_low_temp.append(day_data['min_temp'].mean())
                    day_mean_temp.append(day_data['average_temp'].mean())
                    day_precip.append(day_data['precip'].mean() / 10)
                except ValueError:
                    pass
        plot.add_trace(go.Bar(x=month, y=month_precip,
                              hovertemplate=['<b>{:.1f} mm</b>'.format(i * 10) for i in month_precip],
                              name='Precipitation ', marker=dict(color="rgba(102,194,165, 0.2)")))

        plot.add_trace(go.Scatter(x=month, y=month_high_temp, name='High Temperature',
                                  hovertemplate='<b>%{y:.1f} °C</b>', line=dict(color='#d95f02', width=4)))
        plot.add_trace(go.Scatter(x=month, y=month_low_temp, name='Low Temperature',
                                  hovertemplate='<b>%{y:.1f} °C</b>', line=dict(color='#1f78b4', width=4)))
        plot.add_trace(go.Scatter(x=month, y=month_mean_temp, name='Mean Temperature',
                                  hovertemplate='<b>%{y:.1f} °C</b>', line=dict(color='#7570b3', width=2)))

        plot.add_trace(go.Scatter(x=month, y=month_max_temp,
                                  mode='markers', marker=dict(symbol=136, color="#d95f02", size=15),
                                  hovertemplate='<b>%{y:.1f} °C</b>',
                                  name='Maximum'))
        plot.add_trace(go.Scatter(x=month, y=month_min_temp,
                                  mode='markers', marker=dict(symbol=135, color="#1f78b4", size=15),
                                  hovertemplate='<b>%{y:.1f} °C</b>',
                                  name='Minimum'))

    # Update the layout
    plot.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], clickmode='event+select',
                       hovermode="x unified", font=dict(color=colors['text'], size=font_size, family=font_family),
                       dragmode='lasso', xaxis_tickangle=x_axis_tick_angle)
    plot.update_xaxes(title=period)
    plot.update_yaxes(showticklabels=showTicks, title='Temperature (°C)')

    return plot


# Plot crop information views temperature info
def crops_info(data, mode):
    data = data.iloc[::-1]
    if mode == 'month':
        calendar_value = data.copy()
        calendar_value = calendar_value.astype(str)
        calendar_value[data == 0] = 'not handled'
        calendar_value[data == 1] = 'planted'
        calendar_value[data == 2] = 'planted and harvested'
        calendar_value[data == 3] = 'harvested'
        colors_scale = [(0, 'rgb(247,247,247)'), (0.25, 'rgb(247,247,247)'),
                        (0.25, 'rgb(27,158,119)'), (0.5, 'rgb(27,158,119)'),
                        (0.5, 'rgb(217,95,2)'), (0.75, 'rgb(217,95,2)'),
                        (0.75, 'rgb(117,112,179)'), (1, 'rgb(117,112,179)')]
        hover_template = '%{y} is %{text} in %{x}'
        tick_vals_text = [[0.375, 1.125, 1.875, 2.625], ['None', 'Plant', 'Plant/Harvest', 'Harvest']]
        x_list = list(months_range.values())
        plot = go.Figure(data=go.Heatmap(z=data, x=x_list, y=data.index, colorscale=colors_scale, hoverongaps=False,
                                         text=calendar_value,
                                         hoverlabel=dict(font=dict(size=font_size, family=font_family)),
                                         hovertemplate=hover_template, name='',
                                         colorbar=dict(tickvals=tick_vals_text[0], ticktext=tick_vals_text[1])))
    else:
        x_list, colors_scale = [], []
        hover_template, color_bar_title = '', ''
        if mode == 'planting':
            data = data[['planting_ideal_low', 'planting_ideal_high', 'planting_min', 'planting_max']]
            colors_scale = [(0, 'rgb(242,240,247)'), (1, 'rgb(27,158,119)')]
            hover_template = '%{y} is planted at %{x} of %{z} °C'
            color_bar_title = 'Temperature (°C)'
            x_list = ['Ideal Low', 'Ideal High', 'Minimum', 'Maximum']
        elif mode == 'growing':
            data = data[['growing_ideal_low', 'growing_ideal_high', 'growing_min', 'growing_max']]
            colors_scale = [(0, 'rgb(247,247,247)'), (1, 'rgb(217,95,2)')]
            hover_template = '%{y} grows at %{x} of %{z} °C'
            color_bar_title = 'Temperature (°C)'
            x_list = ['Ideal Low', 'Ideal High', 'Minimum', 'Maximum']
        elif mode == 'harvest':
            data = data[['min_to_cultivation_weeks', 'max_to_cultivation_weeks']]
            colors_scale = [(0, 'rgb(247,247,247)'), (1, 'rgb(117,112,179)')]
            hover_template = '%{y} have %{x} of %{z} weeks'
            color_bar_title = 'Weeks'
            x_list = ['Minimum Cultivation', 'Maximum Cultivation']

        plot = go.Figure(data=go.Heatmap(z=data, x=x_list, y=data.index, colorscale=colors_scale, hoverongaps=False,
                                         hoverlabel=dict(font=dict(size=font_size, family=font_family)),
                                         hovertemplate=hover_template, name='', colorbar=dict(title=color_bar_title)))

    plot.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],
                       font_color=colors['text'], xaxis_nticks=12, yaxis_nticks=len(data.index), hovermode="x",
                       clickmode='event+select', font=dict(color=colors['text'], size=font_size, family=font_family))
    plot.update_traces(xgap=1, ygap=1)
    plot.update_xaxes(showspikes=True, side="top")
    plot.update_yaxes(showspikes=True)
    return plot


# Plot crop information views technical info
def technical_plot(data, mode):
    data = data.iloc[::-1]
    if mode == 'prices':
        colors_scale = [(0, 'rgb(247,247,247)'), (1,  'rgb(117,112,179)')]
        hover_template = '1Kg of %{y} in %{x} sells for %{z} €'
        color_bar_title = 'Euros (€/Kg)'
        x_list = list(months_range.values())

        plot = go.Figure(data=go.Heatmap(z=data, x=x_list, y=data.index, colorscale=colors_scale, hoverongaps=False,
                                         hoverlabel=dict(font=dict(size=font_size, family=font_family)),
                                         hovertemplate=hover_template, name='', colorbar=dict(title=color_bar_title)))

        plot.update_layout(font_color=colors['text'], xaxis_nticks=12, yaxis_nticks=len(data.index), hovermode="x",
                           clickmode='event+select', plot_bgcolor=colors['background'],
                           paper_bgcolor=colors['background'],
                           font=dict(color=colors['text'], size=font_size, family=font_family))

        plot.update_xaxes(showspikes=True, side="top", spikemode="across")
        plot.update_yaxes(showspikes=True)
        plot.update_traces(xgap=1, ygap=1)
    else:
        x_axis_title, metric = '', ''
        if mode == 'distances':
            x_axis_title = 'Minimum spacing between each seed/seedling (cm)'
            metric = 'cm'

        elif mode == 'yields':
            x_axis_title = 'Weight of yield per crop per season cycle (Kg)'
            metric = 'Kg'

        plot = go.Figure(go.Bar(
            x=list(data),
            y=list(data.index.values),
            orientation='h',
            hoverlabel=dict(font=dict(size=font_size, family=font_family), bgcolor='#ffffff'),
            hovertemplate='%{x} '+metric, name=''))

        plot.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],
                           font_color=colors['text'], showlegend=False,
                           yaxis_nticks=len(list(data.index.values)), xaxis_nticks=25,
                           hovermode="closest",
                           font=dict(color=colors['text'], size=font_size, family=font_family),
                           clickmode='event+select', xaxis_tickangle=-45,
                           xaxis_title=x_axis_title)
        plot.update_traces(marker_color='grey')
        plot.update_xaxes(showticklabels=showTicks)

    return plot


# Plot crop companion heatmap
def crops_heatmap(data, mode):
    companionship = data.copy()

    companionship = companionship.to_numpy()

    if mode == 'any':
        companionship[companionship < 0] = -1
        companionship[companionship > 0] = 1
    elif mode == 'insect':
        companionship[companionship < 0] = -1
        companionship[companionship == 1] = 0
        companionship[companionship > 0] = 1
    elif mode == 'disease':
        companionship[companionship < 0] = -1
        companionship[companionship == 1] = 0
        companionship[companionship == 2] = 0
        companionship[companionship > 0] = 1
    elif mode == 'yield':
        companionship[companionship < 0] = -1
        companionship[companionship == 1] = 0
        companionship[companionship == 2] = 0
        companionship[companionship == 3] = 0
        companionship[companionship > 0] = 1

    colors_scale = [(0, 'rgb(117,112,179)'), (0.3, 'rgb(117,112,179)'),
                    (0.3, 'rgb(247,247,247)'), (0.7, 'rgb(247,247,247)'),
                    (0.7, 'rgb(27,158,119)'), (1, 'rgb(27,158,119)')]

    companionship = np.flip(companionship, 0)
    companionship_value = companionship.copy()
    companionship_value = companionship_value.astype(str)
    companionship_value[companionship == 1] = 'beneficial'
    companionship_value[companionship == 0] = 'neutral'
    companionship_value[companionship == -1] = 'detrimental'

    crops_name_y = list(data.index.values)
    crops_name_y.reverse()

    plot = go.Figure(data=go.Heatmap(z=companionship, x=list(data.index.values), y=crops_name_y,
                                     colorscale=colors_scale,
                                     hoverongaps=False, hoverlabel=dict(font=dict(size=font_size, family=font_family)),
                                     text=companionship_value, hovertemplate='%{x} is %{text} to %{y}', name='',
                                     colorbar=dict(tickvals=[-0.7, 0, 0.7],
                                                   ticktext=['Detrimental', 'Neutral', 'Beneficial'])))
    plot.update_xaxes(side="top", showspikes=True)
    plot.update_yaxes(showspikes=True, spikemode="across")
    plot.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],
                       xaxis_nticks=len(crops_name_y), yaxis_nticks=len(crops_name_y), xaxis_tickangle=-45,
                       hovermode="x",
                       clickmode='event+select', font=dict(color=colors['text'], size=font_size, family=font_family))
    plot.update_traces(xgap=1, ygap=1)

    return plot


# Plot the three views, weather line plot, crops_info(calendar and technical), companion heatmap
weather_plot = weather_uncertainty(weather_data, min(years_range), max(years_range)-min(years_range)+1, 'Month',
                                   'No Guidance')
farming_calendar_plot = crops_info(farming_calendar_data, 'month')
technical_comparison = technical_plot(crop_info_data['planting_distance'], 'distances')
crops_companion = crops_heatmap(companion_data, 'any')

# Generate dropdown list for beds division panel in rightDiv1
week_range = [f'Week {i}' for i in range(1, 53)]
dropdown_items = []
week_input_list = []
crop_input_list = []
companion_input_list = []
state_list = []
output_list = []
for bed in range(1, beds+1, 1):
    bed_label = " ".join(['Bed', str(bed)])

    bed_week = 'week' + str(bed)
    main_crop = 'main_crop_' + str(bed)
    companion_crop = 'companion_crop_' + str(bed)
    dd_list = [html.Label(bed_label, style=bed_label_style, className='bed_label_style'),
               html.Div(dcc.Dropdown(crops_name, placeholder='Main Crop', id=main_crop), className='bed_style'),
               html.Div(dcc.Dropdown(crops_name, placeholder='Companion', id=companion_crop), className='bed_style'),
               html.Div(dcc.Dropdown(week_range, placeholder='Plant on', id=bed_week), className='bed_style_w')]
    week_input_list.append(Input(bed_week, 'value'))
    crop_input_list.append(Input(main_crop, 'value'))
    companion_input_list.append(Input(companion_crop, 'value'))
    state_list.append(State(main_crop, 'value'))
    state_list.append(State(companion_crop, 'value'))
    state_list.append(State(bed_week, 'value'))
    output_list.append(Output(main_crop, 'value'))
    output_list.append(Output(companion_crop, 'value'))
    output_list.append(Output(bed_week, 'value'))
    dropdown_items.append(dd_list)

app.layout = html.Div([
    html.Div(id='introduction', className='introduction', style=main_page, children=[
        html.Div([
            html.Div(id='page_number', style={'display': 'none'}, children='1'),
            html.Div(id='tutorial_label_container', className='tutorial_label_container', children=[
                html.Label(id='tutorial_label', className='tutorial_label',
                           children=['ConVa study on-boarding'])]),
            html.Div(id='instructions', className='instructions', children=tutorial_pages[1]),
            html.Div(id='back_tutorial_container', className='back_tutorial_container', children=[
                html.Button('Back', id='back_tutorial', className='submit-val', role='button',
                            style={'display': 'none'}),
                html.Button('Next', id='next_tutorial', className='submit-val', role='button'),
                html.Button('Start Evaluation', id='start', className='submit-val', role='button',
                            style={'display': 'none'})]),
            html.Div(id='bottom_tutorial_container', className='bottom_tutorial_container', children=[
                dcc.Input(id="answer_tutorial", type="text", placeholder="Your Answer", className='answer_tutorial'),
                html.Label('Please try again!', id='next_tutorial_error', className='next_tutorial_error')
            ]),
            html.Div(id='test_figure_container', className='test_figure_container', children=[
                html.Div(id='test_figure_container_1', className='test_figure_container_1', children=[
                    dcc.RadioItems(id='test_mode', labelClassName='test_mode_label', inputClassName='test_mode_input')
                ]),
                html.Div(id='test_figure_container_2', className='test_figure_container_2', children=[
                    dcc.Graph(id='test_figure', className='test_figure')
                ]),
                html.Div(id='test_figure_container_3', className='test_figure_container_3', children=[
                        html.Label('Year range: ', className='yearSlider_label'),
                        dcc.RangeSlider(id='test_yearSlider', className='yearSlider', min=min(years_range),
                                        max=max(years_range),
                                        step=1, value=[min(all_years), max(all_years)], allowCross=False, marks=None,
                                        tooltip={"placement": "bottom", "always_visible": True})]),
            ])
        ], className='tutorial', id='tutorial'),
        html.Div(id='task_guidance', style={'display': 'none'}),
    ]),
    html.Div(id='first_survey', className='first_survey', style=main_page_hide, children=[
        html.Div(children=[
            html.Div(children=['Participant number'], id='participant_label', className='participant_label'),
            html.Div(id='submit_consent_form', className='consent_text_div', children=[
                     html.Div(id='consent_text', className='consent_text',
                              children=consent_form),
                     html.Button('I Consent to the above', id='submit_consent_form_button',
                                 className='submit-val', role='button')])], className='consent_form', id='consent_form'),
        html.Div([
            html.Label(
                "Please read questions carefully and answer on a scale from 'Not confident at all' to 'Very confident'",
                className='survey_title'),
            html.Label(
                "Confident is having or showing assurance and self-reliance (Merriam-Webster)",
                className='survey_definitions'),
            html.Label("Please fill out all answers!", className='caution_missing', id='caution_missing1'),
            html.Div(id='submit_survey_1', className='submit_survey_1', children=[
                     html.Div(id='survey1', className='survey1',
                              children=[html.Div([rb[0], rb[1]], )
                                        for rb in question_items_survey1]),
                     html.Button('Submit Survey', id='submit-survey-1',
                                 className='submit-val', role='button')])], id='survey1_main',
            className='survey1_main')
    ]),
    html.Div(id='dashboard', className='dashboard', style=main_page_hide, children=[
        html.Div(id='topBar', className='topBar', children=[
            html.Div(id='guideSwitch', className='guideSwitch', children=[
                         dcc.Checklist(
                             options=[{'label': 'Guidance', 'value': 'Guidance',
                                       'disabled': True}],
                             inline=True, id='guide_switch', inputClassName='guide_input', labelClassName='guide_label'
                         )]),
            html.Div(id='tabs_bar', children=[
                    dcc.Tabs(id='tabs-inline', value='tab-1', children=[
                        dcc.Tab(label='Weather Analysis', value='tab-1', className='tab_style',
                                selected_className='tab_selected_style', id='tab-1'),
                        dcc.Tab(label='Crop Information', value='tab-2', className='tab_style',
                                selected_className='tab_selected_style', id='tab-2'),
                        dcc.Tab(label='Crop Companions', value='tab-3', className='tab_style',
                                selected_className='tab_selected_style', id='tab-3')], className='tabs-inline')
            ], className='tabs_bar')]),
        html.Div(id='mainDiv', className='mainDiv', children=[
            html.Div(id='rightDiv0', className='rightDiv0',
                     children=[html.Label('How confident do you feel about your decisions in this bed?',
                                              className='inter_question'),
                                   dcc.RadioItems(id='survey', options={1: 'Not confident at all', 2: 'I have doubts',
                                                                        3: 'Neutral', 4: 'Confident',
                                                                        5: 'Very confident'}, value=0, className='rb_i',
                                                  labelClassName='radio_button_label_i')]),
            html.Div(id='leftDiv', className='leftDiv', children=[
                html.Div(id='leftDiv1', className='leftDiv1', style=leftDiv, children=[
                    html.Div(id='leftDiv1_1', className='leftDiv1_1', children=[
                        dcc.Graph(id='weather', className='weather', figure=weather_plot)
                    ]),
                    html.Div(id='leftDiv1_2', className='leftDiv1_2',
                             children=[dcc.RadioItems(id='period', options={'Month': 'Monthly', 'Week': 'Weekly'},
                                                      value='Month', labelClassName='period_label',
                                                      inputClassName='period_input')]),
                    html.Div(id='leftDiv1_3', className='leftDiv1_3', children=[
                        html.Label('Year range: ', className='yearSlider_label'),
                        dcc.RangeSlider(id='yearSlider', className='yearSlider', min=min(years_range),
                                        max=max(years_range),
                                        step=1, value=[min(all_years), max(all_years)], allowCross=False, marks=None,
                                        tooltip={"placement": "bottom", "always_visible": True})])
                ]),
                html.Div(id='leftDiv2', className='leftDiv2', style=leftDiv_hide,  children=[
                    html.Div(id='leftDiv2_1', className='leftDiv2_1', children=[
                        html.Div(id='leftDiv2_1_1', className='leftDiv2_1_1',
                                 children=[dcc.RadioItems(id='calendar_mode',
                                                          options={'month': 'Farming Calendar', 'planting': 'Planting',
                                                                   'growing': 'Growing', 'harvest': 'Harvest'},
                                                          value='month', labelClassName='mode_label',
                                                          inputClassName='mode_input')]),
                        html.Div(id='leftDiv2_1_2', className='leftDiv2_1_2', children=[
                            dcc.Graph(id='farmingCalendar', className='farmingCalendar', figure=farming_calendar_plot)])
                    ]),
                    html.Div(id='leftDiv2_2', className='leftDiv2_2', children=[
                        html.Div(id='leftDiv2_2_1', className='leftDiv2_2_1',
                                 children=[dcc.RadioItems(id='technical_mode',
                                                          options={'distances': 'Planting Distances',
                                                                   'yields': 'Crops Yield', 'prices': 'Crops Prices'},
                                                          value='distances', labelClassName='mode_label',
                                                          inputClassName='mode_input')]),
                        html.Div(id='leftDiv2_2_2', className='leftDiv2_2_2', children=[
                            dcc.Graph(id='technicalInfo', className='technicalInfo', figure=technical_comparison)])])
                ]),
                html.Div(id='leftDiv3', className='leftDiv3', style=leftDiv_hide,  children=[
                    html.Div(id='leftDiv3_1', className='leftDiv3_1', children=[
                        dcc.RadioItems(id='companion_mode',
                                       options={'any': 'Any Benefit', 'insect': 'Insect Repellent',
                                                'disease': 'Disease Control', 'yield': 'Crop Yield'},
                                       value='any', labelClassName='mode_label', inputClassName='mode_input')]),
                    html.Div(id='leftDiv3_2', className='leftDiv3_2', children=[
                        dcc.Graph(id='companion', className='companion', figure=crops_companion)
                    ])
                ])
            ]),
            html.Div(id='midDiv', className='midDiv', children=[
                html.Div(id='calculator', className='calculator', children=[
                    html.Button('7', id='seven',
                                className='calculator_button', role='button'),
                    html.Button('8', id='eight',
                                className='calculator_button', role='button'),
                    html.Button('9', id='nine',
                                className='calculator_button', role='button'),
                    html.Button('÷', id='divide',
                                className='calculator_button', role='button'),
                    html.Button('4', id='four',
                                className='calculator_button', role='button'),
                    html.Button('5', id='five',
                                className='calculator_button', role='button'),
                    html.Button('6', id='six',
                                className='calculator_button', role='button'),
                    html.Button('x', id='multiply',
                                className='calculator_button', role='button'),
                    html.Button('1', id='one',
                                className='calculator_button', role='button'),
                    html.Button('2', id='two',
                                className='calculator_button', role='button'),
                    html.Button('3', id='three',
                                className='calculator_button', role='button'),
                    html.Button('-', id='subtract',
                                className='calculator_button', role='button'),
                    html.Button('=', id='sum',
                                className='calculator_button', role='button'),
                    html.Button('0', id='zero',
                                className='calculator_button', role='button'),
                    html.Button('.', id='decimal',
                                className='calculator_button', role='button'),
                    html.Button('+', id='add',
                                className='calculator_button', role='button'),
                    html.Label(id="result", children=["Ans."], className='result')
                ]),
                dcc.Textarea(id="user_note", value="Take notes here. Please do not erase any of your notes.",
                             className='user_notes')]),
            html.Div(id='rightDiv', className='rightDiv', children=[
                html.Div(id='rightDiv1', className='rightDiv1', children=[html.Div([dd[0], dd[1], dd[2], dd[3]],
                                                                                   style=bed_div_style,
                                                                                   className='bed_div_style')
                                                                          for dd in dropdown_items]),
                html.Div(id='rightDiv2', className='rightDiv2', children=[html.Button('Submit Decision',
                                                                                      id='submit_decision',
                                                                                      className='submit-val',
                                                                                      role='button')]),
                html.Div(id='rightDiv3', className='rightDiv3',
                         children=[html.Label(id='taskLabel', className='taskLabel')]),
                html.Div(id='rightDiv4', className='rightDiv4',
                         children=[html.Label(id='guidance_text', className='guidance_text',
                                              children=[html.H2('Guidance Panel')])])
            ]),
            html.Div(id='provenanceValue', style={'display': 'none'}),
            html.Div(id='intermediate_survey', style={'display': 'none'}, children=['{}']),
            html.Div(id='user_equation', style={'display': 'none'}, children=[]),
            html.Div(id='user_participant_id', style={'display': 'none'}),
            html.Div(id='session_number', style={'display': 'none'}, children=['first'])

        ])
    ]),
    html.Div(id='end_survey', className='end_survey', style=main_page_hide, children=[
        html.Label(
                "Please read questions carefully and answer on a scale from 'Not confident at all' to 'Very confident'",
                className='survey_title'),
        html.Label(
            "Confident is having or showing assurance and self-reliance (Merriam-Webster)",
            className='survey_definitions'),
        html.Label("Please fill out all answers!", className='caution_missing', id='caution_missing2'),
        html.Div(id='submit_survey_2', className='submit_survey_2', children=[

            html.Div(id='survey2', className='survey2', children=[html.Div([rb[0], rb[1]], )
                                                                  for rb in question_items_survey2]),
            html.Button('Submit Survey 2', id='submit-survey-2',
                        className='submit-val', role='button')])]),
    html.Div(id='end_survey_2', className='end_survey', style=main_page_hide, children=[
        html.Label(
                "Please read questions carefully and answer on a scale from 'Not confident at all' to 'Very confident'",
                className='survey_title'),
        html.Label(
            "Confident is having or showing assurance and self-reliance (Merriam-Webster)",
            className='survey_definitions'),
        html.Label("Please fill out all answers!", className='caution_missing', id='caution_missing3'),
        html.Div(id='submit_survey_3', className='submit_survey_2', children=[
                     html.Div(id='survey3', className='survey2', children=[html.Div([rb[0], rb[1]], )
                                                                           for rb in question_items_survey3]),
                     html.Button('Submit Survey 3', id='submit-survey-3',
                                 className='submit-val', role='button')])
    ]),
    html.Div(id='thank_you', className='thank_you', style=main_page_hide, children=[
        html.Label('Thank You!', id='end_session', className='end_session')
    ])
])


# Update the guidance
@app.callback([Output('tab-1', 'style'), Output('tab-2', 'style'), Output('tab-3', 'style'),
               Output('guidance_text', 'children')],
              [Input('tabs-inline', 'value'), Input('submit-survey-2', 'n_clicks'), week_input_list, crop_input_list,
               companion_input_list],
              [State('tabs-inline', 'value'), state_list, State('guide_switch', 'value'),
               State('taskLabel', 'children')],
              prevent_initial_call=True)
def update_guidance(tab_input, submit_click, week_input, main_crop_input, companion_input, tab_state, pending_decision,
                    guide_state, task_label):
    global farming_calendar_data, crop_info_data, prices_data_current, weather_weekly_averaged, companion_data
    chosen_crops = pending_decision[0::3]
    chosen_companion = pending_decision[1::3]
    chosen_week = pending_decision[2::3]

    def calculate_crop_guide(number_of_recommendations):
        # Profitability and weather suitability
        task_month = task_label[2].split(' ')[4]
        task_month = task_month[0:3]
        task_month = task_month.upper()
        all_crops_planted = farming_calendar_data.loc[(farming_calendar_data[task_month] == 1) |
                                                      (farming_calendar_data[task_month] == 2)]

        if len(list(all_crops_planted.index.values)) > 0:
            bed_length = int(task_label[4].split(' ')[6][0:2])
            all_distances = crop_info_data['planting_distance']
            all_yields = crop_info_data['crop_yield']
            max_cultivation = crop_info_data['max_to_cultivation_weeks']
            min_cultivation = crop_info_data['min_to_cultivation_weeks']
            profit_of_each_crop = {}
            months = {'JAN': 'January', 'FEB': 'February', 'MAR': 'March', 'APR': 'April', 'MAY': 'May', 'JUN': 'June',
                      'JUL': 'July', 'AUG': 'August', 'SEP': 'September', 'OCT': 'October', 'NOV': 'November',
                      'DEC': 'December'}
            for index, row in all_distances.items():
                if index in list(all_crops_planted.index.values):
                    total_yield = math.ceil(bed_length/(row/100))*all_yields[index]
                    harvest_start = math.floor(min_cultivation[index]/4)
                    harvest_end = math.ceil(max_cultivation[index]/4)
                    number_of_months = harvest_end - harvest_start + 1
                    yield_portions = total_yield/number_of_months
                    month_index = list(months.keys()).index(task_month)
                    if month_index + harvest_start < 12:
                        start_cultivation = list(months.keys())[month_index + harvest_start]
                    else:
                        start_cultivation = list(months.keys())[month_index + harvest_start - 12]

                    start_cultivation_i = list(months.keys()).index(start_cultivation)
                    crop_price_list = prices_data_current.loc[index].iloc[::-1]
                    total_crop_earning = 0
                    for month in range(0, number_of_months):
                        if start_cultivation_i + month < 12:
                            month_i = list(months.keys())[start_cultivation_i + month]
                            crop_price_list[month_i] * yield_portions
                            total_crop_earning += crop_price_list[month_i] * yield_portions
                        else:
                            month_i = list(months.keys())[(start_cultivation_i + month)-12]
                            total_crop_earning += crop_price_list[month_i] * yield_portions
                    profit_of_each_crop[index] = total_crop_earning

            recommended_crops = dict(sorted(profit_of_each_crop.items(), key=lambda item: item[1], reverse=True))
            list_of_recommendations = list(recommended_crops.keys())
            if len(list_of_recommendations) > number_of_recommendations:
                list_of_recommendations = list_of_recommendations[0:number_of_recommendations]
        else:
            list_of_recommendations = None

        return list_of_recommendations

    def calculate_companion_guide():
        input_bed_reference = ctx.triggered_id.split('_')
        if chosen_crops == [None] * len(chosen_crops):
            text = [html.H2('Guidance Panel')]
        else:
            if input_bed_reference[0] == 'main':
                input_bed_reference = input_bed_reference[2]
            else:
                input_bed_reference = 999
            all_recommended_crops = calculate_crop_guide(100)
            text = [html.H2('Guidance Panel')]
            check_repeated_crops = []
            for item in chosen_crops:
                if item is not None and item not in check_repeated_crops:
                    check_repeated_crops.append(item)
                    try:
                        all_recommended_crops.remove(item)
                    except ValueError:
                        pass
            if all_recommended_crops:
                for unique_crop in check_repeated_crops:
                    list_of_companions = dict()
                    for recommended_crop in all_recommended_crops:
                        companionship_value = companion_data.loc[unique_crop][recommended_crop]
                        if companionship_value > 0:
                            list_of_companions[recommended_crop] = companionship_value
                    if list_of_companions:
                        sort_companions = sorted(list_of_companions.items(), key=lambda x: x[1], reverse=True)
                        text.append('Consider planting ')
                        try:
                            if unique_crop == main_crop_input[int(input_bed_reference)-1]:
                                text.append(html.Mark(html.B(sort_companions[0][0])))
                                text.append(html.Mark(' with '))
                                text.append(html.Mark(html.B(unique_crop)))
                            else:
                                text.append(html.B(sort_companions[0][0]))
                                text.append(' with ')
                                text.append(html.B(unique_crop))
                        except IndexError:
                            text.append(html.B(sort_companions[0][0]))
                            text.append(' with ')
                            text.append(html.B(unique_crop))
                        text.append(html.Br())

        return text

    def calculate_week_guide():
        input_bed_reference = ctx.triggered_id.split('_')
        if input_bed_reference[0] == 'main':
            input_bed_reference = input_bed_reference[2]
        else:
            input_bed_reference == 999
        if chosen_crops == [None] * len(chosen_crops):
            text = [html.H2('Guidance Panel')]
        else:
            text = [html.H2('Guidance Panel')]
            check_repeated_crops = []
            for item in chosen_crops:
                if item is not None and item not in check_repeated_crops:
                    mark_week = 0
                    check_repeated_crops.append(item)
                    indices = [i for i, x in enumerate(chosen_crops) if x == item]
                    text.append('Consider planting ')
                    if len(indices) > 1:
                        text.append(html.B('beds '))
                    else:
                        text.append(html.B('bed '))
                    for bed_index in indices:
                        if str(bed_index+1) == str(input_bed_reference):
                            text.append(html.Mark(html.B(str(bed_index+1))))  # Bed number based on (and highlight)
                            mark_week = 1
                        else:
                            text.append(html.B(str(bed_index+1)))  # Bed number based on
                        text.append(' ')
                    text.append('in ')
                    crop_data_planting = crop_info_data[['planting_ideal_high', 'planting_ideal_low']].loc[item]
                    suitable_weeks = []
                    suitable_week_range = month_week_dict[task_label[2].split(' ')[4]]
                    for week_index, week_averages in weather_weekly_averaged.iterrows():
                        if week_averages['min_temp'] > crop_data_planting['planting_ideal_low']:
                            suitable_weeks.append(week_index+1)
                    suitable_weeks_dict = dict()
                    if task_label[2].split(' ')[4] == 'December':
                        suitable_weeks = [suitable_week for suitable_week in suitable_weeks
                                          if suitable_week >= suitable_week_range[0] or
                                          suitable_week <= suitable_week_range[1]-48]
                    else:
                        suitable_weeks = [suitable_week for suitable_week in suitable_weeks
                                          if suitable_week >= suitable_week_range[0]]
                        suitable_weeks = [suitable_week for suitable_week in suitable_weeks
                                          if suitable_week <= suitable_week_range[1]+4]

                    for week_counter, week in enumerate(suitable_weeks):
                        counter = 0
                        year_loop = 0
                        for next_week in range(suitable_weeks[week_counter], week+len(suitable_weeks) + 1):
                            if year_loop == 0:
                                try:
                                    if next_week == suitable_weeks[week_counter + counter]:
                                        counter += 1
                                    else:
                                        suitable_weeks_dict[week] = counter
                                        break
                                except IndexError:
                                    week_counter -= 52
                                    year_loop = 1
                            else:
                                try:
                                    if next_week == suitable_weeks[week_counter + counter]:
                                        counter += 1
                                    else:
                                        suitable_weeks_dict[week] = counter
                                        break
                                except IndexError:
                                    suitable_weeks_dict[week] = counter
                                    break

                    if suitable_weeks_dict:
                        best_suitable_week = max(suitable_weeks_dict, key=suitable_weeks_dict.get)
                        suggested_week = ' '.join(['Week ', str(best_suitable_week)])

                        if str(bed_index+1) == str(input_bed_reference):
                            text.append(html.Mark(html.B(suggested_week)))
                        else:
                            text.append(html.B(suggested_week))
                        text.append(html.Br())
                    else:
                        index_of_last = len(text) - 1 - text[::-1].index('Consider planting ')
                        text = text[0:index_of_last]

        return text

    guide_text = dash.no_update

    tab_1_style = {'backgroundColor': '#FFFFFF'}
    tab_2_style = {'backgroundColor': '#FFFFFF'}
    tab_3_style = {'backgroundColor': '#FFFFFF'}

    if ctx.triggered_id == 'submit-survey-2':
        guide_text = [html.H2('Guidance Panel')]
    else:
        if guide_state == ['Guidance']:
            if tab_state == 'tab-1':
                guide_text = calculate_week_guide()
            elif tab_state == 'tab-2':
                recommended_list = calculate_crop_guide(3)
                if recommended_list:
                    guide_text = [html.H2('Guidance Panel'), 'Consider the following crops for ',
                                  task_label[2].split(' ')[4], ':', html.Br()]
                    for i, crop in enumerate(recommended_list):
                        guide_text.append(str(i + 1))
                        guide_text.append('. ')
                        guide_text.append(html.B(crop))

                        guide_text.append(html.Br())
                else:
                    guide_text = [html.H2('Guidance Panel')]
            elif tab_state == 'tab-3':
                guide_text = calculate_companion_guide()
    if ctx.triggered_id[0:4] == 'main' and guide_state == ['Guidance']:
        if tab_state == 'tab-1' and main_crop_input[int(ctx.triggered_id[10:])-1] is not None:
            tab_3_style = {'backgroundColor': '#FFFF00'}
        elif tab_state == 'tab-2' and main_crop_input[int(ctx.triggered_id[10:])-1] is not None:
            tab_1_style = {'backgroundColor': '#FFFF00'}
            tab_3_style = {'backgroundColor': '#FFFF00'}
        elif tab_state == 'tab-3' and main_crop_input[int(ctx.triggered_id[10:])-1] is not None:
            tab_1_style = {'backgroundColor': '#FFFF00'}
    elif ctx.triggered_id[0:4] == 'comp' and guide_state == ['Guidance']:
        if tab_state == 'tab-3' or tab_state == 'tab-2':
            tab_1_style = {'backgroundColor': '#FFFF00'}
    return tab_1_style, tab_2_style, tab_3_style, guide_text


# Calculator
@app.callback([Output('user_equation', 'children'),
               Output('result', 'children')],
              [Input('zero', 'n_clicks'),
     Input('one', 'n_clicks'),
     Input('two', 'n_clicks'),
     Input('three', 'n_clicks'),
     Input('four', 'n_clicks'),
     Input('five', 'n_clicks'),
     Input('six', 'n_clicks'),
     Input('seven', 'n_clicks'),
     Input('eight', 'n_clicks'),
     Input('nine', 'n_clicks'),
     Input('subtract', 'n_clicks'),
     Input('add', 'n_clicks'),
     Input('divide', 'n_clicks'),
     Input('multiply', 'n_clicks'),
     Input('decimal', 'n_clicks'),
     Input('sum', 'n_clicks'), Input('submit-survey-2', 'n_clicks')],
              [State('result', 'children'), State('user_equation', 'children')],
              prevent_initial_call=True)
def calculate(zero, one, two, three, four, five, six, seven, eight, nine, subtract, add, divide, multiply,
              decimal, summation, submit_click, result, user_equation):
    numbers_dict = dict(
        {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
         'nine': 9, 'subtract': '-', 'add': '+', 'multiply': '*', 'divide': '/', 'decimal': '.',
         'sum': '='})
    operations_list = ['-', '+', '/', '*']
    equation_result = ''
    if ctx.triggered_id == 'submit-survey-2':
        value_result = 'Ans.'
    elif ctx.triggered_id != 'sum':
        user_equation.append(str(numbers_dict[ctx.triggered_id]))
        value_result = ''.join(user_equation)
    else:
        number_digits = ''
        equation_list = []
        value_result = ''
        for item in user_equation:
            if item not in operations_list:
                number_digits = number_digits + str(item)
            else:
                try:
                    equation_list.append(float(number_digits))
                except ValueError:
                    value_result = 'error'
                    break
                number_digits = ''
                equation_list.append(item)
        if value_result != 'error':
            try:
                equation_list.append(float(number_digits))
                equation_result = equation_list[0]
            except ValueError:
                value_result = 'error'

        for item_index, item in enumerate(equation_list):
            if value_result == 'error':
                user_equation = []
                break
            if item == '/':
                try:
                    equation_result = equation_result/equation_list[item_index+1]
                except ZeroDivisionError:
                    value_result = 'error'
                    user_equation = []
                    break
            elif item == '*':
                equation_result = equation_result * equation_list[item_index + 1]
            elif item == '+':
                equation_result = equation_result + equation_list[item_index + 1]
            elif item == '-':
                equation_result = equation_result - equation_list[item_index + 1]
            else:
                pass
        user_equation = []

        if value_result != 'error':
            equation_result = round(equation_result, 2)
            value_result = str(equation_result)

    return user_equation, value_result


# Consent form
@app.callback([Output('consent_form', 'style'), Output('survey1_main', 'style')],
              Input('submit_consent_form_button', 'n_clicks'), prevent_initial_call=True)
def consent_to_study(consent):
    return {'display': 'none'}, {'display': 'inline-block'}


# Move within tutorial
@app.callback(
    [Output('test_figure_container_1', 'children'),
     Output('test_figure_container_3', 'style'),
     Output('test_figure_container', 'style'),
     Output('test_figure', 'figure'),
     Output('next_tutorial_error', 'style'),
     Output('instructions', 'children'),
     Output('answer_tutorial', 'value'),
     Output('answer_tutorial', 'style'),
     Output('start', 'style'),
     Output('bottom_tutorial_container', 'style'),
     Output('page_number', 'children'),
     Output('back_tutorial', 'style'),
     Output('next_tutorial', 'style'),
     Output('tutorial_label', 'children')],
    [Input('back_tutorial', 'n_clicks'),
     Input('next_tutorial', 'n_clicks'),
     Input('test_mode', 'value'),
     Input('test_yearSlider', 'value')],
    [State('answer_tutorial', 'value'),
     State('page_number', 'children'), State('test_mode', 'value'), State('test_yearSlider', 'value')],
    prevent_initial_call=True)
def move_in_tutorial(back_button, next_button, test_mode, yslider, answer, current_page_number, current_test_mode,
                     current_yslider):
    this_page = int(current_page_number)
    next_page = this_page+1
    last_page = this_page-1
    if this_page == 1:
        last_page = 1
    back_tutorial_style = dash.no_update
    next_tutorial_style = dash.no_update
    figure_style = dash.no_update
    figure = dash.no_update
    error_text = dash.no_update
    instructions = dash.no_update
    answer_text = dash.no_update
    answer_box = dash.no_update
    start_button = dash.no_update
    bottom_style = dash.no_update
    tutorial_title = dash.no_update
    test_figure_container_1 = dash.no_update
    test_figure_container_3 = {'display': 'none'}
    if pages_figures_dict[this_page][0] == 'weather':
        test_figure_container_3 = {'display': 'inline-block'}
    if answer is None:
        answer = 'None'
    else:
        answer = answer.replace(",", ".")
    if ctx.triggered_id == 'next_tutorial':
        if next_page == 12:
            this_page = dash.no_update
        elif pages_answers_dict[this_page] == '0' or \
                (pages_answers_dict[this_page] != '0' and
                 str(answer.strip()).lower() == str(pages_answers_dict[this_page]).lower()):
            instructions = tutorial_pages[next_page]
            this_page += 1
            if this_page == len(list(tutorial_pages.keys())):
                start_button = {'display': 'inline-block'}
            if pages_figures_dict[this_page] == ['0'] and pages_figures_dict[this_page-1] != ['0']:
                figure_style = {'display': 'none'}
                figure = dash.no_update
                error_text = {'display': 'none'}
                bottom_style = {'display': 'none'}
                answer_text = ''
                answer_box = {'display': 'none'}
                bottom_style = {'display': 'none'}
            elif pages_figures_dict[this_page] != ['0'] and pages_figures_dict[this_page-1] == ['0']:
                figure_style = {'display': 'inline-block'}
                figure = dash.no_update
                error_text = {'display': 'none'}
                if pages_answers_dict[this_page] != '0':
                    answer_text = ''
                    answer_box = {'display': 'inline-block'}
                    bottom_style = {'display': 'inline-block'}
            elif pages_figures_dict[this_page] != ['0'] and pages_figures_dict[this_page-1] != ['0']:
                figure = dash.no_update
                error_text = {'display': 'none'}
                if pages_answers_dict[this_page] != '0':
                    answer_text = ''
                    answer_box = {'display': 'inline-block'}
                    bottom_style = {'display': 'inline-block'}
                else:
                    answer_text = ''
                    answer_box = {'display': 'none'}
                    bottom_style = {'display': 'none'}
        elif pages_answers_dict[this_page] != '0' \
                and str(answer.strip()).lower() != str(pages_answers_dict[this_page]).lower():
            error_text = {'display': 'inline-block'}
            this_page = dash.no_update
    elif ctx.triggered_id == 'back_tutorial':
        instructions = tutorial_pages[last_page]
        this_page -= 1
        if this_page == len(list(tutorial_pages.keys()))-1:
            start_button = {'display': 'none'}
        if pages_figures_dict[this_page] == ['0'] and pages_figures_dict[this_page+1] != ['0']:
            figure_style = {'display': 'none'}
            figure = dash.no_update
            error_text = {'display': 'none'}
            bottom_style = {'display': 'none'}
            answer_text = ''
            answer_box = {'display': 'none'}
            bottom_style = {'display': 'none'}
        elif pages_figures_dict[this_page] != ['0'] and pages_figures_dict[this_page+1] == ['0']:
            figure_style = {'display': 'inline-block'}
            figure = dash.no_update
            error_text = {'display': 'none'}
            bottom_style = {'display': 'inline-block'}
            if pages_answers_dict[this_page] != '0':
                answer_text = ''
                answer_box = {'display': 'inline-block'}
                bottom_style = {'display': 'inline-block'}
            else:
                answer_text = dash.no_update
                answer_box = dash.no_update
                bottom_style = dash.no_update
        elif pages_figures_dict[this_page] != ['0'] and pages_figures_dict[this_page+1] != ['0']:
            figure_style = dash.no_update
            figure = dash.no_update
            error_text = {'display': 'none'}
            if pages_answers_dict[this_page] != '0':
                answer_text = ''
                answer_box = {'display': 'inline-block'}
                bottom_style = {'display': 'inline-block'}
            else:
                answer_text = ''
                answer_box = {'display': 'none'}
                bottom_style = {'display': 'none'}

    if ctx.triggered_id == 'test_yearSlider':
        test_figure_container_3 = {'display': 'inline-block'}
        number_of_years = yslider[1] - yslider[0] + 1  # year range
        starting_year = yslider[0]
        figure = weather_uncertainty(weather_data, starting_year, number_of_years, current_test_mode, 'No Guidance')
        this_page = dash.no_update
    elif ctx.triggered_id == 'test_mode':
        if pages_figures_dict[this_page] == ['companion']:
            figure = crops_heatmap(companion_data[0:10][:], test_mode)
        elif pages_figures_dict[this_page] == ['calendar']:
            if test_mode != 'month':
                figure = crops_info(crop_info_data[:][0:10], test_mode)
            else:
                figure = crops_info(farming_calendar_data[:][0:10], test_mode)
        elif pages_figures_dict[this_page] == ['technical']:
            if test_mode == 'prices':
                figure = technical_plot(prices_data_current[0:16][:], test_mode)
            elif test_mode == 'yields':
                figure = technical_plot(crop_info_data[0:16]['crop_yield'], test_mode)
            elif test_mode == 'distances':
                figure = technical_plot(crop_info_data[0:16]['planting_distance'], test_mode)
        elif pages_figures_dict[this_page] == ['weather']:
            test_figure_container_3 = {'display': 'inline-block'}
            number_of_years = current_yslider[1] - current_yslider[0] + 1  # year range
            starting_year = current_yslider[0]
            figure = weather_uncertainty(weather_data, starting_year, number_of_years, test_mode, 'No Guidance')
        this_page = dash.no_update
    elif ctx.triggered_id != 'test_mode' and this_page != dash.no_update:
        if pages_figures_dict[this_page] == ['companion']:
            figure = crops_heatmap(companion_data[0:10][0:10], 'any')
            test_figure_container_1 = [dcc.RadioItems(id='test_mode',
                                                      options={'any': 'Any Benefit', 'insect': 'Insect Repellent',
                                                               'disease': 'Disease Control', 'yield': 'Crop Yield'},
                                                      value='any', labelClassName='test_mode_label',
                                                      inputClassName='test_mode_input')]
        elif pages_figures_dict[this_page] == ['calendar']:
            figure = crops_info(farming_calendar_data[:][0:10], 'month')
            test_figure_container_1 = [dcc.RadioItems(id='test_mode',
                                                      options={'month': 'Farming Calendar', 'planting': 'Planting',
                                                               'growing': 'Growing', 'harvest': 'Harvest'},
                                                      value='month', labelClassName='test_mode_label',
                                                      inputClassName='test_mode_input')]
        elif pages_figures_dict[this_page] == ['technical']:
            figure = technical_plot(crop_info_data[0:16]['planting_distance'], 'distances')
            test_figure_container_1 = [dcc.RadioItems(id='test_mode',
                                                          options={'distances': 'Planting Distances',
                                                                   'yields': 'Crops Yield', 'prices': 'Crops Prices'},
                                                          value='distances', labelClassName='test_mode_label',
                                                          inputClassName='test_mode_input')]
        elif pages_figures_dict[this_page] == ['weather']:
            test_figure_container_3 = {'display': 'inline-block'}
            number_of_years = current_yslider[1] - current_yslider[0] + 1  # year range
            starting_year = current_yslider[0]
            figure = weather_uncertainty(weather_data, starting_year, number_of_years, 'Month', 'No Guidance')
            test_figure_container_1 = [dcc.RadioItems(id='test_mode', options={'Month': 'Monthly', 'Week': 'Weekly'},
                                                      value='Month', labelClassName='test_mode_label',
                                                      inputClassName='test_mode_input')]
        tutorial_title = pages_titles_dict[this_page]
        if this_page == 1:
            back_tutorial_style = {'display': 'none'}
        elif this_page == 2:
            back_tutorial_style = {'display': 'inline-block'}
        if len(list(tutorial_pages.keys())) == this_page:
            next_tutorial_style = {'display': 'none'}
        elif len(list(tutorial_pages.keys())) == this_page + 1:
            next_tutorial_style = {'display': 'inline-block'}
    if this_page != dash.no_update and pages_figures_dict[this_page][0] != 'weather':
        test_figure_container_3 = {'display': 'none'}
    return test_figure_container_1, test_figure_container_3, figure_style, figure, error_text, instructions, \
           answer_text, answer_box,  start_button, bottom_style, this_page, back_tutorial_style, next_tutorial_style, \
           tutorial_title


# Submit Decision and move to another page.
@app.callback(
    [Output('caution_missing1', 'style'), Output('caution_missing2', 'style'), Output('caution_missing3', 'style'),
     Output('participant_label', 'children'), Output('task_guidance', 'children'), Output('introduction', 'style'),
     Output('first_survey', 'style'),
     Output('dashboard', 'style'), Output('end_survey', 'style'), Output('end_survey_2', 'style'),
     Output('thank_you', 'style'), Output('user_participant_id', 'children'),
     Output('taskLabel', 'children'),
     Output('rightDiv4', 'style'), Output('guide_switch', 'value'), Output('session_number', 'children'),
     output_list],
    [Input('start', 'n_clicks'), Input('submit_decision', 'n_clicks'), Input('submit-survey-1', 'n_clicks'),
     Input('submit-survey-2', 'n_clicks'), Input('submit-survey-3', 'n_clicks')],
    [State('intermediate_survey', 'children'), State('user_note', 'value'), State('user_participant_id', 'children'),
     state_list, survey_1_state_list, survey_2_state_list, survey_3_state_list, State('session_number', 'children'),
     State('task_guidance', 'children')],
    prevent_initial_call=True)
def move_pages(start_button, val_button, survey1_button, survey2_button, survey3_button, inter_survey,
               user_note, upi,
               decision, survey_1_answers, survey_2_answers, survey_3_answers, current_session, task_guide_status):
    new_beds_value = len(decision) * [dash.no_update]


    # Read task files and generate Survey pages
    def read_task(file):
        task_list = []
        with open(file) as task_file_read:
            task_reader = csv.reader(task_file_read, delimiter=';')
            line = 0
            for task_row in task_reader:
                if line == 0:
                    task_list.append(html.B(task_row[0]))
                    task_list.append(html.Br())
                    line += 1
                elif line == 1:
                    task_list.append(task_row[0])
                    task_list.append(html.Br())
                    line += 1
                elif line == 2:
                    task_list.append(task_row[0])
                    task_list.append(html.Sup(2))
                    task_list.append(html.Br())
                    line += 1
                elif line > 2 and line < 8 :
                    task_list.append(task_row[0])
                    task_list.append(html.Br())
                elif line == 8:
                    task_list.append(task_row[0])
                    task_list.append(html.Br())
                else:
                    task_list.append(task_row[0])
                    task_list.append(task_row[0])

        return task_list

    def tracking_combinations(file, count):
        open_yet = []
        with open(file, 'r') as tracker_file:
            tracker_reader = csv.reader(tracker_file, delimiter=',')
            header = next(tracker_reader)
            combinations_counter = next(tracker_reader)
            for number, assign in zip(combinations_counter, header):
                if int(number) < count:
                    open_yet.append(assign)
        return open_yet

    if 'start' == ctx.triggered_id:
        # Create unique user participant id number and create directory to save results
        user_participant_id = str(random.randint(1000000, 90000000))
        new_path = os.path.join('results/', user_participant_id)
        os.mkdir(new_path)

        task_data_dir = "assets/task/"  # Directory of the task data
        assignment_tracker_file = 'assignment_tracker.csv'
        assignment_tracker_file_path = os.path.join(task_data_dir, assignment_tracker_file)

        # Read task/combination tracker to check which is closed (reached 5, then incremental)
        open_combination = []
        for repetitions in range(5, 200):
            if not open_combination:
                open_combination = tracking_combinations(assignment_tracker_file_path, repetitions)
            else:
                break

        # Choose a random task/guide combination from open combinations
        choose_rand_combination = random.randint(0, len(open_combination)-1)
        task_guide_combination = open_combination[choose_rand_combination]

        # Write down combination in file
        path = os.path.join('results/', user_participant_id)
        file_name = '_'.join(['combination', user_participant_id, '.txt'])
        save_path = os.path.join(path, file_name)
        with open(save_path, "w") as text_file:
            text_file.write(json.dumps(task_guide_combination))

        # Set task and guidance for first session
        combination_indices = task_guide_combination.split('_')

        chosen_task = combination_indices[0]
        guide_on = combination_indices[1]
        task_guide_record = ''.join([combination_indices[0], combination_indices[1]])

        # Update combination tracker
        combination = pd.read_csv(assignment_tracker_file_path, delimiter=',')
        combination[task_guide_combination] = combination[task_guide_combination]+1

        # Writing into the tracker
        combination.to_csv(assignment_tracker_file_path, index=False)
        return dash.no_update, dash.no_update, dash.no_update, ['Participant ID: {}'.format(user_participant_id)], \
               task_guide_record, main_page_hide, main_page, \
               dash.no_update, dash.no_update, \
               dash.no_update, dash.no_update, \
               user_participant_id, dash.no_update, dash.no_update, dash.no_update, dash.no_update, new_beds_value
    elif 'submit-survey-1' == ctx.triggered_id:
        if 0 in survey_1_answers:
            return {'display': 'inline-block'}, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update, \
                   dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update, new_beds_value
        else:
            path = os.path.join('results/', upi)
            file_name = '_'.join(['survey1', upi, '.txt'])
            save_path = os.path.join(path, file_name)
            q_and_a = [str(survey_1_state_list), survey_1_answers]
            with open(save_path, "w") as text_file:
                text_file.write(json.dumps(q_and_a))

            chosen_task = task_guide_status[0]
            guide_on = task_guide_status[1]
            guide_disabled_ref = {0: ['No Guidance'], 1: ['Guidance']}
            guide_div_ref = {0: ['none'], 1: ['inline-block']}
            guidance_box = {'display': guide_div_ref[int(guide_on)]}

            # Read chosen task
            task_data_dir = "assets/task/"  # Directory of the task data
            task_file = ''.join(['task', chosen_task, '.csv'])
            task_data_file = os.path.join(task_data_dir, task_file)

            task = read_task(task_data_file)

            task_label = [text for text in task]

            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update, main_page_hide, main_page, dash.no_update, \
                   dash.no_update, \
                   dash.no_update, dash.no_update, task_label, guidance_box, guide_disabled_ref[int(guide_on)], \
                   dash.no_update, new_beds_value
    elif 'submit_decision' == ctx.triggered_id and None not in decision:
        # Save the results
        path = os.path.join('results/', upi)
        file_name = ''
        file_name_decision = ''
        file_name_notes = ''
        if current_session == ['first']:
            file_name = '_'.join(['survey_inter_1_',  upi, '.txt'])
            file_name_decision = '_'.join(['decision_1_', upi, '.txt'])
            file_name_notes = '_'.join(['user_note_1_', upi, '.txt'])
            second_survey_style = main_page
            third_survey_style = dash.no_update
        elif current_session == ['second']:
            file_name = '_'.join(['survey_inter_2_',  upi, '.txt'])
            file_name_decision = '_'.join(['decision_2_', upi, '.txt'])
            file_name_notes = '_'.join(['user_note_2_', upi, '.txt'])
            second_survey_style = dash.no_update
            third_survey_style = main_page

        # Write to folder the intermediate survey results from session
        save_path = os.path.join(path, file_name)
        intermediate_survey = json.loads(inter_survey[0])
        with open(save_path, "w") as text_file:
            text_file.write(json.dumps(intermediate_survey))

        # Write to folder the user decisions from session
        save_path = os.path.join(path, file_name_decision)
        with open(save_path, "w") as text_file:
            text_file.write(json.dumps(decision))

        # Write to folder user's notes from session
        save_path = os.path.join(path, file_name_notes)
        with open(save_path, "w") as text_file:
            text_file.write(json.dumps(user_note))
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
               dash.no_update, main_page_hide, second_survey_style, \
               third_survey_style, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
               dash.no_update, new_beds_value
    elif 'submit-survey-2' == ctx.triggered_id:
        if 0 in survey_2_answers:
            return dash.no_update, {'display': 'inline-block'}, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update, \
                   dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update, new_beds_value
        else:
            path = os.path.join('results/', upi)
            file_name = '_'.join(['survey2',  upi, '.txt'])
            save_path = os.path.join(path, file_name)
            q_and_a = [str(survey_2_state_list), survey_2_answers]
            with open(save_path, "w") as text_file:
                text_file.write(json.dumps(q_and_a))

            # Read user's next combination from file
            path = os.path.join('results/', upi)
            combination_data_file = '_'.join(['combination', upi, '.txt'])
            combination_data_file_path = os.path.join(path, combination_data_file)
            guide_disabled_ref = {0: ['No Guidance'], 1: ['Guidance']}
            guide_div_ref = {0: ['none'], 1: ['inline-block']}
            with open(combination_data_file_path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                second_combination = next(csv_reader)
            combination_indices = second_combination[0].split('_')

            chosen_task = combination_indices[2]
            guide_on = combination_indices[3]
            guidance_box = {'display': guide_div_ref[int(guide_on)]}
            task_guide_record = ''.join([combination_indices[2], combination_indices[3]])
            # Read chosen task
            task_data_dir = "assets/task/"  # Directory of the task data
            task_file = ''.join(['task', chosen_task, '.csv'])
            task_data_file = os.path.join(task_data_dir, task_file)

            task = read_task(task_data_file)
            task_label = [text for text in task]
            new_beds_value = len(decision)*[None]

            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, task_guide_record, \
                   dash.no_update, dash.no_update, main_page, main_page_hide, dash.no_update, \
                   dash.no_update, dash.no_update, task_label, guidance_box, guide_disabled_ref[int(guide_on)], \
                   ['second'], new_beds_value
    elif 'submit-survey-3' == ctx.triggered_id:
        if 0 in survey_3_answers:
            return dash.no_update, dash.no_update, {'display': 'inline-block'}, dash.no_update, dash.no_update, \
                   dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update, \
                   dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update, new_beds_value
        else:
            path = os.path.join('results/', upi)
            file_name = '_'.join(['survey3',  upi, '.txt'])
            save_path = os.path.join(path, file_name)
            q_and_a = [str(survey_3_state_list), survey_3_answers]
            with open(save_path, "w") as text_file:
                text_file.write(json.dumps(q_and_a))
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   main_page_hide, main_page, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update, new_beds_value
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
               dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
               dash.no_update, dash.no_update, dash.no_update, dash.no_update, new_beds_value


# Move between tabs/views
@app.callback([Output('leftDiv1', 'style'),
               Output('leftDiv2', 'style'),
               Output('leftDiv3', 'style'), Output('tabs-inline', 'value')],
              [Input('tabs-inline', 'value'), Input('submit-survey-2', 'n_clicks')],
              prevent_initial_call=True)
def render_content(tab, submit_click):
    if 'submit-survey-2' == ctx.triggered_id:
        return leftDiv, leftDiv_hide, leftDiv_hide, 'tab-1'
    if tab == 'tab-1':
        return leftDiv, leftDiv_hide, leftDiv_hide, dash.no_update
    elif tab == 'tab-2':
        return leftDiv_hide, leftDiv, leftDiv_hide, dash.no_update
    elif tab == 'tab-3':
        return leftDiv_hide, leftDiv_hide, leftDiv, dash.no_update


# Update weather figure
@app.callback(
    [Output('weather', 'figure'), Output('yearSlider', 'value'), Output('period', 'value')],
    [Input('yearSlider', 'value'), Input('period', 'value'), Input('submit-survey-2', 'n_clicks')],
    [State('guide_switch', 'value'),
     State('yearSlider', 'value'),
     State('period', 'value'),
     state_list],
    prevent_initial_call=True)
def update_weather_plot(update_year_range, new_period, submit_click, guide, year_range, period, main_crops):
    global weather_data, years_range
    number_of_years = 0
    starting_year = 0
    which_input = list(ctx.triggered_prop_ids.keys())
    if 'submit-survey-2' == ctx.triggered_id:
        weather_plot_update = weather_uncertainty(weather_data, min(years_range),
                                                  max(years_range) - min(years_range) + 1, 'Month', guide[0])
        return weather_plot_update, [min(all_years), max(all_years)], 'Month'
    else:
        if which_input[0] == 'yearSlider.value':
            number_of_years = update_year_range[1] - update_year_range[0] + 1  # year range
            starting_year = update_year_range[0]
        elif which_input[0] == 'period.value':
            number_of_years = year_range[1] - year_range[0] + 1  # year range
            starting_year = year_range[0]

        weather_plot_update = weather_uncertainty(weather_data, starting_year, number_of_years, period, guide[0])

        return weather_plot_update, dash.no_update, dash.no_update


# Update farmingCalendar based on mode selection
@app.callback(
    [Output('farmingCalendar', 'figure'), Output('calendar_mode', 'value')],
    [Input('calendar_mode', 'value'),  Input('submit-survey-2', 'n_clicks')],
    prevent_initial_call=True)
def update_calendar(mode, submit_click):
    global farming_calendar_data, crop_info_data
    if 'submit-survey-2' == ctx.triggered_id:
        calendar_data = farming_calendar_data.copy()
        farming_calendar_plot_update = crops_info(calendar_data, 'month')
        return farming_calendar_plot_update, 'month'
    else:
        if mode == 'month':
            calendar_data = farming_calendar_data.copy()
        else:  # mode == 'harvest' || 'planting' || 'growing'
            calendar_data = crop_info_data.copy()

        farming_calendar_plot_update = crops_info(calendar_data, mode)
        return farming_calendar_plot_update, dash.no_update


# Update technical info based on mode selection
@app.callback(
    [Output('technicalInfo', 'figure'),  Output('technical_mode', 'value')],
    [Input('technical_mode', 'value'),  Input('submit-survey-2', 'n_clicks')],
    prevent_initial_call=True)
def update_technical(mode, submit_click):
    global crop_info_data, prices_data_current
    technical_comparison_update = ''
    if 'submit-survey-2' == ctx.triggered_id:
        technical_comparison_update = technical_plot(crop_info_data['planting_distance'], 'distances')
        return technical_comparison_update, 'distances'
    else:
        if mode == 'distances':
            technical_comparison_update = technical_plot(crop_info_data['planting_distance'], mode)
        elif mode == 'yields':
            technical_comparison_update = technical_plot(crop_info_data['crop_yield'], mode)
        elif mode == 'prices':
            technical_comparison_update = technical_plot(prices_data_current, mode)

        return technical_comparison_update, dash.no_update


# Update companion heatmap based on mode selection
@app.callback(
    [Output('companion', 'figure'), Output('companion_mode', 'value')],
    [Input('companion_mode', 'value'), Input('submit-survey-2', 'n_clicks')],
    prevent_initial_call=True)
def update_companion(mode, submit_click):
    global companion_data
    if 'submit-survey-2' == ctx.triggered_id:
        crops_companion_update = crops_heatmap(companion_data, mode)
        return crops_companion_update, 'any'
    else:
        crops_companion_update = crops_heatmap(companion_data, mode)
        return crops_companion_update, dash.no_update


# Show intermediate survey
@app.callback([Output('leftDiv', 'style'),
               Output('rightDiv0', 'style'),
               Output('survey', 'value'),
               Output('intermediate_survey', 'children')],
              [week_input_list, companion_input_list, crop_input_list,
               Input('survey', 'value'), Input('submit-survey-2', 'n_clicks')],
              State('intermediate_survey', 'children'),
              prevent_initial_call=True)
def render_page(week_value, companion_value, crop_value, survey_value, submit_survey_2_click, inter_survey):
    which_input = list(ctx.triggered_prop_ids.keys())
    radio_reset = None
    current_time = datetime.now().strftime("%H:%M:%S")
    left_div_style = dash.no_update
    if 'submit-survey-2' == ctx.triggered_id:
        return left_div_style, {'display': 'none'}, radio_reset, ['{}']
    elif which_input[0] == 'survey.value':
        intermediate_survey = json.loads(inter_survey[0])
        intermediate_survey[current_time] = [survey_value, week_value]
        left_div_style = {'display': 'inline-block'}
        return left_div_style, {'display': 'none'}, radio_reset, [json.dumps(intermediate_survey)]
    elif which_input[0] != 'survey.value' and ctx.triggered[0]['value'] is None:
        return left_div_style, {'display': 'none'}, radio_reset, dash.no_update
    else:
        bed_number = int(ctx.triggered_id[-1:])-1
        if None not in [week_value[bed_number], companion_value[bed_number], crop_value[bed_number]]:
            left_div_style = {'display': 'none'}
            survey_inter_style = {'display': 'inline-block'}
        else:
            survey_inter_style = dash.no_update
            left_div_style = dash.no_update
        return left_div_style, survey_inter_style, radio_reset, dash.no_update


@app.callback(Output('user_note', 'value'),
              [Input('user_note', 'n_clicks'),
              Input('submit-survey-2', 'n_clicks')],
              State('user_note', 'value'),
              prevent_initial_call=True)
def user_take_note(n_clicks, second_click, note_value):
    which_input = list(ctx.triggered_prop_ids.keys())
    if which_input[0] == 'user_note.n_clicks':
        if note_value == 'Take notes here. Please do not erase any of your notes.':
            return ''
        else:
            return dash.no_update
    elif 'submit-survey-2' == ctx.triggered_id:
        return 'Take notes here. Please do not erase any of your notes.'


@app.callback(Output('provenanceValue', 'children'),
              [Input('user_note', 'n_clicks'), Input('companion_mode', 'value'), Input('technical_mode', 'value'),
               Input('calendar_mode', 'value'), Input('yearSlider', 'value'), Input('period', 'value'),
               Input('tabs-inline', 'value'), Input('sum', 'n_clicks'), Input('submit-survey-1', 'n_clicks'),
               Input('submit-survey-2', 'n_clicks'),
               Input('submit_decision', 'n_clicks'),
               week_input_list, crop_input_list, companion_input_list],
              [State('tabs-inline', 'value'), State('result', 'children'), State('user_note', 'value'),
               State('provenanceValue', 'children'), State('user_participant_id', 'children'),
               State('session_number', 'children'), State('guidance_text', 'children'), State('guide_switch', 'value'),
               state_list],
              prevent_initial_call=True)
def record_provenance(n_clicks, comp_mode, tech_mode, cal_mode, y_slider, period, new_tab, calc, start_analysis,
                      start_second_analysis, end_analysis, week_input, crop_input, companion_input, tab, calc_result,
                      note_value, provenance_value, upi, current_session, guidance_text, guide, pending_decision):
    current_time = datetime.now().strftime("%H:%M:%S")
    which_input = list(ctx.triggered_prop_ids.keys())
    provenance_data = {}

    if which_input[0] == 'submit_decision.n_clicks' and None in pending_decision:
        return dash.no_update
    else:
        if which_input[0] == 'submit-survey-1.n_clicks' or which_input[0] == 'submit-survey-2.n_clicks':
            provenance_data = {'start': [],
                               'tab-1': [], 'yearSlider.value': [], 'period.value_Month': [], 'period.value_Week': [],
                               'select_week': [], 'guided_select_week': [], 'tab-1_note': [],
                               'tab-2': [], 'select_crop': [], 'guided_select_crop': [], 'tab-2_note': [], 'calculate': [],
                               'tab-2_month': [], 'tab-2_planting': [], 'tab-2_growing': [], 'tab-2_harvest': [],
                               'tab-2_distances': [], 'tab-2_yields': [], 'tab-2_prices': [],
                               'tab-3': [], 'select_companion': [], 'guided_select_companion': [], 'tab-3_note': [],
                               'tab-3_any': [], 'tab-3_insect': [], 'tab-3_disease': [], 'tab-3_yield': [],
                               'end': []}
            provenance_data['start'].append(current_time)
        elif which_input[0] != 'submit-survey-1.n_clicks':
            provenance_data = json.loads(provenance_value[0])

        if which_input[0] == 'submit_decision.n_clicks':
            if current_session == ['first']:
                file_name = '_'.join(['provenance_1_', upi, '.txt'])
                file_name_i = '_'.join(['provenance_1_i', upi, '.txt'])
            elif current_session == ['second']:
                file_name = '_'.join(['provenance_2_', upi, '.txt'])
                file_name_i = '_'.join(['provenance_2_i', upi, '.txt'])
            path = os.path.join('results/', upi)
            provenance_data['end'].append(current_time)

            save_path = os.path.join(path, file_name)
            with open(save_path, "w") as text_file:
                text_file.write(json.dumps(provenance_data))

            save_path = os.path.join(path, file_name_i)
            for key in list(provenance_data.keys()):
                provenance_data[provenance_dict[key]] = provenance_data.pop(key)
            with open(save_path, "w") as text_file:
                text_file.write(json.dumps(provenance_data))
        elif which_input[0] == 'sum.n_clicks':
            if calc_result != 'error':
                provenance_data['calculate'].append(current_time)
        elif which_input[0] == 'tabs-inline.value':
            provenance_data[tab].append(current_time)
        elif which_input[0] == 'companion_mode.value':
            provenance_input = '_'.join(['tab-3', comp_mode])
            provenance_data[provenance_input].append(current_time)
        elif which_input[0] == 'technical_mode.value':
            provenance_input = '_'.join(['tab-2', tech_mode])
            provenance_data[provenance_input].append(current_time)
        elif which_input[0] == 'calendar_mode.value':
            provenance_input = '_'.join(['tab-2', cal_mode])
            provenance_data[provenance_input].append(current_time)
        elif which_input[0] == 'user_note.n_clicks':
            provenance_input = '_'.join([tab, 'note'])
            provenance_data[provenance_input].append(current_time)
        elif which_input[0] == 'yearSlider.value':
            provenance_data[which_input[0]].append(current_time)
        elif which_input[0] == 'period.value':
            provenance_input = '_'.join([which_input[0], period])
            provenance_data[provenance_input].append(current_time)
        elif which_input[0][0:4] == 'week':
            if guide == ['No Guidance']:
                provenance_data['select_week'].append(current_time)
            elif tab == 'tab-1':
                list_of_beds = []
                dict_of_suggestions = dict()
                track_bed = 0
                text_of_guidance = str(guidance_text)
                text_of_guidance = text_of_guidance.split('Consider planting ')
                for i_list, text in enumerate(text_of_guidance):
                    if "{'props': {'children': " in text and i_list != 0:
                        text_split = text.split("'children': '")
                        for element in text_split:
                            if track_bed == 1:
                                if element[:1].isnumeric():
                                    list_of_beds.append(int(element[:1]))
                                elif element[0:4] == 'Week':
                                    if element[6:7].isnumeric():
                                        the_week = element[6:8]
                                    else:
                                        the_week = element[6:7]
                                    if the_week in dict_of_suggestions:
                                        for bed_element in list_of_beds:
                                            dict_of_suggestions[the_week].append(bed_element)
                                    else:
                                        dict_of_suggestions[the_week] = list_of_beds
                                    track_bed = 0
                                    list_of_beds = []
                            if element[0:3] == 'bed':
                                track_bed = 1

                the_input_week = int(ctx.triggered_id[4:]) - 1
                the_value_selected = week_input[the_input_week][5:]

                if str(the_value_selected) in list(dict_of_suggestions.keys()):
                    if int(the_input_week) + 1 in dict_of_suggestions[str(the_value_selected)]:
                        provenance_data['guided_select_week'].append(current_time)
                    else:
                        provenance_data['select_week'].append(current_time)
                else:
                    provenance_data['select_week'].append(current_time)
            else:
                provenance_data['select_week'].append(current_time)
        elif which_input[0][0:4] == 'main':
            if guide == ['No Guidance']:
                provenance_data['select_crop'].append(current_time)
            elif tab == 'tab-2':
                try:
                    input_crop = crop_input[int(ctx.triggered_id.split('_')[2]) - 1]
                    suggested_crops = [guidance_text[7]['props']['children'], guidance_text[11]['props']['children'],
                                       guidance_text[15]['props']['children']]
                    if input_crop in suggested_crops:
                        provenance_data['guided_select_crop'].append(current_time)
                    else:
                        provenance_data['select_crop'].append(current_time)
                except ValueError:
                    provenance_data['select_crop'].append(current_time)

            else:
                provenance_data['select_crop'].append(current_time)
        elif which_input[0][0:4] == 'comp':
            if guide == ['No Guidance']:
                provenance_data['select_companion'].append(current_time)
            elif tab == 'tab-3':
                text_of_guidance = str(guidance_text)
                text_of_guidance = text_of_guidance.split('Consider planting ')
                dict_of_guide = dict()
                for i_list, text in enumerate(text_of_guidance):
                    if "{'props': {'children': " in text and i_list != 0:
                        text_split = text.split("'children': '")
                        if text_split[2].split("'}")[0] == ' with ':
                            key_crop = text_split[3].split("'}")[0]
                        else:
                            key_crop = text_split[2].split("'}")[0]
                        dict_of_guide[key_crop] = text_split[1].split("'}")[0]
                index_of_bed = ctx.triggered_id[15:]
                if crop_input[int(index_of_bed) - 1] in list(dict_of_guide.keys()):
                    if dict_of_guide[crop_input[int(index_of_bed) - 1]] == companion_input[int(index_of_bed) - 1]:
                        provenance_data['guided_select_companion'].append(current_time)
                    else:
                        provenance_data['select_companion'].append(current_time)
            else:
                provenance_data['select_companion'].append(current_time)

        return [json.dumps(provenance_data)]


if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=False)
