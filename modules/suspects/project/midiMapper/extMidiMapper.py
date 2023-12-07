
'''Info Header Start
Name : extMidiMapper
Author : Wieland@AMB-ZEPH15
Saveorigin : Project.toe
Saveversion : 2022.32660
Info Header End'''
"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class extMidiMapper:
	"""
	extMidiMapper description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.menuitems = ['StrMenu', 'Menu']
		self.ownerComp = ownerComp
		#self.mappingTable = self.ownerComp.op('midiMap')
		self.Mapping = {}
		self.FillMapping()

	@property
	def mappingTable(self):
		return self.ownerComp.op("repo_maker").Repo
	
	def ClearTable(self):
		self.mappingTable.clear(keepFirstRow=True)
		self.ClearMapping()
	
	def ClearMapping(self):
		self.Mapping = {}
	
	def AddParameter(self, parameter, channel = 'Learn', index = 'Learn'):
		if parameter.style not in self.menuitems:
			rangemin = parameter.normMin
			rangemax = parameter.normMax
		else:
			rangemin = 0
			rangemax = len(parameter.menuNames) - 1
		
		op = parameter.owner.path
		name = parameter.name
		self.mappingTable.appendRow([channel, index, op, name, rangemin, rangemax])
		
	def AdjustValue(self, row, col, val):
		self.mappingTable[row, col].val = val
		return
		
	def SetLearn(self, row):
		self.mappingTable[row, 'chan'] = 'Learn'
		self.mappingTable[row, 'index'] = 'Learn'
		
	def Delete(self, row):
		self.mappingTable.deleteRow(row)
	
	def FillMapping(self):
		self.ClearMapping()
		rows = self.mappingTable.rows()
		for r in rows:
			if r[0].val == "Learn" 	: continue
			
			operator = op(r[2])
			if operator is None	: continue
			par = getattr(operator.par,r[3].val)
			if par is None: continue
			channel = int(r[0].val)
			index = int(r[1].val)
			if channel not in self.Mapping : self.Mapping[channel] = {}
			if index not in self.Mapping[channel] : self.Mapping[channel][index] = []
			mapData = {	'par'	:	par,
						'min'	:	r[4].val,
						'max'	:	r[5].val,	}
						
			self.Mapping[channel][index].append(mapData)
			
		
			
	def ApplyMapping(self, channel, index, value):
		if channel in self.Mapping:
			if index in self.Mapping[channel]:
				for mapData in self.Mapping[channel][index]:
					newValue = tdu.remap(value, 0, 127, mapData['min'], mapData['max'])
					if mapData['par'].style in self.menuitems:
						mapData['par'].menuIndex = newValue
						return
					mapData['par'].val = newValue
	def Learn(self, channel, index):
		if self.ownerComp.par.Learn:
			learnRows = self.mappingTable.rows("Learn")
			for r in learnRows:
				rowIndex = r[0].row
				self.mappingTable[rowIndex, 'chan'] = channel
				self.mappingTable[rowIndex, 'index'] = index