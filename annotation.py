#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 16:25:31 2022
@author: dlr\hu_xk
"""
import re
import json
import csv
import numpy as np
import argparse
import matplotlib.pyplot as plt
# from OSMPythonTools.nominatim import Nominatim
# nominatim = Nominatim()
import requests

url = 'https://nominatim.openstreetmap.org/search'

look_up_url = 'https://nominatim.openstreetmap.org/lookup'

def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

def main():
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('--data', type=str, default='chennai')
    parser.add_argument('--mode', type=int, default=1)

    args = parser.parse_args()
    print ('data: '+str(args.data))
    if args.mode==1:
        print ('You are under annotate mode.')
    if args.mode==2:
        print ('You are under modify mode.')
    if args.mode==0:
        print ('You are under modify mode. You can modify the previous annotation by spefiying tweet ID')

    base_dir = 'data/'
    file = base_dir+args.data+'.json'
    annotation_file = base_dir+args.data+'_anotation.json'
    max_place_count = 100
    io = open(file,"r")
    place_data = json.load(io)
    raw_keys = [str(key) for key in place_data.keys()]
    # import pdb
    # pdb.set_trace()
    try:
        anno_io = open(annotation_file,"r")
        anno_place_data = json.load(anno_io)
    except:
        anno_place_data = {}
    anno_keys = []
    for key in anno_place_data.keys():
        anno_keys.append(str(key))
    if args.mode == 1:
        existing_keys = []
        while 1:
            print(colored(0, 100,  255,'Start from last annotation (1). Start from first unannotated tweet (0). Start from a specific tweet (Tweet ID)'))
            result_index = input()
            if result_index == '1':
                if anno_place_data.keys():
                    existing_keys = list(anno_place_data.keys())[-1]
                break
            elif result_index == '0':
                break
            else:
                if str(result_index) not in raw_keys:
                    print(colored(255, 0, 0,'Tweet does not exist'))
                else:
                    existing_keys.append(result_index)
                    break
    # elif args.mode == 2:
    #     while 1:
    #         print(colored(0, 100,  255,'If you want to start from the first tweet, input 1. Otherwise, input the ID of the starting tweet'))
    #         result_index = input()
    #         existing_keys = []
    #         if result_index != '1':
    #             if str(result_index) not in anno_keys:
    #                 print(colored(0, 100,  255,'Tweet ID is invalid'))
    #             else:
    #                 existing_keys.append(result_index)
    #                 break
    #         else:
    #             break
    else:
        existing_keys = []
    while (1):
        if not args.mode:
            print(colored(0, 100,  255,'Input the ID of the Tweet whose annotation you want to modify'))
            result_index = input()
            while result_index not in place_data.keys():
                print(colored(0, 100,  255,'ID does not exist. Input again:'))
                result_index = input()
            keys = [result_index]
        else:
            keys = list(place_data.keys()); ['672418078106525952']#
        
        key_index = 0
        bool_last_key = 0
        while key_index < len(keys):
            key = keys[key_index]
            if not existing_keys:
                bool_last_key = 1
            if key in existing_keys:
                bool_last_key = 1
            if not bool_last_key:
                key_index += 1
                continue
            key_index += 1
            i = 1
            sentence_text = place_data[key]['text']
            if 'event' in  place_data[key]:
                event =  place_data[key]['event']
            else:
                event = ''
            anno_places = {}
            while i < max_place_count:
                if not 'T'+str(i) in place_data[key]:
                    i+=1
                    continue
                if args.mode==1 and key in anno_place_data and 'T'+str(i) in anno_place_data[key]:
                    i+=1
                    continue
                if args.mode == 2 and (key not in anno_place_data or 'T'+str(i) not in anno_place_data[key]):
                    i+=1
                    continue
                place = place_data[key]['T'+str(i)]
                target_place = place['text']
                ori_place =  place['text']
                cur_annotation = {}
                if key in anno_place_data:
                    if 'T'+str(i) in anno_place_data[key]:
                        cur_annotation = anno_place_data[key]['T'+str(i)]
                if 'type' not in place.keys():
                    place['type'] = 'inLoc'
                if place['type'] == 'ambLoc' or target_place.lower() in ['chennai','puertorico','texas', 'tx', 'houston','la', 'hou', 'khou11', 'housto', 'abc13', 'a','h-town','h town','htown','nws']:
                    i+=1
                    continue
                while 1:
                    '''Previous annotation of target place name'''
                    existing_annotaion = set()
                    for new_key in anno_place_data:
                        m = 0
                        while m < max_place_count:
                            if not 'T'+str(m) in anno_place_data[new_key]:
                                m+=1
                                continue
                            # if args.mode and key in anno_place_data and 'T'+str(i) in anno_place_data[key]:
                            #     i+=1
                            #     continue
                            pre_place = anno_place_data[new_key]['T'+str(m)]
                            if 'type' not in pre_place.keys():
                                pre_place['type'] = 'inLoc'
                            place_name = pre_place['text']
                            if place_name.lower() ==  target_place.lower():
                                existing_annotaion.add((pre_place['osm_id'],pre_place['type'],pre_place['class'], pre_place['lat'],pre_place['lon'],pre_place['place_id']))
                            m+=1
                    existing_annotaion = list(existing_annotaion)
                    # print(existing_annotaion)
                    params = dict(
                        q=target_place,
                        osmtype='R',
                        dedupe=1,
                        format='json',
                        limit=100,
                     )
                    resp = requests.get(url=url, params=params)
                    results = resp.json() 
                    print('*'*50)
                    for j, result in enumerate(results):
                        print(colored(0, 255,0, str(len(results)-j-1+len(existing_annotaion))), results[len(results)-j-1]['display_name'], '(', results[len(results)-j-1]['lat'], results[len(results)-j-1]['lon'], ')', results[len(results)-j-1]['type'])
                    if existing_annotaion:
                        print('*'*50)
                        print(colored(0, 255,0,'Previous annotation of '+target_place))
                    for t, exist in enumerate(existing_annotaion):
                        print(colored(0, 255,0, str(t)), '(', exist[3], exist[4],')', exist[1])
                    if event:
                        print('event:', colored(255, 255,102, str(event)))

                    print('*'*50)
                    if args.mode == 0 or args.mode == 2:
                        if cur_annotation:
                            print(colored(255, 255,0,'Current annotation of '+ori_place))                        
                            print('(', cur_annotation['lat'], cur_annotation['lon'],')', cur_annotation['type'])
                            print('*'*50)
                    start_str = sentence_text[0:int(place['start_idx'])]
                    mid_str = colored(255, 0,  0, place['text']) 
                    end_str =  sentence_text[int(place['end_idx']):len(sentence_text)]
                    print(key+':',start_str+mid_str+end_str)
                    print(colored(0, 100,  255, 'Input the index of the correct one / Input OSM ID / Input a new name / Input lat and lon coordiantes/ Skip:s') )
                    result_index = input()
                    bool_osm_id_way = 0
                    while 1:
                        if result_index.isdigit():
                            if len(result_index) < 3:
                                if (int(result_index) > len(results)+len(existing_annotaion)-1 or int(result_index)<0):
                                    print(colored(255, 0 ,0,'index exceed the maximum index'))
                                    print(colored(0, 100,  255, 'Input the index of the correct one / Input OSM ID / Input a new name / Input lat and lon coordiantes/ Skip:s') )
                                    result_index = input()
                                else:
                                    break
                            else:
                                while 1:
                                    print(colored(0, 100,  255, 'Input the type: way (w) or node (n)'))
                                    result_type = input()
                                    if result_type.lower() in ['n','w']:
                                        break
                                # input the OSM ID of a way
                                params = dict(
                                    osm_ids=result_type.upper()+str(result_index),
                                    format='json',
                                    extratags=1,
                                 )
                                resp = requests.get(url=look_up_url, params=params)
                                results = resp.json()
                                if not results:
                                    print(colored(255, 0 ,0, 'invalid OSM ID or type'))
                                    print(colored(0, 100,  255, 'Input the index of the correct one / Input OSM ID / Input a new name / Input lat and lon coordiantes/ Skip:s') )
                                    result_index = input()
                                else:
                                    anno_place = place
                                    anno_place['lat']= results[0]['lat']
                                    anno_place['lon']= results[0]['lon']
                                    anno_place['osm_id']= results[0]['osm_id']
                                    anno_place['place_id']= results[0]['place_id']
                                    anno_place['type']= results[0]['type']
                                    anno_place['class']= results[0]['class']
                                    if key not in anno_place_data:
                                        anno_place_data[key] = {}
                                    anno_place_data[key]['T'+str(i)] = anno_place
                                    f = open(annotation_file, "w")
                                    json.dump(anno_place_data, f)
                                    f.close()
                                    bool_osm_id_way = 1
                                    break
                        else:
                            break
                    if str(result_index).lower() == 's':
                        break
                    if bool_osm_id_way:
                        break
                    try:
                        anno_place = place
                        if int(result_index) > len(existing_annotaion)-1:
                            right_index = int(result_index)-len(existing_annotaion)
                            anno_place['lat']= float(results[right_index]['lat'])
                            anno_place['lon']= float(results[right_index]['lon'])
                            anno_place['osm_id']= results[right_index]['osm_id']
                            anno_place['place_id']= results[right_index]['place_id']
                            anno_place['type']= results[right_index]['type']
                            anno_place['class']= results[right_index]['class']
                        else:
                            right_index = int(result_index)
                            anno_place['lat']= existing_annotaion[right_index][3]
                            anno_place['lon']= existing_annotaion[right_index][4]
                            anno_place['osm_id']= existing_annotaion[right_index][0]
                            anno_place['place_id']= existing_annotaion[right_index][5]
                            anno_place['type']= existing_annotaion[right_index][1]
                            anno_place['class']= existing_annotaion[right_index][2]
                            
                        if key not in anno_place_data:
                            anno_place_data[key] = {}
                        anno_place_data[key]['T'+str(i)] = anno_place
                        f = open(annotation_file, "w")
                        json.dump(anno_place_data, f)
                        f.close()
                        break
                    except:
                        try:
                            lat= float(str(result_index).split(',')[0])
                            lon=float(str(result_index).split(',')[1])
                            anno_place = place
                            anno_place['lat']= lat
                            anno_place['lon']= lon
                            anno_place['osm_id']= 'none'
                            anno_place['place_id']= 'none'
                            anno_place['type']= 'none'
                            anno_place['class']= 'none'
                            if key not in anno_place_data:
                                anno_place_data[key] = {}
                            anno_place_data[key]['T'+str(i)] = anno_place
                            f = open(annotation_file, "w")
                            json.dump(anno_place_data, f)
                            f.close()
                            break
                        except:
                            target_place = str(result_index)
                i+=1
        print(colored(0, 100,  255, 'Done') )
        if args.mode:
            break

if __name__ == '__main__':
    main()
    
