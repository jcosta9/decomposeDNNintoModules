'''
Created on Mar 29, 2019

@author:  
'''


from __future__ import print_function
import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
import numpy as np
import matplotlib.pyplot as plt

import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import RMSprop
import tensorflow as tf
from skimage.transform import resize
from graphviz import Graph, render
from collections import defaultdict 
import queue as Q
from mpmath.tests.test_linalg import b1


class Slice:
    
    def __init__(self):
        self.W1 = None
        self.W2 = None
        self.b1 = None
        self.b2 = None
        self.D1 = None
        self.D2 = None
        self.d1 = None
        self.d2 = None
        self.first = True
    
    
    
    '''
    Return the static weights of the model
    '''
    
    def getweights(self, nm):
        w1,b1 = nm.layers[1].get_weights()
        w2,b2 = nm.layers[2].get_weights()
        w3,b3 = nm.layers[3].get_weights()
        w4,b4 = nm.layers[4].get_weights()
        w5,b5 = nm.layers[5].get_weights()
        W1 = np.vstack([w1])
        W2 = np.vstack([w2])
        W3 = np.vstack([w3])
        W4 = np.vstack([w4])
        W5 = np.vstack([w5])
        self.W1 = W1
        self.W2 = W2 
        self.W3 = W3
        self.W4 = W4 
        self.W5 = W5
        self.b1 = b1
        self.b2 = b2
        self.b3 = b3
        self.b4 = b4
        self.b5 = b5
        self.D1 = np.zeros_like(W1)
        self.D2 = np.zeros_like(W2)
        self.D3 = np.zeros_like(W3)
        self.D4 = np.zeros_like(W4)
        self.D5 = np.zeros_like(W5)
        self.d1 = np.zeros_like(b1)
        self.d2 = np.zeros_like(b2)
        self.d3 = np.zeros_like(b3)
        self.d4 = np.zeros_like(b4)
        self.d5 = np.zeros_like(b5)
        return W1, W2, W3, W4, W5, b1, b2, b3, b4, b5
    
    '''
    Softmax function
    '''
    def softmax(self,x):
        """Compute softmax values for each sets of scores in x."""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0) # only difference
    '''
    Get the dynamic values at different nodes 
    '''
    def dynamicmodify(self, nm, x,img_rows = 28, img_cols = 28):
        X = x.reshape(img_rows*img_cols,)
        X1 = np.dot(X,self.W1)
        X1 = np.add(X1, self.b1)
        X2 = np.dot(X1,self.W2)
        X2 = np.add(X2,self.b2)
        X3 = np.dot(X2,self.W3)
        X3 = np.add(X3,self.b3)
        X4 = np.dot(X3,self.W4)
        X4 = np.add(X4,self.b4)
        X5 = np.dot(X4,self.W5)
        X5 = np.add(X5,self.b5)
        X5 = self.softmax(X5)
        X1[X1<0]=0
        #W1 = np.zeros_like(self.W1)
        #W2 = np.zeros_like(self.W2)
        #b1 = np.zeros_like(self.b1)
        #b2 = np.zeros_like(self.b2)
        for i in range(X1.shape[0]):
            if X1[i] <= 0:
                #print("Zero X1")
                self.D1[:,i] = [x for x in self.D1[:,i]]
            else:
                self.D1[:,i] = self.W1[:,i]
                self.d1[i] = self.b1[i]
        X2[X2<0]=0
        for i in range(X2.shape[0]):
            if X2[i] <= 0:
                #print("Zero X1")
                self.D2[:,i] = [x for x in self.D2[:,i]]
            else:
                self.D2[:,i] = self.W2[:,i]
                self.d2[i] = self.b2[i]
        X3[X3<0]=0
        for i in range(X3.shape[0]):
            if X3[i] <= 0:
                #print("Zero X1")
                self.D3[:,i] = [x for x in self.D3[:,i]]
            else:
                self.D3[:,i] = self.W3[:,i]
                self.d3[i] = self.b3[i]
        X4[X4<0]=0
        for i in range(X4.shape[0]):
            if X4[i] <= 0:
                #print("Zero X1")
                self.D4[:,i] = [x for x in self.D4[:,i]]
            else:
                self.D4[:,i] = self.W4[:,i]
                self.d4[i] = self.b4[i]
        for i in range(X5.shape[0]):
            if X5[i] <=.5:
                #print("Zero X2")
                self.D5[:,i] = [x for x in self.D5[:,i]]
            else:
                self.D5[:,i] = self.W5[:,i]
                self.d5[i] = self.b5[i]
        
        #print("D1")
        #print(self.D1)
        #print("D2")
        #print(self.D2)
        return self.D1, self.D2, self.D3, self.D4, self.D5, self.d1, self.d2, self.d3, self.d4, self.d5
    def backtrack (self, intent):
        #Pre-Step1: Remove the edges only incident to the negative ones with one edge
        tempD5=[]
        for i in range(self.D5.shape[0]):
            temp1=[]
            temp2=[]
            if(self.D5[i,intent]<0.05 and self.D5[i,intent]>-0.05 and self.D5[i,intent]!=0):
                #print('yipee')
                for j in range(0,10):
                    if(j!=intent):
                        if(self.D5[i,j]!=0):
                            temp1.append(self.D5[i,j])
                            temp2.append(j)
                if(intent==0):
                    
                    self.D5[i,1]=np.mean(temp1)
                    if(np.isnan(self.D5[i,1])):
                        self.D5[i,1]=0
                    
                    for k in temp2:
                        self.D5[i,k]=0
                else:
                    self.D5[i,0]=np.mean(temp1)
                    if(np.isnan(self.D5[i,0])):
                        self.D5[i,0]=0
                    for k in temp2:
                        self.D5[i,k]=0
                tempD5.append(i)
        print(tempD5)
        if(len(tempD5)>1):
            if(intent==0):
                a=0
                for i in tempD5:
                    a+=self.D5[i,0] 
                    #print(a)
                    #print(len(tempD2))
                self.D5[tempD5[0],1]=a/len(tempD5)
                if(np.isnan(self.D5[tempD5[0],1])):
                        self.D5[tempD5[0],1]=0
                for x in tempD5[1:len(tempD5)]:
                    self.D5[x,1]=0
                    #self.d4[x]=0
            else:
                a=0
                for i in tempD5:
                    a+=self.D5[i,1] 
                self.D5[tempD5[0],0]=a/len(tempD5)
                if(np.isnan(self.D5[tempD5[0],0])):
                    self.D5[tempD5[0],0]=0
                for x in tempD5[1:len(tempD5)]:
                    #print(tempD4)
                    self.D5[x,0]=0
                    #print(x)
                    #self.d4[x]=0
        
            for i in range(self.D4.shape[0]):
                tempD4=[]
                for j in tempD5:
                    tempD4.append(self.D4[i,j])
                self.D4[i,tempD5[0]]=np.mean(tempD4)
                #print(np.mean(tempD4))
                if(np.isnan(self.D4[i,tempD5[0]])):
                        self.D4[i,tempD5[0]]=0
                for x in tempD5[1:len(tempD5)]:
                        self.D4[i,x]=0
        #Step 1: Short circuit the output nodes
        for i in range(self.D5.shape[0]):
            temp=self.D5[i,:]
            if (intent==0):
                temp[1]=np.mean(temp[1:10])
                temp[2:10]=0
                #print(self.d2[1:10])
                #self.d2[1]=np.mean(self.d2[1:10])
                #self.d2[2:10]=0
            else:
                tempW5 = [0] * (len(temp)-1)
                tempB5=[0] * len(self.d5)
                k=0
                for j in range(0,10):
                    
                    if(j!=intent):
                        tempW5[k]=temp[j]
                        tempB5[k]=self.d5[j]
                        k=k+1
                temp[0]=np.mean(tempW5)
                #self.d2[0]=np.mean(tempB2)
                for j in range(1,10):
                    if(j!=intent):
                        temp[j]=0
                        #self.d2[j]=0
            self.D5[i,:]=temp
        if(intent==0):
            self.d5[1]=np.mean(self.d5[1:10])
            self.d5[2:10]=0
        else:
            self.d5[0]=np.mean(tempB5)
            for j in range(1,10):
                    if(j!=intent):
                        self.d5[j]=0
        #Step 2: Remove irrelevant edges with one common edge.
        for i in range(self.D5.shape[0]):
            temp=[]
            if(intent==0):
                if(self.D5[i,0]==0 and self.D5[i,1]!=0):
                    temp.append(i)
            else:
                if(self.D5[i,0]!=0 and self.D5[i,intent]==0):
                    temp.append(i)
        # #counter=0
        # if(len(temp)>0):
        #     print("length:"+str(len(temp)))
        #     if(intent==0):
        #         tempD5=[]
        #         tempd5=[]
        #         for x in temp:
        #             tempD5.append(self.D5[x,1])
        #             tempd5.append(self.d5[x])
        #         self.D5[temp[0],1]=np.mean(tempD5)
        #         self.d5[temp[0]]=np.mean(tempd5)
        #         for x in temp[1:len(temp)]:
        #             self.D5[x,1]=0
        #             self.d5[x]=0
        #     if(intent!=0):
        #         tempD5=[]
        #         tempd5=[]
        #         for x in temp:
        #             tempD5.append(self.D5[x,1])
        #             print(x)
        #             #tempd5.append(self.d5[x])
        #         self.D5[temp[0],0]=np.mean(tempD5)
        #         #self.d5[temp[0]]=np.mean(tempd5)
        #         for x in temp[1:len(temp)]:
        #             self.D5[x,0]=0
        #             #self.d5[x]=0
        #     for i in range(self.D4.shape[0]):
        #         tempD4=[]
        #         tempd4=[]
        #         for j in temp:
        #             tempD4.append(self.D4[i,j])
        #             #tempd4.append(self.d4[i,j])
        #         self.D4[i:temp[0]]=np.mean(tempD4)
        #         for x in temp[1:len(temp)]:
        #             self.D4[i:x]=0
    def modifyThroughInterSection(self,nm, x,img_rows = 28, img_cols = 28):
        X = x.reshape(img_rows*img_cols,)
        X1 = np.dot(X,self.W1)
        X1 = np.add(X1, self.b1)
        X2 = np.dot(X1,self.W2)
        X2 = np.add(X2,self.b2)
        X3 = np.dot(X2,self.W3)
        X3 = np.add(X3,self.b3)
        X4 = np.dot(X3,self.W4)
        X4 = np.add(X4,self.b4)
        X5 = np.dot(X4,self.W5)
        X5 = np.add(X5,self.b5)
        X5 = self.softmax(X5)
        X1[X1<0]=0
        #W1 = np.zeros_like(self.W1)
        #W2 = np.zeros_like(self.W2)
        #b1 = np.zeros_like(self.b1)
        #b2 = np.zeros_like(self.b2)
        for i in range(X1.shape[0]):
            if X1[i] <= 0:
                #print("Zero X1")
                self.D1[:,i] = [0 for x in self.D1[:,i]]
                self.D2[i,:]=[0 for x in self.D2[i,:]]
                self.d1[i] = 0
            else:
                if self.first == True:
                    self.D1[:,i] = self.W1[:,i]
                    self.d1[i] = self.b1[i]
                else:
                    for j in range(0,len(self.W1[:,i])):
                        if self.W1[j,i] < 0 :
                            self.D1[j,i] = max(self.D1[j,i], self.W1[j,i])
                            if(self.D1[j,i]<0):
                                self.D1[j,i]=0
                        else:
                            self.D1[j,i] = min(self.D1[j,i], self.W1[j,i])
                    self.d1[i] = self.b1[i]
        for i in range(X2.shape[0]):
            if X2[i] <= 0:
                #print("Zero X1")
                self.D2[:,i] = [0 for x in self.D2[:,i]]
                self.D3[i,:]=[0 for x in self.D3[i,:]]
                self.d2[i] = 0
            else:
                if self.first == True:
                    self.D2[:,i] = self.W2[:,i]
                    self.d2[i] = self.b2[i]
                else:
                    for j in range(0,len(self.W2[:,i])):
                        if self.W2[j,i] < 0 :
                            self.D2[j,i] = max(self.D2[j,i], self.W2[j,i])
                            if(self.D2[j,i]<0):
                                self.D2[j,i]=0
                        else:
                            self.D2[j,i] = min(self.D2[j,i], self.W2[j,i])
                    self.d2[i] = self.b2[i]
        for i in range(X3.shape[0]):
            if X3[i] <= 0:
                #print("Zero X1")
                self.D3[:,i] = [0 for x in self.D3[:,i]]
                self.D4[i,:]=[0 for x in self.D4[i,:]]
                self.d3[i] = 0
            else:
                if self.first == True:
                    self.D3[:,i] = self.W3[:,i]
                    self.d3[i] = self.b3[i]
                else:
                    for j in range(0,len(self.W3[:,i])):
                        if self.W3[j,i] < 0 :
                            self.D3[j,i] = max(self.D3[j,i], self.W3[j,i])
                            if(self.D3[j,i]<0):
                                self.D3[j,i]=0
                        else:
                            self.D3[j,i] = min(self.D3[j,i], self.W3[j,i])
                    self.d3[i] = self.b3[i]
        for i in range(X4.shape[0]):
            if X4[i] <= 0:
                #print("Zero X1")
                self.D4[:,i] = [0 for x in self.D4[:,i]]
                #self.D5[i,:]=[0 for x in self.D5[i,:]]
                self.d4[i] = 0
            else:
                if self.first == True:
                    self.D4[:,i] = self.W4[:,i]
                    self.d4[i] = self.b4[i]
                else:
                    for j in range(0,len(self.W4[:,i])):
                        if self.W4[j,i] < 0 :
                            self.D4[j,i] = max(self.D4[j,i], self.W4[j,i])
                            if(self.D4[j,i]<0):
                                self.D4[j,i]=0
                        else:
                            self.D4[j,i] = min(self.D4[j,i], self.W4[j,i])
                    self.d4[i] = self.b4[i]
        for i in range(X5.shape[0]):
            # if X5[i] <= .0001:
            #     #print("Zero X2")
            #     self.D5[:,i] = [ 0 for x in self.D5[:,i]]
            #     self.b5[i] = 0
            # else:
            if self.first == True:
                self.D5[:,i] = self.W5[:,i]
                self.d5[i] = self.b5[i]
            else:
                for j in range(0,len(self.W5[:,i])):
                    if self.W5[j,i] < 0 :
                        self.D5[j,i] = max(self.D5[j,i], self.W5[j,i])
                        # if(self.D2[j,i]<0):
                        #     self.D2[j,i]=0
                    else:
                        self.D5[j,i] = min(self.D5[j,i], self.W5[j,i])
                    #self.D2[:,i] = self.W2[:,i]
                self.d5[i] = self.b5[i]
        
        #print("D1")
        #print(self.D1)
        #print("D2")
        #print(self.D2)
        if self.first == True:
            self.first = False
        return self.D1, self.D2, self.D3, self.D4, self.D5, self.d1, self.d2, self.d3, self.d4, self.d5
    
    def getLabel(self,y):
        one = [0, 1]
        zer = [1 , 0]
        if y == 1:
            return 1
        elif y == 0:
            return 0
        elif (y == one).all():
            return 1
        else:
            return 0
    def getLabel2(self, y):
        return y[0]
    
    def showstatweights(self,nm, x, y,img_rows = 28, img_cols = 28, ss = .2):
        w1,b1 = self.D1, self.d1
        w2,b2 = self.D2, self.d2
        W1 = np.vstack([w1])
        print(W1.shape)
        X = x.reshape(img_rows*img_cols,)
        X1 = np.dot(X,W1)
        X1 = np.add(X1, b1)
        X1[X1<0]=0
        W2 = np.vstack([w2])
        X2 = np.dot(X1,W2)
        X2 = np.add(X2,b2)
        X2 = self.softmax(X2)
        dot = Graph(format='png')
        #dot.attr(bgcolor='purple:pink', kw = "edge", style = "invis",nodesep = "0")
        dot.attr(bgcolor='purple:pink', kw = "edge", color = "yellow",nodesep = "0")
        dot.attr(kw = "graph", nodesep = "0", ranksep = "0")
        
        color = ["red","green"]
        green = ["springgreen","springgreen1","springgreen2","springgreen3","springgreen4"]
        edgep = ["springgreen","springgreen1","springgreen2","springgreen3","springgreen4"]
        edgen = ["rosybrown1", "salmon", "orange", "orangered", "red", "red3"]
        dot.node('I',"",color = "black",style = "filled",**{'width':str(.2), 'height':str(.2)})
        maxa = np.amax(X)
        maxc = np.amax(W1)
        maxd = np.amax(W2)
        print(maxa,maxc,maxd)
        A = []
        s = ss
        
        
        for i in range(X.shape[0]):
            if X[i] > 0:
                ind = int((X[i])//(maxa/4))
                #print(ind,X[i])
                c = green[ind]
                dot.node('x_'+str(i), "", color = "black",fillcolor = "black", style  = "filled",**{'width':str(s), 'height':str(s)})
            else :
                dot.node('x_'+str(i), "", color = "black", style  = "filled",**{'width':str(s), 'height':str(s)})
        E = []
        total = 0
        for j in range(X.shape[0]):
            total += 1
            #if X[j] > 0:
            #E.append(('I','x_'+str(j))) # May need uncommenting
            dot.edge('I','x_'+str(j), style ="invis")
            
    
        #print(len(E),total,100*len(E)/total)
        #A.append(100*len(E)/total)
        #dot.edges(E) # My need uncommenting
        for i in range(X1.shape[0]):
            if X1[i] > 0:
                ind = int((X1[i])//(maxc/4))
                c = green[ind]
                dot.node('x1_'+str(i), "", color = "black", fillcolor = "black",style  = "filled",**{'width':str(s), 'height':str(s)})
            else :
                dot.node('x1_'+str(i),"", color = "black", fillcolor = "black", style  = "filled",**{'width':str(s), 'height':str(s)})
    
        E1 = []
        total = 0
        print(X1.shape," Here")
        minw = 0
        maxw = -1
        indices1 = []
        
        # Getting max w phase
        for j in range(W1.shape[1]):
            for i in range(X.shape[0]):

                if True:
                    #E1.append(('x_'+str(i),'x1_'+str(j))) # May need uncommenting
                    w = W1[i][j]
                    maxw = max(maxw,w)
                    minw = min(w, minw)
                    sw = w *255
        
        for j in range(W1.shape[1]):
            for i in range(X.shape[0]):
                total += 1
                if (W1[i][j]  == 0):
                    dot.edge('x_'+str(i),'x1_'+str(j), style = "invis")
                    continue
                if True:
                    #E1.append(('x_'+str(i),'x1_'+str(j))) # May need uncommenting
                    w = W1[i][j]
                    sw = w *255
                    if sw <= 0:
                        ind = int(abs(sw)/((abs(minw) * 255)/5))
                        c = edgen[ind]
                        dot.edge('x_'+str(i),'x1_'+str(j), color = c)
                        indices1.append("n{}".format(ind))
                    else:
                        ind = int(sw/((maxw * 255)/4))
                        #print(ind)
                        c = edgep[ind]
                        dot.edge('x_'+str(i),'x1_'+str(j), color = c)
                        indices1.append("p{}".format(ind))
        # Adding edges
        #print(len(E1),total,100*len(E1)/total)
        print(maxw, minw, "MINMAX W")
        A.append(100*len(E1)/total)
        #dot.edges(E1) # May need uncommenting
        for i in range(X2.shape[0]):
            if X2[i] > 0:
                ind = int((X2[i])//(maxd/4))
                c = green[ind]
                dot.node('x2_'+str(i), "", color = "black", fillcolor = "black", style  = "filled",**{'width':str(s), 'height':str(s)})
            else :
                dot.node('x2_'+str(i), "", color = "black", fillcolor = "black",style  = "filled",**{'width':str(s), 'height':str(s)})
        E2 = []
        total = 0
        minw = 0
        maxw = -1
        for j in range(W2.shape[1]):
            for i in range(X1.shape[0]):
                if True:
                    #E1.append(('x_'+str(i),'x1_'+str(j))) # May need uncommenting
                    w = W2[i][j]
                    maxw = max(maxw,w)
                    minw = min(w, minw)
                    sw = w *255
            
        indices2 = []
        for j in range(W2.shape[1]):
            for i in range(X1.shape[0]):
                total += 1
                if (W2[i][j]  == 0):
                    dot.edge('x1_'+str(i),'x2_'+str(j),style  = "invis")
                    continue
                if True:
                    w = W2[i][j]
                    sw = w *255
                    if sw <= 0:
                        ind = int(abs(sw)/((abs(minw) * 255)/5))
                        c = edgen[ind]
                        dot.edge('x1_'+str(i),'x2_'+str(j),color = c)
                        indices2.append("n{}".format(ind))
                    else:
                        ind = int(sw/((maxw* 255)/4))
                        #print(ind)
                        c = edgep[ind]
                        dot.edge('x1_'+str(i),'x2_'+str(j),color = c)
                        indices2.append("n{}".format(ind))
    
                    #E2.append(('x1_'+str(i),'x2_'+str(j))) # To be uncommented if needed 
        #print(len(E2), total, 100*len(E2)/total)
        print(maxw, minw, "MINMAX W")
        indices1 = set(indices1)
        indices2 = set(indices2)
        print(indices1, indices2)
        A.append(100*len(E2)/total)
        #dot.edges(E2) # To be uncommented if needed 
        return dot, A   
    
    
    
    
