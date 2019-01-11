import types

class TsvRecord(object):
	__slots__ = ('__keys', '__vals')

	def __init__(self, vals = None, keys = None):
		"""
		r = TsvRecord([1,2,3,4,5])
		r.__vals == [1,2,3,4,5]
		r.__keys == None
		"""
		self.__vals = vals or []
		if keys:
			assert len(keys) == len(vals)
			self.__keys = dict(zip(keys, range(len(keys))))
		else:
			self.__keys = None
	
	def attachKeys(self, keys):
		assert len(keys) == len(self.__vals)
		self.__keys = dict(zip(keys, range(len(keys))))

	def keys(self):
		if not self.__keys:
			return range(len(self.__vals))
		return sorted(self.__keys, key=self.__keys.get)
	
	def values(self):
		return self.__vals

	def items(self):
		if not self.__keys:
			return enumerate(self.__vals)
		return zip(list(self.keys()), list(self.__vals))
	
	def __repr__(self):
		return '<TsvRecord: {!r}>'.format(dict(self.items()))

	def __getitem__(self, key):
		if isinstance(key, (slice, int)):
			return self.__vals[key]
		
		if key in self.__keys:
			return self.__vals[self.__keys[key]]

		raise KeyError("Record contains no '{}' field.".format(key))

	def __getattr__(self, key):
		if str(key).startswith('__') or str(key).startswith('_TsvRecord'):
			return super(TsvRecord, self).__getattr__(key)
		return self[key]

	def __setitem__(self, key, value):
		if isinstance(key, int):
			if key > len(self) or key < 0:
				raise IndexError('Index out of range: {}'.format(key))
		elif self.__keys and key in self.__keys:
			self.__vals[self.__keys[key]] = value
		else:
			self.__keys = self.__keys or {}
			self.__keys[key] = len(self)
			self.__vals.append(value)
	
	def __len__(self):
		return len(self.__vals)

	def __setattr__(self, key, value):
		if str(key).startswith('__') or str(key).startswith('_TsvRecord'):
			super(TsvRecord, self).__setattr__(key, value)
		else:
		  self[key] = value

	def get(self, key, default=None):
		"""Returns the value for a given key, or default."""
		try:
			return self[key]
		except KeyError:
			return default

	def __eq__(self, other):
		return self.keys() == other.keys() and self.values() == other.values()

	def __ne__(self, other):
		return not self.__eq__(other)

	def asDict(self, ordered=False):
		"""Returns the row as a dictionary, as ordered."""
		return OrderedDict(self.items()) if ordered else dict(items.items())

	def __contains__(self, key):
		return self.__keys and key in self.__keys

	def __delitem__(self, key):
		if not self.__keys:
			del self.__vals[key]
		elif key in self.__keys:
			del self.__vals[self.__keys[key]]
			del self.__keys[key]
		else:
			del self.__keys[list(self.keys())[key]]
			del self.__vals[key]

class TsvReader(object):

	def __init__(self, 
		infile, 
		delimit = '\t',
		comment = '#',
		skip    = 0,
		cnames  = True, # "False": no head; "None"/"True": split first line with delimit, "Callback": get head for first line in your way
		attach  = True,
		row     = None, # row factory
		cname0  = "ROWNAME"):
		openfunc = open
		if infile.endswith('.gz'):
			import gzip
			openfunc = gzip.open

		self.file    = openfunc(infile)
		self.delimit = delimit
		self.comment = comment
		self.attach  = attach
		self.row     = row
		self.tell    = 0

		if skip > 0:
			for _ in range(skip):
				self.file.readline()

		while True:
			tell = self.file.tell()
			line = self.file.readline()
			if comment and line.startswith(comment):
				continue
			self.file.seek(tell)
			break
		
		headline = self.file.readline() if cnames is not False else ''
		if callable(cnames):
			self.cnames = cnames(headline)
		elif headline:
			if comment and headline.startswith(comment):
				headline = headline[1:].lstrip()
			self.cnames = headline.rstrip('\n').split(delimit)
		else:
			self.cnames = []
		# try to add "cname0" as column name 
		tell  = self.file.tell()
		firstline = self.file.readline().rstrip('\n')
		ncols = len(firstline.split(delimit))

		if firstline and self.cnames and len(self.cnames) == ncols - 1:
			self.cnames.insert(0, cname0)
		if firstline and self.cnames and len(self.cnames) != ncols:
			raise ValueError('Not a valid tsv file. Head has %s columns, while first line has %s.' % (len(self.cnames), ncols))
		
		self.file.seek(tell)
		self.tell = tell

	def next(self):
		line = self.file.readline()
		line = line.rstrip('\n')
		# empty lines not allowed
		if not line: raise StopIteration()
		record = TsvRecord(line.split(self.delimit))
		if self.attach and self.cnames:
			record.attachKeys(self.cnames)
		if callable(self.row):
			return self.row(record)
		return record

	def dump(self, col = None):
		if not col:
			return list(self)
		if not isinstance(col, list):
			return [r[col] for r in self]
		return [tuple(r[c] for c in col) for r in self]

	def __next__(self):
		return self.next()

	def rewind(self):
		self.file.seek(self.tell)

	def __iter__(self):
		return self

	def __del__(self):
		self.close()

	def close(self):
		if self.file:
			self.file.close()

class TsvWriter(object):
	def __init__(self, outfile, delimit = '\t', append = False):
		openfunc = open
		if outfile.endswith('.gz'):
			import gzip
			openfunc = gzip.open

		self.delimit = delimit
		self.cnames    = []
		self.file    = openfunc(outfile, 'w' if not append else 'a')

	def writeHead(self, callback = True):
		if not self.cnames:
			return
		if callback and callable(callback):
			head = callback(self.cnames)
			self.file.write(head + "\n")
		elif callback:
			head = self.delimit.join(self.cnames)
			self.file.write(head + "\n")

	def write(self, record):
		if isinstance(record, list) or isinstance(record, types.GeneratorType):
			self.file.write(self.delimit.join(str(v) for v in record) + '\n')
		elif isinstance(record, TsvRecord):
			if not self.cnames:
				self.write(record.values())
			else:
				self.write(record[n] for n in self.cnames)
		else:
			self.file.write(str(record))

	def __del__(self):
		self.close()

	def close(self):
		if self.file:
			self.file.close()

class TsvJoin(object):

	@staticmethod
	def compare(a, b, reverse = False):
		if not reverse:
			return 0 if a < b else 1 if a > b else -1
		else:
			return 0 if a > b else 1 if a < b else -1
	
	def __init__(self, *files, **inopts):
		inopts_default = dict(
			delimit = '\t',
			comment = '#',
			skip    = 0,
			cnames  = True,
			attach  = False,
			row     = None,
			cname0  = "ROWNAME"
		)
		inopts_multi = {}
		self.length = len(files)
		for key, val in inopts.items():
			if not isinstance(val, list):
				inopts_multi[key] = [val] * self.length
			elif len(val) < self.length:
				inopts_multi[key] = val + [inopts_default[key]] * (self.length - len(val))
			else:
				inopts_multi[key] = val
		inopts = []
		for i in range(self.length):
			inopts.append({k:v[i] for k,v in inopts_multi.items()})

		self.readers = [TsvReader(f, **inopts[i]) for i,f in enumerate(files)]

	def _defaultMatch(self, *rows):
		data = [row[0] for row in rows]
		mind = min(data)
		return -1 if data.count(mind) == self.length else data.index(mind)

	def join(self, do, outfile, match = None, outopts = None):
		outopts = outopts or {}
		outopts_default = dict(
			delimit = "\t",
			append  = False
		)
		outopts_default.update(outopts)
		outopts = outopts_default

		cnames = False
		if 'cnames' in outopts:
			cnames = outopts['cnames']
			del outopts['cnames']
			
		out = TsvWriter(outfile, **outopts)
		out.cnames = sum((reader.cnames for reader in self.readers if reader.cnames), [])
		out.writeHead(cnames)

		match = match or self._defaultMatch
		rows = [None] * self.length
		while True:
			try:
				for i, row in enumerate(rows):
					rows[i] = row or next(self.readers[i])
				m = match(*rows)
				if m < 0: # matched
					do(out, *rows)
					m = 0
				rows[m] = None
			except StopIteration:
				break
			except Exception:
				from sys import stderr
				from traceback import format_exc
				info = format_exc().splitlines()
				info.append("With rows:")
				info.extend(["- {}".format(r) for r in rows])
				stderr.write("\n".join(info) + "\n\n")
				rows = [None] * self.length
				continue
		out.close()

