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
  
  
import MySQLdb.cursors
import specificIMDbQueries

queries = []

queries.append(('generic Runtime', specificIMDbQueries.GenericRuntimeQuery()))
queries.append(('feature film runtime', specificIMDbQueries.FeatureFilmRuntimeQuery()))
queries.append(('bracketed runtime', specificIMDbQueries.BracketedRuntimeQuery()))
queries.append(('generic genres', specificIMDbQueries.GenreQuery()))
queries.append(('feature film genres', specificIMDbQueries.FeatureFilmGenreQuery()))
queries.append(('genre sums', specificIMDbQueries.GenreSumQuery()))
queries.append(('feature film genre sums', specificIMDbQueries.FeatureFilmGenreSumQuery()))

db     = MySQLdb.connect(host="192.168.2.120", user="external", passwd="password", db="imdb", port=3306, cursorclass=MySQLdb.cursors.DictCursor)
cursor = db.cursor()

for (queryName, query) in queries:
  print "\n\n-- Starting " + queryName + " query:"
  query.startQuery(cursor)

cursor.close()

print "\n\nAll done!"