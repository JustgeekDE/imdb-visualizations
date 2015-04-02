'''
Created on 10.08.2014

@author: Philip Peter <philip.peter@justgeek.de>

As long as you retain this notice you can do whatever you want with this stuff.
If we meet some day, and you think this stuff is worth it, you can buy me a
beer in return

Philip Peter
'''
from genericIMDbQuery import IMDbQuery, GenericSumQuery

class GenericRuntimeQuery(IMDbQuery):
  '''
  Basic Query for number of movies and runtimes
  '''
  errorFileName = 'errors.runtime.txt'
  dataFileName  = "runtimes.dat"
  statList      = ['number', 'length', 'aggregateNumber', 'aggregateLength']
  query = """
    SELECT 
      title.id as id,
      title.production_year as year,
      runtime.info as runtime
    FROM 
      title,
      movie_info as runtime
    WHERE 
      title.kind_id in (1,3,4) AND 
      runtime.movie_id = title.id AND
      runtime.info_type_id = 1 AND
      title.id NOT IN (SELECT movie_id FROM movie_info WHERE info_type_id = 3 AND info in ('Adult','Erotica','Reality-TV','News','Talk-Show','Game-Show'))
    ORDER by year ASC
  """


  def __init__(self):
    '''
    Constructor
    '''
    super(GenericRuntimeQuery,self).__init__()
    self.tempDictionary   = {}
    self.aggregateLength = 0
    self.aggregateNumber = 0
    
  def addRow(self, row):
    movie_id = row['id']
    length   = row['runtime']
    runtime = self.convertRuntime(length)
    
    if(self.checkMovieRuntime(movie_id, runtime, length)):
      self.addLargerEntryToDict( self.tempDictionary, movie_id, runtime)
      
    return

  
  def tally(self, resultDict):
    number = 0
    length = 0
    for runtime in self.tempDictionary.values():
      number += 1
      length += runtime
      
    length = length / (24.0 * 60.0)
    self.aggregateLength += length
    self.aggregateNumber += number
    
    ''' Fill dict '''
    resultDict['number']           = number
    resultDict['length']           = length
    resultDict['aggregateNumber']  = self.aggregateNumber 
    resultDict['aggregateLength']  = self.aggregateLength
    
    ''''Clear data'''
    self.tempDictionary.clear() 
    return resultDict


class FeatureFilmRuntimeQuery(GenericRuntimeQuery):
  '''
  Just the number and runtimes of movies 45 - 300 minutes long
  '''
  dataFileName  = "runtimes.features.dat"
  errorFileName = 'errors.feature.txt'

  def checkMovieRuntime(self, movie_id, runtime, originalRuntime):
    if runtime >= 40:
      if runtime < 300:
        return True
      self.debugMessage("- Movie " + str(movie_id) + " has a runtime of " + str(runtime) + " ( " + str(originalRuntime) + " ) ")
    return False


class BracketedRuntimeQuery(GenericRuntimeQuery):
  '''
  Query for number of movies and length binned by runtime
  '''
  dataFileName  = "runtimes.brackets.dat"
  errorFileName = 'errors.brackets.txt'

  def __init__(self):
    '''
    Constructor
    '''
    super(BracketedRuntimeQuery,self).__init__()
    
    self.brackets = {0 : (0,10), 10 : (10,30), 30 : (30,60), 60 : (60,120), 120 : (120,180), 180 : (180,720)}
    self.bracketKeys = sorted(self.brackets.keys())
    
    self.statList = []
    for bracket in self.bracketKeys:
      self.statList.append(str(bracket))
      self.statList.append(str(bracket)+'-length')
    self.statList.append('total')
    self.statList.append('total-length')
    
  def getBracket(self, length):
    for bracket in self.bracketKeys:
      (minL, maxL) = self.brackets[bracket]
      if (length >= minL) and (length < maxL):
        return bracket
    return -1  

  def tally(self, resultDict):
    for runtime in self.tempDictionary.values():
      bracket = self.getBracket(runtime)
      if bracket != -1 :
        resultDict[str(bracket)] += 1
        resultDict[str(bracket)+'-length'] += runtime
        resultDict['total'] += 1
        resultDict['total-length'] += runtime
    
    self.tempDictionary.clear() 
    return resultDict


class GenreQuery(IMDbQuery):
  '''
  Query to figure out the genre distribution
  '''
  errorFileName = 'errors.genres.txt'
  dataFileName  = "genres.dat"
  genres        = ['Drama', 'Documentary', 'Comedy', 'Romance', 'Thriller', 'Action', 'Crime', 'Adventure', 'Horror', 'Music', 'Family', 'Mystery', 'Biography',
                   'History', 'Musical', 'Fantasy', 'Sci-Fi', 'War', 'Western', 'Short', 'Sport', 'Animation', 'Film-Noir', 'Lifestyle', 'Experimental', 'Commercial']
 
  query = """
    SELECT 
      title.id as id,
      title.production_year as year,
      runtime.info as runtime,
      genre.info as genre
    FROM 
      title,
      movie_info as runtime,
      movie_info as genre
    WHERE 
      title.kind_id in (1,3,4) AND 
      runtime.movie_id = title.id AND
      runtime.info_type_id = 1 AND
      genre.movie_id = title.id AND
      genre.info_type_id = 3 AND
      genre.info != '_//bbfc.co.uk/releases/import-export-2008-0_' AND
      title.id NOT IN (SELECT movie_id FROM movie_info WHERE info_type_id = 3 AND info in ('Adult','Erotica','Reality-TV','News','Talk-Show','Game-Show'))
    ORDER by year ASC
  """


  def __init__(self):
    '''
    Constructor
    '''
    super(GenreQuery,self).__init__()

    self.runtimeDictionary = {}
    self.genreDictionary   = {}
    
    self.statList = []
    for genre in self.genres:
      self.statList.append(genre)
      self.statList.append(genre+'-length')
      self.genreDictionary[genre] = set()
      
    self.statList.append('total')
    self.statList.append('total-length')
    
    
  def addRow(self, row):
    movie_id = row['id']
    length   = row['runtime']
    genre    = row['genre']
    runtime = self.convertRuntime(length)
    
    if(self.checkMovieRuntime(movie_id, runtime, length)):
      self.addLargerEntryToDict( self.runtimeDictionary, movie_id, runtime)
      self.genreDictionary[genre].add(movie_id)
    return

  
  def tally(self, resultDict):
    for genre in self.genres:
      for movie_id in self.genreDictionary[genre]:
        runtime = self.runtimeDictionary[movie_id]
        resultDict[genre] += 1
        resultDict[genre+'-length'] += runtime
        resultDict['total'] += 1
        resultDict['total-length'] += runtime
      self.genreDictionary[genre].clear()
    
    ''''Clear data'''
    self.runtimeDictionary.clear() 
    return resultDict

class FeatureFilmGenreQuery(GenreQuery):
  '''
  Just the number and runtimes of movies 45 - 300 minutes long per genre by year
  '''
  dataFileName  = "genres.features.dat"
  errorFileName = 'errors.genres.feature.txt'

  def checkMovieRuntime(self, movie_id, runtime, originalRuntime):
    if runtime >= 40:
      if runtime < 300:
        return True
      self.debugMessage("- Movie " + str(movie_id) + " has a runtime of " + str(runtime) + " ( " + str(originalRuntime) + " ) ")
    return False


class GenreSumQuery(GenericSumQuery):
  '''
  Query to figure out the genre distribution
  '''
  errorFileName = 'errors.sum.genres.txt'
  dataFileName  = "genres.sum.dat"
  genres        = ['Drama', 'Documentary', 'Comedy', 'Romance', 'Thriller', 'Action', 'Crime', 'Adventure', 'Horror', 'Music', 'Family', 'Mystery', 'Biography',
                   'History', 'Musical', 'Fantasy', 'Sci-Fi', 'War', 'Western', 'Short', 'Sport', 'Animation', 'Film-Noir', 'Lifestyle', 'Experimental', 'Commercial']
 
  query = """
    SELECT 
      title.id as id,
      title.production_year as year,
      runtime.info as runtime,
      genre.info as genre
    FROM 
      title,
      movie_info as runtime,
      movie_info as genre
    WHERE 
      title.kind_id in (1,3,4) AND 
      runtime.movie_id = title.id AND
      runtime.info_type_id = 1 AND
      genre.movie_id = title.id AND
      genre.info_type_id = 3 AND
      genre.info != '_//bbfc.co.uk/releases/import-export-2008-0_' AND
      title.id NOT IN (SELECT movie_id FROM movie_info WHERE info_type_id = 3 AND info in ('Adult','Erotica','Reality-TV','News','Talk-Show','Game-Show'))
    ORDER by year ASC
  """


  def __init__(self):
    '''
    Constructor
    '''
    self.runtimeDictionary = {}
    self.genreDictionary   = {}
    
    self.statList = []
    for genre in self.genres:
      self.statList.append(genre+'-length')
      self.statList.append(genre)
      self.genreDictionary[genre] = set()
      
    super(GenreSumQuery,self).__init__()
    
    
  def addRow(self, row):
    movie_id = row['id']
    length   = row['runtime']
    genre    = row['genre']
    runtime = self.convertRuntime(length)
    
    if(self.checkMovieRuntime(movie_id, runtime, length)):
      self.addLargerEntryToDict( self.runtimeDictionary, movie_id, runtime)
      self.genreDictionary[genre].add(movie_id)
    return

  
  def tally(self, resultDict):
    for genre in self.genres:
      for movie_id in self.genreDictionary[genre]:
        runtime = self.runtimeDictionary[movie_id]
        resultDict[genre] += 1
        resultDict[genre+'-length'] += runtime
      self.genreDictionary[genre].clear()
    
    ''''Clear data'''
    self.runtimeDictionary.clear() 
    return resultDict

class FeatureFilmGenreSumQuery(GenreSumQuery):
  '''
  Just the number movies 45 - 300 minutes per genre
  '''
  dataFileName  = "genres.features.sum.dat"
  errorFileName = 'errors.genres.feature.sum.txt'

  def checkMovieRuntime(self, movie_id, runtime, originalRuntime):
    if runtime >= 40:
      if runtime < 300:
        return True
      self.debugMessage("- Movie " + str(movie_id) + " has a runtime of " + str(runtime) + " ( " + str(originalRuntime) + " ) ")
    return False


