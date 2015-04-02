'''
Created on 10.08.2014

@author: Philip Peter <philip.peter@justgeek.de>

As long as you retain this notice you can do whatever you want with this stuff.
If we meet some day, and you think this stuff is worth it, you can buy me a
beer in return

Philip Peter
'''

class IMDbQuery(object):
  '''
  A generic class for IMDb queries
  Actual queries need to be derieved from this
  '''
  outputDir     = "..\\data\\"
  dataFileName  = "generic.dat"
  errorFileName = 'errors.txt'
  debugEnabled  = False
  statList      = []
  query = """
    SELECT 
      title.id as id,
      title.production_year as year,
    FROM 
      title
    WHERE 
      title.kind_id in (1,3,4) AND 
      title.id NOT IN (SELECT movie_id FROM movie_info WHERE info_type_id = 3 AND info in ('Adult','Erotica','Reality-TV','News','Talk-Show','Game-Show'))
    ORDER by year ASC
  """

  def __init__(self):
    '''
    All common stuff
    '''
    self.conversionErrors = 0


  def writeDataHeader(self):
    '''
    Lists the stat names in order at the beginning of the data file
    '''
    self.dataFile.write('# year')
    for entry in self.statList:
      self.dataFile.write(', ' + entry)
    self.dataFile.write("\n\n")
    self.dataFile.flush()
    
  def debugMessage(self, debugMessage):
    '''
    Small wrapper to output debug messages
    '''
    if self.debugEnabled:
      self.errorFile.write(debugMessage)
      self.errorFile.write("\n")
      self.errorFile.flush()
  
  def addLargerEntryToDict(self, dictionary, movie_id, runtime):
    if movie_id in dictionary:
      if dictionary[movie_id] < runtime:
        dictionary[movie_id] = runtime
    else:
      dictionary[movie_id] = runtime
        
  def convertRuntime(self, runtime):
    '''
    Parse most runtime formats
    '''
    originalTime = runtime
    runtime.strip()
    if runtime[0].isalpha():
      # most likely first is name like USA:length
      runtime = runtime.split(':', 1)
      runtime = runtime[1]
    runtime = runtime.replace(':', '.')
    runtime = runtime.replace(',', '.')
    runtime = runtime.replace("'", '.')
    runtime = runtime.replace('"', '')
    try:
      result = float(runtime)
      return result
    except ValueError:
      #Not a valid int
      result = 0
    self.conversionErrors += 1
    self.debugMessage("! Runtime conversion error: " + str(originalTime) + "\t->\t" + str(runtime))
    return 0
  
  def checkMovieRuntime(self, movie_id, runtime, originalRuntime):
    if runtime > 0:
      if runtime < 1200:
        return True
      self.debugMessage("- Movie " + str(movie_id) + " has a runtime of " + str(runtime) + " ( " + str(originalRuntime) + " ) ")
    return False
  
  def endOfYear(self, year):
    '''
    Called once per year, write data to file
    '''
    results = {}
    year = int(year)
    for entry in self.statList:
      results[entry] = 0
    
    results = self.tally(results)
    if year >= 2014 or year == '0':
      ''''Skip years after 2013, incomplete data'''
      return
    
    self.dataFile.write(str(year))
    
    for entry in self.statList:
      self.dataFile.write("\t" + str(round(results[entry], 2)))
    self.dataFile.write("\n")
    self.dataFile.flush()
    
    if (year % 10) == 0:
      print "\nProcessed year " + str(year),
    else:
      print '.',
      
  def startQuery(self, cursor):
    '''
    Main query, does everything
    '''
    lastYear = '0'
    self.dataFile = open(self.outputDir + self.dataFileName, 'w')
    if(self.debugEnabled):
      self.errorFile = open(self.outputDir + self.errorFileName, 'w')
    self.writeDataHeader()
    
    cursor.execute(self.query)
    print "\tQuery executed"
    
    row = cursor.fetchone()
    while row is not None:
      year = row['year']

      if (year == None) or (year == 'None'):
        year = '0';
      year = str(year)
      
      if year != '0':
        if(year != lastYear):
          self.endOfYear(lastYear);
          lastYear = year
        self.addRow(row)
              
      row = cursor.fetchone()
    self.closeFiles()
    
  def closeFiles(self):
    self.dataFile.close()
    if(self.debugEnabled):
      self.errorFile.close()

  def addRow(self, row):
    '''
    Needs to be implemented in subclass
    Process one individual row
    '''
    

  def tally(self, resultDict):
    '''
    Needs to be implemented in subclass
    Called at the end of each year, returns dict with all stats
    '''
    return resultDict

class GenericSumQuery(IMDbQuery):
  '''
  Outputs just a sum add the end of everything
  '''
  
  def __init__(self):
    '''
    Constructor
    '''
    super(GenericSumQuery,self).__init__()
    self.results = {}
    for entry in self.statList:
      self.results[entry] = 0
  
  def writeDataHeader(self):
    '''
    Not necessary
    '''

  def endOfYear(self, year):
    '''
    Called once per year, doesn't do much
    '''
    self.results = self.tally(self.results)
    if year >= 2014 or year == '0':
      ''''Skip years after 2013, incomplete data'''
      return
    
    if (year % 10) == 0:
      print "\nProcessed year " + str(year),
    else:
      print '.',
      
  def writeResults(self, results):
    for entry in self.statList:
      self.dataFile.write(str(entry) + "\t" + str(round(results[entry], 2)))
      self.dataFile.write("\n")
    self.dataFile.flush()
    
  
  def startQuery(self, cursor):
    '''
    Main query, does everything
    '''
    lastYear = '0'
    self.dataFile = open(self.outputDir + self.dataFileName, 'w')
    if(self.debugEnabled):
      self.errorFile = open(self.outputDir + self.errorFileName, 'w')
    self.writeDataHeader()
    
    cursor.execute(self.query)
    print "\tQuery executed"
    
    row = cursor.fetchone()
    while row is not None:
      year = row['year']

      if (year == None) or (year == 'None'):
        year = '0';
      year = str(year)
      
      if year != '0':
        if(year != lastYear):
          self.endOfYear(lastYear);
          lastYear = year
        self.addRow(row)
                
      row = cursor.fetchone()
    self.writeResults(self.results)
    self.closeFiles()