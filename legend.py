import matplotlib
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.axes

def rgbspectrum(x):
    RED = [246, 52, 57]
    GRAY = [65, 69, 84]
    GREEN = [48, 204, 90]
    TOP_PERCENT_SCALE = 3 #percent
    BOTTOM_PERCENT_SCALE = -3 #percent
    if x >= TOP_PERCENT_SCALE:
        return GREEN
    elif x <= BOTTOM_PERCENT_SCALE:
        return RED
    elif x > 0:
        R = round((GREEN[0] - GRAY[0])*(x/TOP_PERCENT_SCALE)+GRAY[0],0)
        G = round((GREEN[1] - GRAY[1])*(x/TOP_PERCENT_SCALE)+GRAY[1],0)
        B = round((GREEN[2] - GRAY[2])*(x/TOP_PERCENT_SCALE)+GRAY[2],0)
        return [R, G, B]
    elif x < 0:
        R = round((RED[0] - GRAY[0])*(x/BOTTOM_PERCENT_SCALE)+GRAY[0],0)
        G = round((RED[1] - GRAY[1])*(x/BOTTOM_PERCENT_SCALE)+GRAY[1],0)
        B = round((RED[2] - GRAY[2])*(x/BOTTOM_PERCENT_SCALE)+GRAY[2],0)
        return [R, G, B]
    else:
        return GRAY

plt.figure(figsize=(16, 9))
ax1 = plt.subplot2grid((6,1), (0,0), rowspan=6, colspan=1)

for i in range(7):
    List = rgbspectrum(-3+i)
    ax1.add_patch(Rectangle((0,0+i*2), 1, 2, facecolor=(List[0]/255, List[1]/255, List[2]/255),  edgecolor = "black", linewidth = 0.5))
    ax1.text(0.5, 1+i*2, '{}%'.format(-3+i), verticalalignment = 'center', horizontalalignment = 'center', fontsize = 10)

ax1.set_xlim([0, 10])
ax1.set_ylim([0, 21])



plt.show()