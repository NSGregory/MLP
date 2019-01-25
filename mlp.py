

#import pyvttbl as pt
#import statsmodels

import importlib
import os
import shutil
import datetime
from lib import FR_Buddy as frb
from lib import sc_assess as sca
from lib import parse_experiment_type as parse
from lib import lab_ppt as ppt

# Still actively changing many of these modules and this is the only way I know
# to make them reflect changes as they happen
importlib.reload(frb)
importlib.reload(sca)
importlib.reload(parse)
importlib.reload(ppt)

cwd = os.getcwd()
d = datetime.datetime.today().strftime('%Y-%m-%d')

# Sort through excel files in the folder and if they match the pattern, create
# graphs
experiments = parse.EXparse()
experiments.processFile()

# This puts graphs into the presentation and moves them to a folder with the
# day's date
presentation = ppt.powerPoint()
presentation.make_title()
presentation.get_images() # Moves the "gotten" images to the folder as it loads
                          # them into the pptx.
presentation.prs.save("Lab_meeting.pptx")
shutil.move("Lab_meeting.pptx", cwd+"\\"+d+"\\")
