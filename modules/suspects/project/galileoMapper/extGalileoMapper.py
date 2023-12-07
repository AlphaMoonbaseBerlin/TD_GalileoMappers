


'''Info Header Start
Name : extGalileoMapper
Author : Wieland@AMB-ZEPH15
Saveorigin : Project.toe
Saveversion : 2022.32660
Info Header End'''

from functools import cached_property

class extGalileoMapper:
	"""
	extMidiMapper description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.menuitems = ['StrMenu', 'Menu']
		self.ownerComp = ownerComp

	@property
	def mappingTable(self):
		return self.ownerComp.op("repo_maker").Repo

	def ClearTable(self):
		self.mappingTable.clear(keepFirstRow=True)
		self.ResetMapping()
	
	def AddParameter(self, parameter, channel = 'Learn', index = 'Learn'):
		if parameter.style not in self.menuitems:
			rangemin = parameter.normMin
			rangemax = parameter.normMax
		else:
			rangemin = 0
			rangemax = len(parameter.menuNames) - 1
		
		op = parameter.owner.path
		name = parameter.name
		self.mappingTable.appendRow([channel, op, name, rangemin, rangemax])
		
	def AdjustValue(self, row, col, val):
		self.mappingTable[row, col].val = val
		return
		
	def SetLearn(self, row):
		self.mappingTable[row, 'chan'] = 'Learn'
		
	def Delete(self, row):
		self.mappingTable.deleteRow(row)
	
	def ResetMapping(self):
		try:
			del self.Mapping
		except AttributeError:
			pass


	@cached_property
	def Mapping(self):
		mapping = {}
		for row in self.mappingTable.rows():
			if row[0].val == "Learn" 	: continue
			
			operator = op(row[1])
			if operator is None	: continue
			par = getattr(operator.par,row[2].val)
			if par is None: continue
			channel = row[0].val
			
			if channel not in mapping : mapping[channel] = []
	
			mapData = {	'par'	:	par,
						'min'	:	row[3].val,
						'max'	:	row[4].val,
						'channel':	channel	}
			
			mapping[channel].append(mapData)
		return mapping
			
	def ApplyMapping(self, channel, value):
		if channel in self.Mapping:
			for mapData in self.Mapping[channel]:
				newValue = tdu.remap(value[0], 0.0, 1.0, mapData['min'], mapData['max'])
				if mapData['par'].style in self.menuitems:
					mapData['par'].menuIndex = newValue
					return
				mapData['par'].val = newValue
	
	def Learn(self, channel):
		if self.ownerComp.par.Learn:
			learnRows = self.mappingTable.rows("Learn")
			for r in learnRows:
				rowIndex = r[0].row
				self.mappingTable[rowIndex, 'chan'] = channel
				