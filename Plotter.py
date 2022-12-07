# https://pythonprogramming.net/live-graphs-matplotlib-tutorial/

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
	demLines = []
	repLines = []
	try:
		demFile = open('demResults.txt','r')
		demGraphData = demFile.read()
		demFile.close()
		demLines = demGraphData.split('\n')
		repFile = open('repResults.txt','r')
		repGraphData = repFile.read()
		repFile.close()
		repLines = repGraphData.split('\n')
	except FileNotFoundError:
		print("WARNING!")
		print("One or more results files do not exist!")
	times = []
	demVotes = []
	repVotes = []
	for demLine in demLines:
		if len(demLine) > 1:
			time, demVote = demLine.split(',')
			times.append(float(time))
			demVotes.append(int(demVote))
	for repLine in repLines:
		if len(repLine) > 1:
			time, repVote = repLine.split(",")
			repVotes.append(int(repVote))
	ax1.clear()
	ax1.set_title('Georgia Runoff Results')
	ax1.set_xlabel('time')
	ax1.set_ylabel('vote count')
	ax1.plot(times, demVotes, label="dem")
	ax1.plot(times, repVotes, label="rep")
	ax1.legend(loc="upper left")
		
	
ani = animation.FuncAnimation(fig, animate, interval=30000)
plt.show()