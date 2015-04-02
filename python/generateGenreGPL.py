'''
Created on 10.08.2014

@author: Philip Peter <philip.peter@justgeek.de>

As long as you retain this notice you can do whatever you want with this stuff.
If we meet some day, and you think this stuff is worth it, you can buy me a
beer in return

Philip Peter
'''
if __name__ == '__main__':
    pass
  
from specificIMDbQueries import GenreQuery
from string import Template

header = Template("""load 'general-theme.gpl'

### Runtime Brackets ###
set title '$title'
set output imageDir.'$imagename.'.outputFormat
set multiplot
set key below samplen 1
set format y "%.2f"
set xrange[1915:2014]
set xtic mirror

set label "movies can be tagged\\nwith multiple genres" at screen 0.02, 0.98 left font ",8" front tc ls 53


plot \\""")

def getGenreIndex(genre):
  try:
    index = GenreQuery.genres.index(genre)
    return (index + 1) * 2
  except ValueError:
    return None

def getSum(genreList):
  first = True
  result = '('
  for genre in genreList:
    if not(first):
      result += '+'
    result += '$' + str(getGenreIndex(genre))
    first = False
  result+= ')'
  return result

def writeGPLFile(filename, imagename, title, relevantGenres, linestyle = 21):
  '''
  Generates a gnuplot file, in which the multiplot graphs are layered over each other.
  Each graph using the x-axis as basis
  '''
  gplFile = open(filename, 'w')
  gplFile.write(header.substitute(imagename=imagename, title = title))
  first = True
  remainingGenres = set(relevantGenres)
  for genre in relevantGenres:
    if not(first):
      gplFile.write(', \\')
    gplFile.write("\n")
    gplFile.write('  genreDataFeatures using 1:(')
    gplFile.write(getSum(remainingGenres))
    gplFile.write('/')
    gplFile.write(getSum(relevantGenres))
    gplFile.write(') with filledcurves x1 title \"'+genre+'\" ')
    gplFile.write('ls ' + str(linestyle) + ' ')
    linestyle += 1
    remainingGenres.remove(genre)
    first = False
  gplFile.close()  
  

def writeGPLFileStacked(filename, imagename, title, relevantGenres, linestyle = 21):
  '''
  Generates a gnuplot file, in which the multiplot graphs are stacked on top of each other.
  Each graph using the previous one as basis.
  '''
  gplFile = open(filename, 'w')
  gplFile.write(header.substitute(imagename=imagename, title = title))
  lastCurve = ''
  usedGenres = set()
  for genre in relevantGenres:
    usedGenres.add(genre)
    curve = '(' + getSum(usedGenres)+'/'+getSum(relevantGenres)+')'
    
    if lastCurve != '':
      gplFile.write(', \\')
    gplFile.write("\n")
    
    gplFile.write('  genreDataFeatures using 1:')
    gplFile.write(curve)
    if(lastCurve != ''):
      gplFile.write(':'+lastCurve + ' with filledcurves title \"'+genre+'\" lw 2 ')
    else:
      gplFile.write(' with filledcurves x1 title \"'+genre+'\" lw 2 ')
    gplFile.write('ls ' + str(linestyle) + ' ')
    linestyle += 1
    lastCurve = curve
  gplFile.close()  

writeGPLFile('../gnuplot/genrePlotAll.gpl',  'grouped.genre.relative.per.annum.all', 'genre distribution of feature length (40+ min) movies', GenreQuery.genres[:-3])
writeGPLFile('../gnuplot/genrePlotTop10.gpl', 'grouped.genre.relative.per.annum.10', 'genre distribution of feature length (40+ min) movies (Top 10)', GenreQuery.genres[:10])
writeGPLFile('../gnuplot/genrePlotTop15.gpl', 'grouped.genre.relative.per.annum.15', 'genre distribution of feature length (40+ min) movies (Top 15)', GenreQuery.genres[:15])
