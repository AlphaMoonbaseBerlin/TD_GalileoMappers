

'''Info Header Start
Name : extGalileoMapper
Author : Wieland@AMB-ZEPH15
Version : 0
Build : 4
Savetimestamp : 2023-07-21T22:41:30.796915
Saveorigin : Project.toe
Saveversion : 2022.28040
Info Header End'''


from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class extGalileoMapper:
	"""
	extMidiMapper description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.menuitems = ['StrMenu', 'Menu']
		self.ownerComp = ownerComp
		#self.mappingTable = self.ownerComp.self.mappingTable
		self.Mapping = {}
		self.ChannelMap = {}
		self.FillMapping()
		self.oscout = self.ownerComp.op('oscout')

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
		self.mappingTable.appendRow([channel, op, name, rangemin, rangemax])
		
	def AdjustValue(self, row, col, val):
		self.mappingTable[row, col].val = val
		return
		
	def SetLearn(self, row):
		self.mappingTable[row, 'chan'] = 'Learn'
		
	def Delete(self, row):
		self.mappingTable.deleteRow(row)
	
	def FillMapping(self):
		self.ClearMapping()
		rows = self.mappingTable.rows()
		for r in rows:
			if r[0].val == "Learn" 	: continue
			
			operator = op(r[1])
			if operator is None	: continue
			par = getattr(operator.par,r[2].val)
			if par is None: continue
			channel = r[0].val
			
			if channel not in self.Mapping : self.Mapping[channel] = []
			if par not in self.ChannelMap : self.ChannelMap[par] = []
	
			mapData = {	'par'	:	par,
						'min'	:	r[3].val,
						'max'	:	r[4].val,
						'channel':	channel	}
			
			self.Mapping[channel].append(mapData)
			self.ChannelMap[par].append(mapData)
		
			
	def ApplyMapping(self, channel, value):
		if channel in self.Mapping:
			for mapData in self.Mapping[channel]:
				newValue = tdu.remap(value[0], 0.0, 1.0, mapData['min'], mapData['max'])
				if mapData['par'].style in self.menuitems:
					mapData['par'].menuIndex = newValue
					return
				mapData['par'].val = newValue
				
	def ReturnMapping(self, parameter):
		if parameter in self.ChannelMap:
			for mapdata in self.ChannelMap[parameter]:
				newValue = tdu.remap(	parameter.menuIndex if parameter.style in self.menuitems else parameter.eval(), 
										mapdata['min'], 
										mapdata['max'], 0, 1)
				self.oscout.sendOSC( mapdata["channel"], [newValue] )
	
	def Learn(self, channel):
		if self.ownerComp.par.Learn:
			learnRows = self.mappingTable.rows("Learn")
			for r in learnRows:
				rowIndex = r[0].row
				self.mappingTable[rowIndex, 'chan'] = channel
				