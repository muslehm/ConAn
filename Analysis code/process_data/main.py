from __future__ import print_function
import json
import csv
import pandas as pd
from datetime import datetime
import os
from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

main_analysis = {}
global_metric = {}
local_metric = {}
provenance_dict = {'start': 'start',
                       'tab-1': 'a_v1',
                       'yearSlider.value': 'a_f1',
                       'period.value_Month': 'a_f2',
                       'tab-1_note': 'a_n1',
                       'period.value_Week': 'a_f3',
                       'select_week': 'a_d1',
                       'guided_select_week': 'a_d2',
                       'tab-2': 'b_v1',
                       'tab-2_note': 'b_n1',
                       'calculate': 'b_c1',
                       'select_crop': 'b_d1',
                       'guided_select_crop': 'b_d2',
                       'tab-2_month': 'b_f1',
                       'tab-2_planting': 'b_f2',
                       'tab-2_growing': 'b_f3',
                       'tab-2_harvest': 'b_f4',
                       'tab-2_distances': 'b_f5',
                       'tab-2_yields': 'b_f6',
                       'tab-2_prices': 'b_f7',
                       'tab-3': 'c_v1',
                       'tab-3_note': 'c_n1',
                       'tab-3_any': 'c_f1',
                       'tab-3_insect': 'c_f2',
                       'tab-3_disease': 'c_f3',
                       'tab-3_yield': 'c_f4',
                       'select_companion': 'c_d1',
                       'guided_select_companion': 'c_d2',
                       'end': 'end'}

all_actions = ['a_v1', 'a_f1', 'a_f2', 'a_n1', 'a_f3', 'b_v1', 'b_n1', 'b_c1', 'b_f1', 'b_f2', 'b_f3', 'b_f4', 'b_f5',
               'b_f6', 'b_f7', 'c_v1', 'c_n1', 'c_f1', 'c_f2', 'c_f3', 'c_f4', 'd_a1', 'd_b1', 'd_c1']
action_centrality = []


def process_provenance(file):
    # Extract all actions and timestamp and put them in a dataframe
    with open(file) as a_file:
        full_data = a_file.read()
        js = json.loads(full_data)

    list_of_dict = []
    for js_key, js_value in js.items():
        for v in js_value:
            item = {'node': js_key, 'timestamp': v}
            list_of_dict.append(item)
    df = pd.DataFrame(list_of_dict, columns=['node', 'timestamp'])

    return df


def process_survey(file):
    survey_questions_dict = {'practices': 'Question 1', 'process': 'Question 2', 'session': 'Question 2',
                             'plant': 'Question 3', 'crops': 'Question 4', 'bed': 'Question 5',
                             'data': 'Question 6', 'visually': 'Question 7', 'visualization': 'Question 7',
                             'effectively': 'Question 8', 'efficiently': 'Question 9', 'decisions_1': 'Question_10',
                             'decisions_2': 'Question_11'}
    # Process survey results files to extract a dictionary of results, then use the dictionary above
    # to standardize order of questions that has been shuffled
    with open(file) as survey:
        survey_data = survey.read()
    survey_data = survey_data[3:-2]
    survey_data = survey_data.split(']", [')

    answers_of_survey = {}
    questions = survey_data[0].split(', ')
    answers = survey_data[1].split(', ')
    for q, a in zip(questions, answers):
        a = a.strip('"')
        split_q = q.split('_')

        if len(split_q) == 4:
            q = '_'.join([split_q[2], split_q[3]])
            q = q[:-8]
        else:
            q = split_q[2][:-8]

        q_number = survey_questions_dict[q]
        answers_of_survey[q_number] = int(a)

    q_keys = list(answers_of_survey.keys())
    q_keys.sort()
    sorted_answers_of_survey = {k: answers_of_survey[k] for k in q_keys}

    # COMPUTE results of survey
    score_for_all = 0
    score_for_visual = 0
    score_for_farming = 0
    score_for_guided = 0
    score_for_unguided = 0

    # all responses are 1 to 5 bad to good, we turn them to 0 to 4, and we get the percentile by
    # multiplying the sums by (25/number of questions)

    for question, score in sorted_answers_of_survey.items():
        if question[-2:] == '10':
            score_for_unguided += score - 1
        elif question[-2:] == '11':
            score_for_guided += score - 1
        elif int(question[-1:]) < 6:
            score_for_farming += score - 1
            score_for_all += score - 1
        else:
            score_for_visual += score - 1
            score_for_all += score - 1

    score_for_all = score_for_all*(25/10)
    score_for_visual = score_for_visual*(25/4)
    score_for_farming = score_for_farming*(25/5)

    if len(list(sorted_answers_of_survey.keys())) == 11:
        score_for_unguided = score_for_unguided*25/10
        score_for_guided = score_for_guided*25/10
        survey_results = {'score_for_all': score_for_all, 'score_for_visual': score_for_visual,
                          'score_for_farming': score_for_farming, 'guided': score_for_guided,
                          'unguided': score_for_unguided}
    else:
        survey_results = {'score_for_all': score_for_all, 'score_for_visual': score_for_visual,
                          'score_for_farming': score_for_farming}

    return survey_results


def process_inter_survey(file):
    with open(file) as survey:
        survey_data = survey.read()
    json_data = json.loads(survey_data)

    total_score = 0
    for k, v in json_data.items():
        total_score += int(v[0]) - 1
    percentile_score = (total_score * 25/len(list(json_data.keys())))*4/len(list(json_data.keys()))

    return [len(list(json_data.keys())), percentile_score]


def create_node_information(node_df, participant_id, guided_v, session_number):
    node_df = node_df.sort_values('timestamp')
    node_df = node_df.reset_index(drop=True)

    keys = node_df["node"].unique()

    # Compute time at each action
    dict_of_times = dict()
    for k in keys:
        dict_of_times[k] = []
    for pos in range(0, len(node_df)-1):
        if node_df['node'].iloc[pos] != 'start' and node_df['node'].iloc[pos] != 'end':
            d1 = datetime.strptime(node_df['timestamp'].iloc[pos+1], "%H:%M:%S")
            d2 = datetime.strptime(node_df['timestamp'].iloc[pos], "%H:%M:%S")
            d = d1 - d2
            d = d.total_seconds()
            dict_of_times[node_df['node'].iloc[pos]].append(d)
    guided_decision = dict({'a': 0, 'b': 0, 'c': 0})
    unguided_decision = dict({'a': 0, 'b': 0, 'c': 0})

    # Sum-up times of each unique action, and in guided versions, get number of guided decisions vs. unguided
    for k, v in dict_of_times.items():
        if guided_v == 'g':
            if k[-2:] == 'd1':
                unguided_decision[k[0:1]] = len(v)
            elif k[-2:] == 'd2':
                guided_decision[k[0:1]] = len(v)
        dict_of_times[k] = sum(v)

    # Encode decision actions to a separate decisions cluster.
    for k in list(guided_decision.keys()):
        new_key = '_'.join(['d', k])
        old_key1 = '_'.join([k, 'd1'])
        if guided_v == 'g':
            try:
                old_key2 = '_'.join([k, 'd2'])
                dict_of_times[new_key] = dict_of_times[old_key1] + dict_of_times[old_key2]
                dict_of_times.pop(old_key1)
                dict_of_times.pop(old_key2)
            except KeyError:
                try:
                    dict_of_times[new_key] = dict_of_times.pop(old_key1)
                except KeyError:
                    pass
        else:
            dict_of_times[new_key] = dict_of_times.pop(old_key1)

    list_of_items_dict = []

    # Construct node list for the network graph
    for k, v in dict_of_times.items():
        if k == 'start':
            pass
        elif k == 'end':
            pass
        else:
            if k[0:1] == 'd':
                # Compute opacity, 200 for nodes except for decision nodes that depends on guided to total decisions.
                if guided_v == 'g':
                    opacity = round(guided_decision[k[2:3]]/(unguided_decision[k[2:3]]+guided_decision[k[2:3]]), 1)
                else:
                    opacity = 100
                action_type = 'D'
            else:
                opacity = 100
                action_type = k[2:-1].upper()
            item = {'Node': k, 'Time': v, 'Cluster': k[0:1].upper(), 'Action Type': action_type, 'Opacity': opacity}
            list_of_items_dict.append(item)
    df_prov = pd.DataFrame(list_of_items_dict,
                           columns=['Node', 'Time', 'Cluster', 'Action Type', 'Opacity'])
    time_per_cluster = df_prov.groupby(['Cluster'])['Time'].sum()

    create_save_file = '_'.join(['nodes/png_nodes', participant_id, guided_v, str(session_number), '.csv'])
    df_prov.to_csv(create_save_file, index=False)

    time_per_cluster_A = 0
    time_per_cluster_B = 0
    time_per_cluster_C = 0
    time_per_cluster_D = 0
    for index, row in time_per_cluster.items():
        if index == 'A':
            time_per_cluster_A = time_per_cluster['A']
        elif index == 'B':
            time_per_cluster_B = time_per_cluster['B']
        elif index == 'C':
            time_per_cluster_C = time_per_cluster['C']
        elif index == 'D':
            time_per_cluster_D = time_per_cluster['D']

    total_exploration_time = {'total': df_prov['Time'].sum(), 'A': time_per_cluster_A,
                              'B': time_per_cluster_B, 'C': time_per_cluster_C, 'D': time_per_cluster_D}

    return total_exploration_time, df_prov


def create_edge_list(node_df, participant_id, guided_v, session_number, node_info):
    node_df = node_df.sort_values('timestamp')
    node_df = node_df.reset_index(drop=True)
    edge_items = []
    for node_edge in range(1, len(node_df) - 2):
        item = {'Source': node_df['node'].iloc[node_edge], 'Target': node_df['node'].iloc[node_edge + 1]}
        edge_items.append(item)
    edge_list = pd.DataFrame(edge_items, columns=['Source', 'Target'])
    decision_dict = {'a_d1': 'd_a', 'a_d2': 'd_a', 'b_d1': 'd_b', 'b_d2': 'd_b', 'c_d1': 'd_c', 'c_d2': 'd_c'}
    for key_decision in list(decision_dict.keys()):
        try:
            edge_list['Source'] = edge_list['Source'].str.replace(key_decision, decision_dict[key_decision])
        except KeyError:
            pass
        try:
            edge_list['Target'] = edge_list['Target'].str.replace(key_decision, decision_dict[key_decision])
        except KeyError:
            pass

    edge_list_unique = edge_list.groupby(edge_list.columns.tolist(), as_index=False).size()
    edge_list_unique.rename(columns={'size': 'Frequency'}, inplace=True)

    edge_list_unique = edge_list_unique[edge_list_unique['Source'] != edge_list_unique['Target']]

    create_save_file = '_'.join(['edges/png_edges', participant_id, guided_v, str(session_number), '.csv'])
    edge_list_unique.to_csv(create_save_file, index=False)

    if participant_id != '42864671':
        graph_network(edge_list_unique, node_info, participant_id, guided_v, session_number)


def graph_network(edge_l, node_l, p_id, guide, session):
    global action_centrality_df, all_actions, action_centrality
    if guide == 'g':
        guide = 1
    else:
        guide = 0
    G = nx.DiGraph()
    G.add_nodes_from(list(node_l['Node']))
    nx.set_node_attributes(G, list(node_l['Time']), 'time')
    nx.set_node_attributes(G, list(node_l['Cluster']), 'cluster')
    nx.set_node_attributes(G, list(node_l['Action Type']), 'type')
    nx.set_node_attributes(G, list(node_l['Opacity']), 'opacity')
    G.add_edges_from(edge_l[["Source", "Target"]].itertuples(index=False))
    nx.draw_shell(G, with_labels=False)
    in_degree = nx.in_degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    for a in all_actions:
        if a in betweenness and a in in_degree:
            node_centrality = {'action': a, 'participant': p_id, 'guidance': guide, 'session': session,
                               'betweenness': betweenness[a], 'degree': in_degree[a]}
        elif a in betweenness and a not in in_degree:
            node_centrality = {'action': a, 'participant': p_id, 'guidance': guide, 'session': session,
                               'betweenness': betweenness[a], 'degree': 0}
        elif a not in betweenness and a in in_degree:
            node_centrality = {'action': a, 'participant': p_id, 'guidance': guide, 'session': session,
                               'betweenness': 0, 'degree': in_degree[a]}
        else:
            node_centrality = {'action': a, 'participant': p_id, 'guidance': guide, 'session': session,
                               'betweenness': 0, 'degree': 0}
        action_centrality.append(node_centrality)


def analyze_results(survey_df, main_df):
    merged_df = pd.merge(survey_df, main_df, on=['Participant', 'Session', 'Guidance'])
    merged_df = merged_df.replace(['guided'], '1')
    merged_df = merged_df.replace(['unguided'], '0')
    merged_df = merged_df.replace(['first'], '1')
    merged_df = merged_df.replace(['second'], '2')

    cols = ['Participant', 'Session', 'Guidance',
            'Inter_survey_Questions', 'Inter_survey_Score', 'All Score', 'Vis Score', 'Farming Score',
            'Actions', 'Total Time', 'A Time', 'B Time', 'C Time', 'D Time']
    merged_df = merged_df[cols]
    merged_df.to_csv('merged_df.csv', index=False)
    merged_df = merged_df[merged_df['Participant'] != '42864671']
    top_time = merged_df.sort_values('Total Time', ascending=True).head(3)
    bottom_time = merged_df.sort_values('Total Time', ascending=True).tail(3)
    time_list = pd.concat([top_time, bottom_time]).reset_index(drop=True)

    top_actions = merged_df.sort_values('Actions', ascending=True).head(3).reset_index(drop=True)
    bottom_actions = merged_df.sort_values('Actions', ascending=True).tail(3).reset_index(drop=True)
    actions_list = pd.concat([top_actions, bottom_actions]).reset_index(drop=True)

    top_survey = merged_df.sort_values('All Score', ascending=False).head(3).reset_index(drop=True)
    bottom_survey = merged_df.sort_values('All Score', ascending=False).tail(3).reset_index(drop=True)
    survey_list = pd.concat([top_survey, bottom_survey]).reset_index(drop=True)

    top_inter_survey = merged_df.sort_values('Inter_survey_Score', ascending=False).head(3).reset_index(drop=True)
    bottom_inter_survey = merged_df.sort_values('Inter_survey_Score', ascending=False).tail(3).reset_index(drop=True)
    inter_survey_list = pd.concat([top_inter_survey, bottom_inter_survey]).reset_index(drop=True)

    top_inter_q = merged_df.sort_values('Inter_survey_Questions', ascending=True).head(3).reset_index(drop=True)
    bottom_inter_q = merged_df.sort_values('Inter_survey_Questions', ascending=True).tail(3).reset_index(drop=True)
    inter_q_list = pd.concat([top_inter_q, bottom_inter_q]).reset_index(drop=True)

    top_vis_survey = merged_df.sort_values('Vis Score', ascending=False).head(3).reset_index(drop=True)
    bottom_vis_survey = merged_df.sort_values('Vis Score', ascending=False).tail(3).reset_index(drop=True)
    vis_survey_list = pd.concat([top_vis_survey, bottom_vis_survey]).reset_index(drop=True)

    top_farming_survey = merged_df.sort_values('Farming Score', ascending=False).head(3).reset_index(drop=True)
    bottom_farming_survey = merged_df.sort_values('Farming Score', ascending=False).tail(3).reset_index(drop=True)
    farming_survey_list = pd.concat([top_farming_survey, bottom_farming_survey]).reset_index(drop=True)

    top_bottom_data = {'Time': time_list['Participant'].tolist(),
                       'Time_g': time_list['Guidance'].tolist(),
                       'Time_v': time_list['Total Time'].tolist(),

                       'Actions': actions_list['Participant'].tolist(),
                       'Actions_g': actions_list['Guidance'].tolist(),
                       'Actions_v': actions_list['Actions'].tolist(),


                       'Survey': survey_list['Participant'].tolist(),
                       'Survey_g': survey_list['Guidance'].tolist(),
                       'Survey_v': survey_list['All Score'].tolist(),

                       'Vis Survey': vis_survey_list['Participant'].tolist(),
                       'Vis Survey_g': vis_survey_list['Guidance'].tolist(),
                       'Vis Survey_v': vis_survey_list['Vis Score'].tolist(),

                       'Farming Survey': farming_survey_list['Participant'].tolist(),
                       'Farming Survey_g': farming_survey_list['Guidance'].tolist(),
                       'Farming Survey_v': farming_survey_list['Farming Score'].tolist(),

                       'Inter Survey': inter_survey_list['Participant'].tolist(),
                       'Inter Survey_g': inter_survey_list['Guidance'].tolist(),
                       'Inter Survey_v': inter_survey_list['Inter_survey_Score'].tolist(),

                       'Inter Q': inter_q_list['Participant'].tolist(),
                       'Inter Q_g': inter_q_list['Guidance'].tolist(),
                       'Inter Q_v': inter_q_list['Inter_survey_Questions'].tolist()}
    top_bottom_df = pd.DataFrame(top_bottom_data)
    # Save top_bottom result
    top_bottom_df.to_csv('top_bottom.csv', index=True)

    survey_df = survey_df[survey_df['Participant'] != '42864671']
    survey_df = survey_df.reset_index(drop=True)

    survey_summary = survey_df[survey_df.columns.drop('Participant')].groupby(['Session', 'Guidance']).mean()
    # Save Survey summary
    survey_summary.to_csv('survey_summary.csv', index=True)


if __name__ == '__main__':
    # Read results folder
    x = list(os.walk("results"))
    participants = x[0][1]
    main_analysis = {}
    survey_answers = {}
    inter_survey_answers = {}
    node_time = {}
    combination_of_sessions = {}  # [Study Control] use to double-check if sessions were distributed equally.
    # Main analysis are the metrics for the global characteristics
    for participant in participants:
        node_time[participant] = {1: {}, 2: {}}
        main_analysis[participant] = {'guided': {'time': 0, 'actions': 0},  'unguided': {'time': 0, 'actions': 0},
                                      'first': {'time': 0, 'actions': 0}, 'second': {'time': 0, 'actions': 0}}
        data_dir = ''.join(['results/', participant, '/'])

        # We get the combination to know which session was guided and which unguided
        combination_fn = os.path.join(data_dir, '_'.join(['combination', participant, '.txt']))
        with open(combination_fn) as f:
            combination = f.read()

        combination = combination.replace('"', '')

        # [Start Study Control]
        if combination_of_sessions != {} and combination in list(combination_of_sessions.keys()):
            combination_of_sessions[combination] = combination_of_sessions[combination] + 1
        else:
            combination_of_sessions[combination] = 1
        # [End Study Control]

        survey_1 = os.path.join(data_dir, '_'.join(['survey1', participant, '.txt']))
        survey_2 = os.path.join(data_dir, '_'.join(['survey2', participant, '.txt']))
        survey_3 = os.path.join(data_dir, '_'.join(['survey3', participant, '.txt']))
        survey_answers[participant] = {'survey1': {}, 'survey2': {}, 'survey3': {}, 'guided': {}, 'unguided': {}}
        inter_survey_answers[participant] = {'first': [], 'second': [], 'guided': [], 'unguided': []}
        for survey_fn in [survey_1, survey_2, survey_3]:
            results_data = process_survey(survey_fn)
            title_of_survey = survey_fn.split('_')[0][-7:]
            if len(list(results_data.keys())) == 3:
                survey_answers[participant][title_of_survey] = results_data
            else:
                first_inter_survey_fn = os.path.join(data_dir, ''.join(['survey_inter_1__',
                                                                        participant, '_.txt']))
                second_inter_survey_fn = os.path.join(data_dir, ''.join(['survey_inter_2__',
                                                                        participant, '_.txt']))

                inter_survey_answers[participant]['first'] = process_inter_survey(first_inter_survey_fn)
                inter_survey_answers[participant]['second'] = process_inter_survey(second_inter_survey_fn)

                if int(combination.split('_')[1]) == 0:
                    survey_answers[participant]['survey2']['score_for_all'] = \
                        survey_answers[participant]['survey2']['score_for_all'] + results_data['unguided']
                    survey_answers[participant]['survey3'] = {
                        'score_for_all': results_data['score_for_all'] + results_data['guided'],
                        'score_for_visual': results_data['score_for_visual'],
                        'score_for_farming': results_data['score_for_farming']}

                    survey_answers[participant]['unguided'] = survey_answers[participant]['survey2']
                    survey_answers[participant]['guided'] = survey_answers[participant]['survey3']

                    inter_survey_answers[participant]['unguided'] = inter_survey_answers[participant]['first']
                    inter_survey_answers[participant]['guided'] = inter_survey_answers[participant]['second']
                else:
                    survey_answers[participant]['survey2']['score_for_all'] = \
                        survey_answers[participant]['survey2']['score_for_all'] + results_data['guided']
                    survey_answers[participant]['survey3'] = {
                        'score_for_all': results_data['score_for_all'] + results_data['unguided'],
                        'score_for_visual': results_data['score_for_visual'],
                        'score_for_farming': results_data['score_for_farming']}

                    survey_answers[participant]['guided'] = survey_answers[participant]['survey2']
                    survey_answers[participant]['unguided'] = survey_answers[participant]['survey3']

                    inter_survey_answers[participant]['unguided'] = inter_survey_answers[participant]['second']
                    inter_survey_answers[participant]['guided'] = inter_survey_answers[participant]['first']

        session = 1
        number_of_actions = 0
        total_time = {}
        for i, comb in enumerate(combination.split('_')):
            if i % 2 != 0:
                if comb == "1":
                    guided_provenance_fn = os.path.join(data_dir, '_'.join(['provenance', str(session), 'i',
                                                                            participant, '.txt']))
                    data = process_provenance(guided_provenance_fn)
                    number_of_actions = len(data) - 2

                    if i == 1:
                        total_time, node_i = create_node_information(data, participant, 'g', 1)
                        create_edge_list(data, participant, 'g', 1, node_i)
                        main_analysis[participant]['first']['time'] = total_time
                        main_analysis[participant]['first']['actions'] = number_of_actions

                    else:
                        total_time, node_i = create_node_information(data, participant, 'g', 2)
                        create_edge_list(data, participant, 'g', 2, node_i)
                        main_analysis[participant]['second']['time'] = total_time
                        main_analysis[participant]['second']['actions'] = number_of_actions

                    main_analysis[participant]['guided']['time'] = total_time
                    main_analysis[participant]['guided']['actions'] = number_of_actions
                    session += 1
                else:
                    unguided_provenance_fn = os.path.join(data_dir, '_'.join(['provenance', str(session), 'i',
                                                                              participant, '.txt']))
                    data = process_provenance(unguided_provenance_fn)
                    number_of_actions = len(data) - 2

                    if i == 1:
                        total_time, node_i = create_node_information(data, participant, 'u', 1)
                        create_edge_list(data, participant, 'u', 1, node_i)
                        main_analysis[participant]['first']['time'] = total_time
                        main_analysis[participant]['first']['actions'] = number_of_actions
                    else:
                        total_time, node_i = create_node_information(data, participant, 'u', 2)
                        create_edge_list(data, participant, 'u', 2, node_i )
                        main_analysis[participant]['second']['time'] = total_time
                        main_analysis[participant]['second']['actions'] = number_of_actions
                    main_analysis[participant]['unguided']['time'] = total_time
                    main_analysis[participant]['unguided']['actions'] = number_of_actions
                    session += 1

                node_time[participant][session-1] = {'Nodes': number_of_actions, 'time': total_time}
    # [Study Control]
    # print(combination_of_sessions)

    df_dict = {}
    main_items = []
    item_dict = {}
    for key, value in main_analysis.items():
        for second_key, second_value in value.items():
            if second_key == 'guided' or second_key == 'unguided':
                if second_value == value['first']:
                    item_dict = {'Participant': key, 'Guidance': second_key, 'Total Time': second_value['time']['total'],
                                 'A Time': second_value['time']['A'], 'B Time': second_value['time']['B'],
                                 'C Time': second_value['time']['C'], 'D Time': second_value['time']['D'],
                                 'Actions': second_value['actions'], 'Session': 'first'}
                else:
                    item_dict = {'Participant': key, 'Guidance': second_key,
                                 'Total Time': second_value['time']['total'],
                                 'A Time': second_value['time']['A'], 'B Time': second_value['time']['B'],
                                 'C Time': second_value['time']['C'], 'D Time': second_value['time']['D'],
                                 'Actions': second_value['actions'], 'Session': 'second'}
                main_items.append(item_dict)
    df_main_analysis = pd.DataFrame(main_items, columns=['Participant', 'Guidance', 'Total Time', 'A Time', 'B Time',
                                                         'C Time', 'D Time', 'Actions', 'Session'])

    df_main_analysis.to_csv('df_main_analysis.csv', index=False)

    # Create a table with all survey and inter_survey data
    df_dict = {}
    survey_items = []
    for key, value in survey_answers.items():
        for second_key, second_value in value.items():
            if second_key == 'survey2' or second_key == 'survey3':
                if second_key == 'survey2':
                    session_survey = 'first'
                else:
                    session_survey = 'second'
                if second_value == value['guided']:
                    item_dict = {'Participant': key, 'Session': session_survey,
                                 'Inter_survey_Questions': inter_survey_answers[key]['guided'][0],
                                 'Inter_survey_Score': inter_survey_answers[key]['guided'][1],
                                 'All Score': second_value['score_for_all'],
                                 'Vis Score': second_value['score_for_visual'],
                                 'Farming Score': second_value['score_for_farming'],
                                 'Guidance': 'guided'}
                else:
                    item_dict = {'Participant': key, 'Session': session_survey,
                                 'Inter_survey_Questions': inter_survey_answers[key]['unguided'][0],
                                 'Inter_survey_Score': inter_survey_answers[key]['unguided'][1],
                                 'All Score': second_value['score_for_all'],
                                 'Vis Score': second_value['score_for_visual'],
                                 'Farming Score': second_value['score_for_farming'],
                                 'Guidance': 'unguided'}
                survey_items.append(item_dict)
            elif second_key == 'survey1':
                item_dict = {'Participant': key, 'Session': 'Control',
                             'Inter_survey_Questions': 0, 'Inter_survey_Score': 0,
                             'All Score': second_value['score_for_all'],
                             'Vis Score': second_value['score_for_visual'],
                             'Farming Score': second_value['score_for_farming'],
                             'Guidance': 'Control'}
                survey_items.append(item_dict)

    df_survey_results = pd.DataFrame(survey_items, columns=['Participant', 'Session', 'Inter_survey_Questions',
                                                            'Inter_survey_Score', 'All Score',
                                                            'Vis Score', 'Farming Score', 'Guidance'])

    # Save Survey results
    df_survey_results.to_csv('df_survey_results.csv', index=False)

    analyze_results(df_survey_results, df_main_analysis)

    action_centrality_df = pd.DataFrame(action_centrality,
                                        columns=['action', 'participant', 'guidance', 'session', 'betweenness',
                                                 'degree'])
    # Save Survey centrality results
    action_centrality_df.to_csv('df_centrality.csv', index=False)


    fig, axs = plt.subplots(2, 2,
                            figsize=(10, 7),
                            tight_layout=True)

    x = action_centrality_df[action_centrality_df['guidance'] == 1]
    axs[0, 0].hist(x['degree'], bins=[0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.99])
    axs[0, 0].set_title('Guided Betweenness')
    x = action_centrality_df[action_centrality_df['guidance'] == 0]
    axs[0, 1].hist(x['degree'], bins=[0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.99])
    axs[0, 1].set_title('Unguided Degree')
    x = action_centrality_df[action_centrality_df['guidance']==1]
    axs[1, 0].hist(x['betweenness'], bins=[0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.99])
    axs[1, 0].set_title('Guided Betweenness')
    x = action_centrality_df[action_centrality_df['guidance'] == 0]
    axs[1, 1].hist(x['betweenness'], bins=[0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.99])
    axs[1, 1].set_title('Unguided Betweenness')
    fig.show()
