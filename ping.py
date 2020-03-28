from pythonping import ping
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.ensemble import AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
import datetime as dt
import json

import warnings
warnings.filterwarnings("ignore") #Ignore warnings

count = 50 #Number of pings per sample

with open('data.json') as f: #Open recorded data
  range_estimation = json.load(f)

try:
    k = True #Sample first time or not
    while(True):
        #Check the ping
        while(True):
            try:
                print("Taking ping") #Making ping
                a = ping('www.google.com', verbose=False,count = count)
                break
            except:
                pring("Trying agian...") #An error happen in the pythonping function

        #Convert the pings optain in a list
        aux = str(a).replace("\r\n"," ").split(" ")
        l_aux = []
        for i in range(len(aux)-1):
            if aux[i][len(aux[i])-2:] == "ms":
                l_aux.append(aux[i].replace("ms",""))
        if k: #First sample when the program is execute
            l =  np.array(list(map(lambda x: float(x),l_aux)))
            k = False
        else: #Rest of the time
            l = np.array(l[count:].tolist()  + list(map(lambda x: float(x),l_aux)))
        ##########################

        n = len(l) #size of list
        x = np.arange(n)[:, np.newaxis] #x axis
        plt.xticks(x) #put axis x as int

        print("Analizing data")
        rng = np.random.RandomState(1)
        #Estimation
        regr_2 = AdaBoostRegressor(DecisionTreeRegressor(max_depth=4),n_estimators=300, random_state=rng)

        scl = StandardScaler()
        x_scaled = scl.fit_transform(x) #Scale the data
        l_tree = l[:, np.newaxis]
        regr_2.fit(x_scaled, l_tree) #Training
        y_2 = regr_2.predict(x_scaled) #Making regresion

        x = x.reshape(-1) #we need to do this to ploting

        print("Plotting")
        fig = plt.figure(1,figsize = (50,50))
        fig.suptitle('Internet connection', fontsize=20)
        plt.subplot(3,1,1)

        #ranges and colors of the ranges
        colors = ['white','#b3ffb3','#66ff66','#ffbf80','#ff9933','#e62e00','#661400','#330a00']
        ranges = [0,30,60,90,120,150,180,210]

        ma = max(l) #Max value on the stream
        mi = min(l) #Min value on the stream
        me = np.mean(l) #Mean value of the string
        nr = len(ranges)

        #Draw the ranges
        for i in range(1,len(colors)):
            if ma > ranges[i-1] and mi < ranges[i]:
                if i == nr -1:
                    ranges[i] = max(l)
                y = np.ones(n) * ranges[i]
                y0 = np.ones(n) * ranges[i-1]
                plt.fill_between(x, y0,y, color=colors[i])
        ##############

        plt.plot(x,l,'bo', label = "ping") #Plot the ping obtain
        plt.plot(x,y_2,'k-', label= "estimation")
        plt.xlabel('number pings', fontsize=14)
        plt.ylabel('time ms', fontsize=14)
        plt.legend()

        plt.subplot(3,1,2)
        for i in range(1,len(colors)):
            if ranges[i-1] <= me <= ranges[i]: #Plot values between ranges
                boxplot = sns.boxplot(data=l,orient= 'h', color =colors[i]) #Plot the box plot
                break
            if i == len(colors) -1: #Plot in case is the last element
                boxplot = sns.boxplot(data=l,orient= 'h', color =colors[i])

        plt.subplot(3,1,3)
        color_range = []
        aux_mean = []
        for j in range_estimation.keys():
            for i in range(1,len(colors)):
                if range_estimation[j]["count"] > 0: #Calculating mean from recorded data
                    aux = np.log(int(range_estimation[j]["total"]/range_estimation[j]["count"]))
                    aux2 = int(range_estimation[j]["total"]/range_estimation[j]["count"])
                else:
                    aux = 0
                    aux2 = 0
                if ranges[i-1] <= aux2 <= ranges[i]: #Ajusting colors
                    color_range.append(colors[i])
                    aux_mean.append(aux)
                    break
                if aux2 > ranges[len(colors)-1]: #Ajusting if mean is in the last range
                    color_range.append(colors[len(colors)-1])
                    aux_mean.append(aux)
                    break
        plt.bar(np.arange(16) + 8,aux_mean, color = color_range)
        plt.xlabel('hours in day', fontsize=14)
        plt.ylabel('log(time) ms', fontsize=14)
        try:
            #Recording the new data
            h = dt.datetime.today().hour
            range_estimation[str(h)]["total"] += int(me)
            range_estimation[str(h)]["count"] += 1
        except:
            #Case we record outside the time
            print("Time out of range")
        plt.draw() #Draw plots
        plt.pause(2) #Time between refressing plots
        plt.clf()

except KeyboardInterrupt: #Closing program if user make ctrl + C
    print("Closing program")
except Exception as e: #Closing program because there was an unexpecte it error
    print(e)
finally:
    #Before close the program save the data
    print("Saving the data")
    with open('data.json', 'w') as f:
        json.dump(range_estimation, f)
