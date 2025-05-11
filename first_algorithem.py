# -*- coding: utf-8 -*-
"""
Created on Sat May  3 12:49:03 2025

@author: ks

Target: Build a macro-based placement power planning algorithem

This Algorthem:
    1 Only consider macro plased area.
    2.Only support rectangle shaped.
    3.The generate power-stripe would follow min-spacing, min-width DRC rule.
    4. No consider io-pin

"""
import numpy as np

def opt_power_grid_planning(pattern_stripe_start_end:list, metal_spacing:int, metal_width:int, opt_type:str):
    pattern_stripe_start_end.sort(reverse=False,key=lambda score: score[0]);
    print("opt power grid planning");
    print(pattern_stripe_start_end);
    
    power_planning=[]; #[start, end, spacing, width,score];
    
    ##Change compensate space to greater score power_grid_pattern.
    ##In this Scenario no adjust power_grid_pattern spacing and width.
    
    print("")
    print("Do opt fixing with different type:")
    
    if(opt_type=="space"):
        up_adjust=0;
        pre_score=0;
        for idx in range(len(pattern_stripe_start_end)):
            pattern=pattern_stripe_start_end[idx];
            cur_score=pattern[4];
            
            if(pattern[5]!=0):
                cur_s=cur_score;
                down_adjust=pattern[5];
                for idy in range(idx-1, 0,-1):
                    pre_s=pattern_stripe_start_end[idy][4];
                    if(pre_s<=cur_s): break;
                    power_planning[idy]=([power_planning[idy][0]-down_adjust,power_planning[idy][1]-down_adjust,metal_spacing,metal_width,power_planning[idy][4]]);
                    cur_s=pre_s;
            
            if(pre_score<cur_score):
                power_planning.append([pattern[2]-up_adjust,pattern[3]-up_adjust,metal_spacing,metal_width,pattern[4]]);
                up_adjust+=pattern[6];
            else:
                power_planning.append([pattern[2],pattern[3],metal_spacing,metal_width,pattern[4]])
                up_adjust=pattern[6];
            pre_score=cur_score;


    ##In this Scenario, change compensate to greater score region. larger some boundary stripe in greater score power_grid_pattern.
    elif(opt_type=="width"):
        up_adjust=0;
        pre_score=0;
        for idx in range(len(pattern_stripe_start_end)):
            pattern=pattern_stripe_start_end[idx];
            cur_score=pattern[4];
            
            if(pattern[5]!=0):
                cur_s=cur_score;
                down_adjust=pattern[5];
                for idy in range(idx-1, 0,-1):
                    pre_s=pattern_stripe_start_end[idy][4];
                    if(pre_s<=cur_s): 
                        power_planning[idy+1]=([power_planning[idy+1][0]-down_adjust,power_planning[idy+1][1],metal_spacing,metal_width+down_adjust,power_planning[idy+1][4]]);
                        break;
                    power_planning[idy]=([power_planning[idy][0]+down_adjust,power_planning[idy][1]+down_adjust,metal_spacing,metal_width+down_adjust,power_planning[idy][4]]);
                    cur_s=pre_s;
            
            if(pre_score<cur_score):
                power_planning.append([pattern[2]-up_adjust,pattern[3]-up_adjust,metal_spacing,metal_width,pattern[4]]);
                up_adjust+=pattern[6];
            else:
                power_planning[idx-1]=([power_planning[idx-1][0],power_planning[idx-1][1]+up_adjust,metal_spacing,metal_width+up_adjust,power_planning[idx-1][4]]);
                power_planning.append([pattern[2],pattern[3],metal_spacing,metal_width,pattern[4]])
                up_adjust=pattern[6];
            pre_score=cur_score;

    
    ##Do do any opt.
    else:
        for idx in range(len(pattern_stripe_start_end)):
            power_planning.append([pattern[2],pattern[3],metal_spacing,metal_width,pattern[4]]);
            

    print(power_planning)
        
    
def power_grid_planning(pattern_list:list, up_score:dict, down_score:dict, metal_spacing:int, metal_width:int,pattern_width:int):
    up_offset={}; 
    down_offset={};
    pattern_stripe_start_end=[]; #pattern_stripe_start_end =[pattern start point, pattern end point, stripe start point, stripe end point, pattern weight,up_compensate,down_compensate]
    
    for pattern in pattern_list:
        print(pattern);
        down=pattern[1];
        up=pattern[2];
        
        down_margin=metal_spacing/2; 
        up_margin=metal_spacing/2;
        if(down_offset.get(down)!=None): down_margin+=down_offset[down];
        if(up_offset.get(up)!=None): up_margin+=up_offset[up];
        
        
        ##SCENARIO 0 : Solve off-set pattern.
        if(down==0):
            offset=up-pattern_width;
            print("chck offset", offset)
            if(up_offset.get(up)==None):
                pattern_stripe_start_end.append([down,up,down+metal_spacing,up-offset,pattern[0],0,0]);
                down_offset[up]=offset;
                
            else:
                end_stripe=metal_width-up_offset.get(up);
                if(end_stripe<0): end_stripe=0;
                pattern_stripe_start_end.append([down,up,metal_spacing-end_stripe+down+offset,up-end_stripe,pattern[0],0,0]);
            
        ##SCENARIO 1: the power_grid_pattern up and down PATTERN both not be assigned.
        elif(up_offset.get(up)==None and down_offset.get(down)==None):
            print("Scenario 1");
            up_weight=0;
            down_weight=0;
            if(up_score.get(up)!=None): up_weight=up_score[up];
            if(down_score.get(down)!=None): down_weight=down_score[down];
            
            
            if(down_weight!=0 and up_weight!=0):down_margin=(down_margin+up_margin)*(up_weight)/(up_weight+down_weight);
            up_margin=metal_spacing-down_margin;
            pattern_stripe_start_end.append([down,up,down_margin+down,up-up_margin,pattern[0],0,0]);
            up_offset[down]=down_margin;
            down_offset[up]=up_margin;
        
        #SCENARIO 2: ony one up or down PATTERN be assigned, 
        ##
        elif(up_offset.get(up)==None):
            print("Scenario 2");
            start_stripe=metal_spacing-down_offset[down];
            if(start_stripe<=0): start_stripe=0;
            pattern_stripe_start_end.append([down,up,start_stripe+down,up-metal_spacing+start_stripe,pattern[0],0,0]);
            up_offset[down]=start_stripe;
            down_offset[up]=metal_spacing-start_stripe;
            
        elif(down_offset.get(down)==None):
            print("Scenario 3");
            end_stripe=metal_spacing-up_offset[up];
            if(end_stripe<=0): end_stripe=0;
            pattern_stripe_start_end.append([down,up,metal_spacing-end_stripe+down,up-end_stripe,pattern[0],0,0]);
            print([down,up,metal_spacing-end_stripe+down,up-end_stripe,pattern[0],0]);
            up_offset[down]=metal_spacing-end_stripe;
            down_offset[up]=end_stripe;
            
        ##SCENARIO 3: both up-down PATTERN be assigned.
        ##This scenario may be occur DRC spacing, would be fixed in last step: Fixing_step
        else:
            print("Scenario 4");
            down_margin=down_offset[down];
            up_margin=up_offset[up];
            
            #This PATTERN SHOUD BE saved area to fit the DRC.
            diff=2*metal_spacing-down_margin-up_margin;
            #print("down up margin:", down_margin,up_margin)
            ##This shoud be decrease One stripe.
            compensate=0;
            up_compensate=0;
            down_compensate=0;
            
            if(diff>metal_spacing):
                compensate=metal_width-diff+metal_spacing;
                print("decrease on stripe", compensate,diff)
            up_weight=0;
            down_weight=0;
            if(up_score.get(up)!=None): up_weight=up_score[up];
            if(down_score.get(down)!=None): down_weight=down_score[down];
            print("Run compensate ")
            if(down_weight>=0.75 and up_weight>=0.75):
                up_compensate=0.5*compensate;
                down_compensate=compensate-up_compensate;
            elif(down_weight>=0.75):
                up_compensate=0.25*compensate;
                down_compensate=compensate-up_compensate;
            elif(down_weight<0.75):
                up_compensate=0.75*compensate;
                down_compensate=compensate-up_compensate;    
            else:   
                up_compensate=0.5*compensate;
                down_compensate=compensate-up_compensate;
                
            pattern_stripe_start_end.append([down,up,down+metal_spacing-down_margin+down_compensate,up-(metal_spacing-up_margin)-up_compensate,pattern[0],up_compensate,down_compensate]);
            print([down,up,down+metal_spacing-down_margin+down_compensate,up-(metal_spacing-up_margin)-up_compensate,pattern[0],up_compensate,down_compensate]);
        print("=========================")
        print("")
    return pattern_stripe_start_end;
        
            

def power_grid_pattern(design_box:list, macro_box:list, ishorizontal:bool, metal_spacing:int,metal_width:int, level:int):
    pattern_list=[];
    pattern_width=(metal_spacing+metal_width)*level*1;
    row=design_box[3]-design_box[1]+1;
    col=design_box[2]-design_box[0]+1;
    
    number_pattern=0 #Dedfine how many pattern we shoud use
    pattern_offset=0;
    if(ishorizontal):
        number_pattern=int(col/pattern_width);
        pattern_offset=col%pattern_width;
    
    else:
        number_pattern=int(row/pattern_width);
        pattern_offset=row%pattern_width;
        
        
        
    idx_score=weight_macro_score(design,macro_box);
    
    #print("CHECK OFF pattern number, offset,width:", number_pattern,pattern_offset, pattern_width);
    
    #Firstly Add offset Region.
    
    score=0;
    area=0;    
    start=0;
    if(ishorizontal):
        for y in range(pattern_offset):
            for x in range(row):
                score+=idx_score[y][x];
                area+=1;
    else :
        for x in range(pattern_offset):
            for y in range(col):
                score+=idx_score[x][y];
                area+=1;

    for idx in range(number_pattern):

        if(ishorizontal):
            for y in range(pattern_width):
                for x in range(row):
                    score+=idx_score[y+start][x];
                    area+=1;
        
        else :
            for x in range(pattern_width):
                for y in range(col):
                    score+=idx_score[x][y+start];
                    area+=1;
        end=0;
        if(idx==0): end=start+pattern_width+pattern_offset;
        else: end=start+pattern_width;
        pattern_list.append([score,area,start,end]);
        start=end;
        score=0;
        area=0;
    #print(pattern_list)
    #print("After Merge Pattern:")    
    pattern_list=merge_pattern(pattern_list);
    #print(pattern_list)
    #print("After Normalization Pattern:")
    pattern_list=normalization_score(pattern_list);
    #print(pattern_list)
    pattern_list.sort(reverse=True,key=lambda score: score[0]);
    #print("Sort:")
    #print(pattern_list)
    
    
    down_score={};
    up_score={};
    for pattern in pattern_list:
        down=pattern[1];
        up=pattern[2];
        down_score[up]=pattern[0];
        up_score[down]=pattern[0];
    
    
    
    return pattern_list,down_score,up_score,pattern_width;
    
    
#If macro is no-score defined on user it would use area-score!
def weight_macro_score(design_box:list, macro_box:list, ishorizontal:bool):
    row=design_box[3]-design_box[1]+1;
    col=design_box[2]-design_box[0]+1;
    
    macro_area=[];
    print(macro_box)
    if(len(macro_box[0])==4):
        for macro in macro_box:
            macro_row=macro[3]-macro[1]+1;
            macro_col=macro[2]-macro[0]+1;
            macro.append(macro_row*macro_col);
            macro_area.append(macro_row*macro_col);
     
        macro_area=normalization_score1(macro_area);
        
        for idx in range(len(macro_box)):
            macro_box[idx][4]=macro_area[idx];
    
    idx_score = [[0] * row for _ in range(col)]
    for mdx in macro_box:
        score=mdx[4];
        for idx in range(mdx[0],mdx[2]+1):
            for idy in range(mdx[1], mdx[3]+1):
                idx_score[idx][idy]+=score;
    
    return idx_score;


#Merge same scroe of pattern to decrease run time!              
def merge_pattern(pattern_list:list):
    merge_list=[];
    pre_score=-1;
    pre_start=0;
    pre_end=0;
    area=0;
    for pattern in pattern_list:
        if(pre_score==-1):
            pre_score=pattern[0];
            pre_start=pattern[2];
            pre_end=pattern[3];
            area=pattern[1];
        elif(pre_score==pattern[0]):
            pre_end=pattern[3];
            area+=pattern[1];
            
        else:
            merge_list.append([pre_score/area,pre_start,pre_end]);
            pre_score=pattern[0];
            pre_start=pattern[2];
            pre_end=pattern[3];
            area=pattern[1];
    
    merge_list.append([pre_score/area,pre_start,pre_end]);
    return merge_list;

#Normailized score to 
def normalization_score1(pattern_list:list):
    score_list=[]
    for score in pattern_list:
        score_list.append(score);
        
    #mi=np.min(score_list);
    mi=0;
    ma=np.max(score_list);
   
    for idx in range(len(pattern_list)):
        pattern_list[idx]=(pattern_list[idx]-mi)/(ma-mi);
        
    return pattern_list;

def normalization_score(pattern_list:list):
    score_list=[]
    for score in pattern_list:
        score_list.append(score[0]);
        
    mi=np.min(score_list);
    ma=np.max(score_list);
    for pattern in pattern_list:
        pattern[0]=(pattern[0]-mi)/ma-mi;
        
    return pattern_list;
   
def macro_based_power_planning(design_box:list, macro_box:list,metal_spacing:int, metal_width:int, opt_type:str):
    pattern_list,down_score,up_score,pattern_width=power_grid_pattern(design,macro_box,True,metal_spacing,metal_width,1);
    print("End of power_grid_pattern:")
    #print(pattern_list)
    #print(down_score)
    #print(up_score)
    print("=======================================")
    pattern_stripe_start_end=power_grid_planning(pattern_list,up_score,down_score,metal_spacing,metal_width,pattern_width);
    print("End of power_grid_planning:")
    print(pattern_stripe_start_end)
    
    opt_power_grid_planning(pattern_stripe_start_end,metal_spacing, metal_width,opt_type)

design=[0, 0,30,30]
macro=[[0,0,10,10,2],[15,15,25,25,3]]

#design_score=weight_macro_score(design,macro);
#power_grid_pattern(design,macro,True,2,2,1);
#macro_based_power_planning(design,macro,3,2,"space");
macro_based_power_planning(design,macro,3,2,"width");

