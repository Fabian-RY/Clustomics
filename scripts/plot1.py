
import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn 



def print_plot(list_info, list_group):
    data_numbers=pd.DataFrame(list_info)
    data_group=pd.DataFrame(list_group,columns=["grupo"])

    number_groups=len(set(data_group["grupo"]))

    colors=seaborn.color_palette(palette="Set1", n_colors=number_groups)

    color=[]
    for i in range(len(data_group)):
        color.append(colors[data_group["grupo"][i]])

    plt.scatter(x=data_numbers[data_numbers.columns[0]],y=data_numbers[data_numbers.columns[1]],color=color)




