import openmol

pointers = [
	'NATOM', 	'NTYPES', 'NBONH',  'MBONA',  'NTHETH', 'MTHETA',
	'NPHIH',    'MPHIA',  'NHPARM', 'NPARM',  'NNB',    'NRES',
	'NBONA',    'NTHETA', 'NPHIA',  'NUMBND', 'NUMANG', 'NPTRA',
	'NATYP',    'NPHB',   'IFPERT', 'NBPER',  'NGPER',  'NDPER',
	'MBPER',    'MGPER',  'MDPER',  'IFBOX',  'NMXRS',  'IFCAP',
	'NUMEXTRA', 'NCOPY'
]

def initialize():
	MOL = openmol.initialize()
	MOL['source_format'] = "AMBER PARM7"

	MOL['parm_version_string'] = None
	MOL['atom_type_index'] = []
	MOL['atom_no_excluded'] = []

	# FF parameters
	MOL['FF_bond_k'] = []
	MOL['FF_bond_eq'] = []
	MOL['bond_ff_index'] = []

	MOL['FF_angle_k'] = []
	MOL['FF_angle_eq'] = []
	MOL['angle_ff_index'] = []

	MOL['FF_dihed_k'] = []
	MOL['FF_dihed_phase'] = []
	MOL['FF_dihed_periodicity'] = []
	MOL['dihed_ff_index'] = []

	MOL['FF_lj_acoeff'] = []
	MOL['FF_lj_bcoeff'] = []
	MOL['FF_lj_parm_index'] = []

	for i in pointers:
		MOL['PARM_%s' %i] = 0

	return MOL

def process_last_section(MOL, section, lines, format):
	items = []
	for l in lines:
		items += l.split()

	if not section:
		return True

	if section == 'TITLE':
		MOL['title'] = lines[0]

	elif section == 'POINTERS':
		if len(items) > len(pointers):
			print('\nWarning: unknown PRMTOP pointer found. Ignoring ...', end=' ')

		for i, v in enumerate(items):
			if i < len(pointers):
				MOL['PARM_%s' %pointers[i]] = int(v)

		MOL['no_atoms'] = MOL['PARM_NATOM']
		MOL['no_bonds'] = MOL['PARM_NBONA'] + MOL['PARM_NBONH']
		MOL['no_angles'] = MOL['PARM_NTHETH'] + MOL['PARM_MTHETA']
		MOL['no_diheds'] = MOL['PARM_NPHIH'] + MOL['PARM_MPHIA']
		MOL['no_residues'] = MOL['PARM_NRES']
		MOL['no_atom_types'] = MOL['PARM_NATYP']

	elif section == 'ATOM_NAME':
		if len(items) != MOL['no_atoms']:
			print('Error: no_atoms and ATOM_NAME section mismatch')
			return False

		for name in items:
			MOL['atom_name'].append(name)

	elif section == 'CHARGE':
		if len(items) != MOL['no_atoms']:
			print('Error: no_atoms and CHARGE section mismatch')
			return False

		for q in items:
			# in electionic units
			MOL['atom_q'].append(float(q)/18.2223)

	elif section == 'ATOMIC_NUMBER':
		if len(items) != MOL['no_atoms']:
			print('Error: no_atoms and ATOMIC_NUMBER section mismatch')
			return False

		for A in items:
			MOL['atom_atomic_no'].append(int(A))

	elif section == 'MASS':
		if len(items) != MOL['no_atoms']:
			print('Error: no_atoms and MASS section mismatch')
			return False

		for m in items:
			MOL['atom_mass'].append(float(m))

	elif section == 'ATOM_TYPE_INDEX':
		if len(items) != MOL['no_atoms']:
			print('Error: no_atoms and ATOM_TYPE_INDEX section mismatch')
			return False

		for t in items:
			MOL['atom_type_index'].append(int(t) - 1)

	elif section == 'NUMBER_EXCLUDED_ATOMS':
		if len(items) != MOL['no_atoms']:
			print('Error: no_atoms and NUMBER_EXCLUDED_ATOMS section mismatch')
			return False

		for ex in items:
			MOL['atom_no_excluded'].append(int(ex))

	# lj parm index, needed to find epsilon, sigma
	elif section == 'NONBONDED_PARM_INDEX':
		if len(items) != MOL['no_atom_types']**2:
			print('Error: no_atom_types and NONBONDED_PARM_INDEX section mismatch')
			return False

		for ix in items:
			MOL['FF_lj_parm_index'].append(int(ix))

	elif section == 'RESIDUE_LABEL':
		if len(items) != MOL['no_residues']:
			print('Error: no_residues and RESIDUE_LABEL section mismatch')
			return False

		for i in items:
			MOL['residue_name'].append(i)

	elif section == 'RESIDUE_POINTER':
		if len(items) != MOL['no_residues']:
			print('Error: no_residues and RESIDUE_POINTER section mismatch')
			return False

		for i in items:
			MOL['residue_start'].append(int(i) - 1)

	elif section in ['BONDS_INC_HYDROGEN', 'BONDS_WITHOUT_HYDROGEN']:
		for i in range(0, len(items), 3):
			index0 = int(abs(int(items[i]))/3)
			index1 = int(abs(int(items[i+1]))/3)
			index2 = int(items[i+2]) - 1
			MOL['bond_from'].append(index0)
			MOL['bond_to'].append(index1)
			MOL['bond_ff_index'].append(index2)

	elif section in ['ANGLES_INC_HYDROGEN', 'ANGLES_WITHOUT_HYDROGEN']:
		for i in range(0, len(items), 4):
			index0 = int(abs(int(items[i]))/3)
			index1 = int(abs(int(items[i+1]))/3)
			index2 = int(abs(int(items[i+2]))/3)
			index3 = int(items[i+3]) - 1
			MOL['angle_a'].append(index0)
			MOL['angle_b'].append(index1)
			MOL['angle_c'].append(index2)
			MOL['angle_ff_index'].append(index3)

	elif section in ['DIHEDRALS_INC_HYDROGEN', 'DIHEDRALS_WITHOUT_HYDROGEN']:
		for i in range(0, len(items), 5):
			index0 = int(abs(int(items[i]))/3)
			index1 = int(abs(int(items[i+1]))/3)
			index2 = int(abs(int(items[i+2]))/3)
			index3 = int(abs(int(items[i+3]))/3)
			index4 = int(items[i+4]) - 1
			MOL['dihed_a'].append(index0)
			MOL['dihed_b'].append(index1)
			MOL['dihed_c'].append(index2)
			MOL['dihed_d'].append(index3)
			MOL['dihed_ff_index'].append(index4)

	elif section == 'AMBER_ATOM_TYPE':
		if len(items) != MOL['no_atoms']:
			print('Error: no_atoms and AMBER_ATOM_TYPE section mismatch')
			return False

		for t in items:
			MOL['atom_type'].append(t)
			if t not in MOL['unique_atom_types']:
				MOL['unique_atom_types'].append(t)

	elif section == 'BOND_FORCE_CONSTANT':
		for i in items:
			MOL['FF_bond_k'].append(float(i))

	elif section == 'BOND_EQUIL_VALUE':
		for i in items:
			MOL['FF_bond_eq'].append(float(i))

	elif section == 'ANGLE_FORCE_CONSTANT':
		for i in items:
			MOL['FF_angle_k'].append(float(i))

	elif section == 'ANGLE_EQUIL_VALUE':
		for i in items:
			MOL['FF_angle_eq'].append(float(i))

	elif section == 'DIHEDRAL_FORCE_CONSTANT':
		for i in items:
			MOL['FF_dihed_k'].append(float(i))

	elif section == 'DIHEDRAL_PERIODICITY':
		for i in items:
			MOL['FF_dihed_periodicity'].append(float(i))

	elif section == 'DIHEDRAL_PHASE':
		for i in items:
			MOL['FF_dihed_phase'].append(float(i))

	elif section == 'LENNARD_JONES_ACOEF':
		for i in items:
			MOL['FF_lj_acoeff'].append(float(i))

	elif section == 'LENNARD_JONES_BCOEF':
		for i in items:
			MOL['FF_lj_bcoeff'].append(float(i))


	print('OK.')
	return True

def read_prmtop(prmtop):
	global section_lines

	MOL = initialize()

	line_no = 0
	section_line_no = 0
	section = None
	section_format = None
	section_lines = []

	for line in open(prmtop, 'r'):
		line_no += 1
		section_line_no += 1

		line = line.strip()

		if len(line) == 0:
			continue

		if line.startswith('%VERSION'):
			parts = line.split()
			if len(parts) < 2:
				print('Invalid PRMTOP [line %d]:\n%s' %(line_no, line))
				return None
			else:
				MOL['parm_version_string'] = ' '.join(parts[1:])

		# new section
		elif line.startswith('%FLAG'):
			parts = line.split()
			if len(parts) < 2:
				print('Invalid PRMTOP [line %d]:\n%s' %(line_no, line))
				return None
			else:
				if not process_last_section(MOL, section, section_lines, section_format):
					return False

				section = parts[1]
				print('Reading %s ...' %section, end=' ')
				section_line_no = 0
				section_lines = []

		elif line.startswith('%FORMAT'):
			parts = line.split('(')
			if len(parts) < 2:
				print('Invalid PRMTOP [line %d]:\n%s' %(line_no, line))
				return None
			else:
				section_format = parts[1][:-1]

		else:
			section_lines.append(line)

	if not process_last_section(MOL, section, section_lines, section_format):
		return False

	print('Done.')
	return MOL

def read_rst7(MOL, rst_file):
	line_no = 0
	no_atoms = 0
	items = []
	last_line = None

	for line in open(rst_file, 'r'):
		line_no += 1
		line = line.strip()

		if len(line) == 0:
			continue

		last_line = line

		if line_no == 1:
			rst_title = line
			continue
		elif line_no == 2:
			parts = line.split()
			no_atoms = int(parts[0])
			if len(parts) > 1:
				MOL['time'] = float(parts[1])
			if len(parts) > 2:
				MOL['temp'] = float(parts[2])

			if no_atoms != MOL['no_atoms']:
				print('Error: RST7 no_atoms mismatch.')
				return False
		else:
			items += line.split()

	if len(items) < no_atoms * 3:
		print('Error: RST7 no_atoms, coordinate items mismatch.')
		return False

	print('Reading coordinates ...', end=' ')

	for i in range(0, no_atoms*3, 3):
		MOL['atom_x'].append(float(items[i]))
		MOL['atom_y'].append(float(items[i+1]))
		MOL['atom_z'].append(float(items[i+2]))

	print('OK.')

	if len(items) >= no_atoms*6:
		print('Reading velocities ...', end=' ')

		for i in range(no_atoms*3, no_atoms*6, 3):
			MOL['atom_vx'].append(float(items[i]))
			MOL['atom_vy'].append(float(items[i+1]))
			MOL['atom_vz'].append(float(items[i+2]))

		print('OK.')

	box_size_conditions = [
		len(items) == no_atoms*3 + 3,
		len(items) == no_atoms*6 + 3,
		len(items) == no_atoms*3 + 6,
		len(items) == no_atoms*6 + 6,
	]

	if any(box_size_conditions):
		print('Reading box dimension ...', end=' ')
		parts = last_line.split()
		MOL['box_x'] = float(parts[0])
		MOL['box_y'] = float(parts[1])
		MOL['box_z'] = float(parts[2])

		print('OK.')
	else:
		print('No PBC box information found.')

	box_angle_conditions = [
		len(items) == no_atoms*3 + 6,
		len(items) == no_atoms*6 + 6,
	]

	if any(box_angle_conditions):
		print('Reading box angles ...', end=' ')
		parts = last_line.split()
		MOL['box_alpha'] = float(parts[3])
		MOL['box_beta'] = float(parts[4])
		MOL['box_gamma'] = float(parts[5])

		print('OK.')

	print('Done.')
	return MOL

def read(prmtop, rst7):
	MOL = read_prmtop(prmtop)
	if not MOL:
		return False
	
	MOL = read_rst7(MOL, rst7)
	if not openmol.check(MOL):
		return False

	return MOL