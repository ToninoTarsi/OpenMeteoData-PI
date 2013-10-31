import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager


#path = 'c:/windows/fonts/meteocons.ttf'
path = 'img/meteocons.ttf'
prop = font_manager.FontProperties(fname=path)
fig, ax = plt.subplots()
ax.set_title('123456788ABCDEFGHILMN', fontproperties=prop, size=40)
plt.show()


exit()

path = '/usr/share/fonts/truetype/meteocons.ttf'
prop = font_manager.FontProperties(fname=path)
fig, ax = plt.subplots()
ax.set_title('123456788ABCDEFGHILMN', fontproperties=prop, size=40)
plt.savefig("pp.png", dpi=100,bbox_inches='tight',transparent=True)
plt.show()




path = 'c:/windows/fonts/meteocons.ttf'
prop = font_manager.FontProperties(fname=path)
mpl.rcParams['font.family'] = prop.get_name()
fig, ax = plt.subplots()
ax.set_title('Text in a cool font', size=40)
plt.show()












