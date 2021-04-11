# import section
from pathlib import Path
import matplotlib.pyplot as plt
import sys
import os
#from CifFile import ReadCif

# input section
INPUT_FILE_NAME = 'aj5301cubic_1_NDsup19.rtv.combined.cif'

# path and folders section
src_path = Path.cwd()
parent_path = src_path.resolve().parent
data_path = parent_path / 'data'
png_path = parent_path / 'png'
txt_path = parent_path / 'txt'
file_path = data_path / INPUT_FILE_NAME
file_name = file_path.stem
# print(file_name)
# sys.exit()

folders = [png_path, txt_path]
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

# data section
with open(file_path, mode='r',encoding='utf-8') as file:
    lines = file.readlines()

for i in range(0,len(lines)):
    if '_pd_proc_intensity_bkg_calc' in lines[i]:
        start = i + 2
    elif '_pd_proc_number_of_points' in lines[i]:
        end = i

twotheta,intensity = [],[]
for i in range(start,end):
    twotheta.append(float(lines[i].split()[1]))
    intensity.append(float(lines[i].split()[2].split('(')[0]))
# print(twotheta[0],twotheta[-1],len(twotheta))
# print(intensity[0],intensity[-1],len(intensity))
# sys.exit()

# writer section
txt_file_name = str(txt_path / file_name) + '.txt'
txt = []
for i in range(0,len(twotheta)):
    if len(str(twotheta[i])) < 8:
        txt.append(str(twotheta[i]) + 2*'\t' + str(intensity[i]) + '\n')
    elif len(str(twotheta[i])) >= 8:
        txt.append(str(twotheta[i]) + '\t' + str(intensity[i]) + '\n')
# print(txt[0])
# print(txt[-1])
# sys.exit()
with open(txt_file_name,mode = 'w') as output_file:
    output_file.writelines(txt)
output_file.close()


# plot section
png_file_name = str(png_path / file_name) + '.png'
#png_file_name = png_path / file_name + '.png'
#print(png_file_name)
#sys.exit()
plt.figure(figsize=(12,4),dpi=300)
plt.plot(twotheta,intensity)
plt.xlabel(r'$2\theta$ $[\degree]$')
plt.ylabel(r'$I$ $[\mathrm{counts}]$')
plt.ticklabel_format(style = 'sci', axis = 'y', scilimits = (0,0))

# x_range = max(twotheta) - min(twotheta)
# y_range = max(intensity) - min(intensity)
plt.xlim(min(twotheta), max(twotheta))
#plt.ylim(min(intensity), max(intensity))

#plt.show()
plt.savefig(png_file_name,bbox_inches = 'tight')
plt.close()