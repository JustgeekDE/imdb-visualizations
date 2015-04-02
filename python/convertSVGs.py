'''
Created on 10.08.2014

@author: Philip Peter <philip.peter@justgeek.de>

As long as you retain this notice you can do whatever you want with this stuff.
If we meet some day, and you think this stuff is worth it, you can buy me a
beer in return

Philip Peter
'''
import os

if __name__ == '__main__':
    pass
  
inputDir  = '../plots/svg/'  
outputDir = '../plots/'  

width  = 1800
heigth = 1200

for item in os.listdir(inputDir):
  split = item.split(".")
  if split[-1] == "svg":
    filename = '.'.join(split[:-1])
    print "Converting "+filename
    os.system("inkscape.exe -z -e "+outputDir+filename+".png -w " + str(width) + " -h " + str(heigth) + " "+inputDir+item)
