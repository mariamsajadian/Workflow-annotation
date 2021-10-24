"""
@author: Eric

Sorry for the messy code. It will probably be difficult to get it to work like this. If you want to try out the code,
let me know and I will make some time to explain how to run the code.
"""

import pandas as pd
import numpy as np

df = pd.read_csv('results2.csv', sep=',')
df = df[df['in_out'] == 'output']
print(df['wp_geom'].mean())
print(df['wp_geom'].std())
print(df['wp_scale'].mean())
print(df['wp_scale'].std())
print(df['wp_qual'].mean())
print(df['wp_qual'].std())
print(df['wp_total'].mean())
print(df['wp_total'].std())
exit()
df['wp_total_mean'] = df.groupby(['tool_1', 'tool_2'])['wp_total'].transform('mean')
#print(df[['wp_total_mean', 'tool_1', 'tool_2', 'in_out']].loc[:5])
df = df.drop_duplicates(['tool_1', 'tool_2', 'wp_total_mean'])
groups = df[['tool_1', 'tool_2', 'wp_total_mean']].groupby(['tool_1'])
df = df.drop_duplicates(['tool_1', 'tool_2', 'wp_total_mean'])

tools_1 = ['surface-volume', 'afbuffer', 'aobuffer', 'ffclip', 'foclip', 'ofclip',
 'polyline-to-raster', 'raster-to-polygon', 'join-field', 'merge-layers',
 'raster-calculator', 'con-', 'cost-distance', 'cost-path',
 'euclidean-distance', 'extract-by-mask', 'majority-filter', 'reclassify',
 'weighted-overlay', 'zonal-statistics-as-table']

tools_2 = ['grid_analysis_0', 'grid_analysis_5', 'grid_filter_6', 'grid_gridding_10',
           'grid_tools_26', 'clip-raster-by-mask-layer', 'merge-vector-layers',
           'raster-surface-volume', 'reclassify-by-table', 'zonal-statistics',
           'polygonize', 'qfbuffer', 'qobuffer', 'ffqgisclip', 'foqgisclip', 'ofqgisclip']

tool_sets = [('ofclip', 'ofqgisclip'), ('foclip', 'foqgisclip'), ('ffclip', 'ffqgisclip'),
             ('afbuffer', 'qfbuffer'), ('aobuffer', 'qobuffer'), ('surface-volume', 'raster-surface-volume'),
             ('reclassify', 'reclassify-by-table'),
             ('merge-layers', 'merge-vector-layers'), ('cost-path', 'grid_analysis_5'),
             ('euclidean-distance', 'grid_tools_26'), ('polyline-to-raster', 'grid_gridding_10'),
             ('cost-distance', 'raster-calculator', 'grid_analysis_0'), ('extract-by-mask', 'clip-raster-by-mask-layer'),
             ('zonal-statistics-as-table', 'zonal-statistics'), ('majority-filter', 'grid_filter_6'),
             ('raster-to-polygon', 'polygonize')]

#tools_x1 = [
# 'join-field',
# 'con-',
# 'weighted-overlay', ]

checked = set()
recommended = 0
not_recommended = 0
print("Top 1 recommendation: \n")
for name, group in groups:
    largest = group.nlargest(5, 'wp_total_mean')['tool_2']
    miss = True
    for row_index, row in group.iterrows():
        for sett in tool_sets:
            check = 0
            if row['tool_2'] in sett and row['tool_1'] in sett:
                for row2 in largest:
                    if row['tool_2'] == row2:
                        print(sett, round(100 * row['wp_total_mean']) / 100)
                        #print(row['tool_1'], row['tool_2'], row['wp_total_mean'])
                        recommended += 1
                        miss = False
                if miss:
                    not_recommended += 1

print(recommended, not_recommended)
print('\nRecommended: ' + str(recommended) + '\nNot recommended: ' + str(not_recommended) +
       '\nPercentage: ' + str(round(100 * recommended / (recommended + not_recommended))) + "%")






