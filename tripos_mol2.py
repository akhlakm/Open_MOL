import openmol

def initialize():
	MOL = openmol.initialize()

	MOL['source_format'] = 'TRIPOS MOL2'

	MOL['atom_status_bit'] = []
	MOL['residue_dict_type'] = []
	MOL['residue_chain'] = []
	MOL['residue_sub_type'] = []
	MOL['residue_comment'] = []
	MOL['residue_inter_bonds'] = []

	return MOL

def check_last_section(section):
	if section == 'ATOM':
		if not openmol.check_atoms_ok(MOL):
			return False
		else:
			unique_atom_types = set(MOL['atom_type'])
			MOL['unique_atom_types'] = list(unique_atom_types)

	elif section == 'BOND':
		if not openmol.check_bonds_ok(MOL):
			return False

	elif section == 'SUBSTRUCTURE':
		if not openmol.check_residues_ok(MOL):
			return False

	print('OK.')
	return True


def read(mol2_file):
	MOL = initialize()

	line_no = 0
	section_line_no = 0
	section = None

	# variables for sanity checking
	type_ok = False
	charge_ok = False
	name_ok = False
	summary_ok = False


	for line in open(mol2_file, 'r'):

		line_no += 1
		section_line_no += 1

		line = line.strip()

		if len(line) == 0:
			continue

		# comments
		if line.startswith('#'):
			MOL['description'] += "%s\n" %line
			continue

		# new section definition
		if line.startswith('@<'):
			parts = line.split('>')

			if len(parts) < 2:
				print('Invalid MOL2 [line %d]:\n%s' %(line_no, line))
				return None
			else:
				if not check_last_section(section):
					return False

				section = parts[1]
				print('Reading %s ...' %section, end=' ')
				section_line_no = 0
				continue

		# handle sections
		if section == 'MOLECULE':
			if section_line_no == 1:
				MOL['title'] = line 
				name_ok = True

			elif section_line_no == 2:
				parts = line.split()
				if len(parts) > 0:
					MOL['no_atoms'] = int(parts[0])

				if len(parts) > 1:
					MOL['no_bonds'] = int(parts[1])

				if len(parts) > 2:
					MOL['no_residues'] = int(parts[2])

				if len(parts) > 3:
					MOL['no_features'] = int(parts[3])

				if len(parts) > 4:
					MOL['no_sets'] = int(parts[4])

				summary_ok = True

			elif section_line_no == 3:
				MOL['type'] = line 
				type_ok = True

			elif section_line_no == 4:
				MOL['charge_type'] = line
				charge_ok = True

			elif section_line_no == 5:
				MOL['mol2_status_bits'] = line

			elif section_line_no == 6:
				MOL['mol2_comment'] = line

		elif section == 'ATOM':
			parts = line.split()

			if len(parts) < 6:
				print('Invalid MOL2 [line %d]:\n%s' %(line_no, line))
				return None

			MOL['atom_name'].append(parts[1])
			MOL['atom_x'].append(float(parts[2]))
			MOL['atom_y'].append(float(parts[3]))
			MOL['atom_z'].append(float(parts[4]))
			MOL['atom_type'].append(parts[5])

			if len(parts) > 6:
				MOL['atom_resid'].append(int(parts[6]) - 1)

			if len(parts) > 7:
				MOL['atom_resname'].append(parts[7])

			if len(parts) > 8:
				MOL['atom_q'].append(float(parts[8]))

			if len(parts) > 9:
				MOL['atom_status_bit'].append(parts[9])


		elif section == 'BOND':
			parts = line.split()

			if len(parts) < 4:
				print('Invalid MOL2 [line %d]:\n%s' %(line_no, line))
				return None

			MOL['bond_from'].append(int(parts[1]) - 1)
			MOL['bond_to'].append(int(parts[2]) - 1)
			MOL['bond_type'].append(parts[3])

			if len(parts) > 4:
				MOL['bond_status_bit'].append(parts[4])

		elif section == 'SUBSTRUCTURE':
			parts = line.split()

			if len(parts) < 3:
				print('Invalid MOL2 [line %d]:\n%s' %(line_no, line))
				return None

			MOL['residue_name'].append(parts[1])
			MOL['residue_start'].append(int(parts[2]) - 1)

			if len(parts) > 3:
				MOL['residue_type'].append(parts[3])
			if len(parts) > 4:
				MOL['residue_dict_type'].append(parts[3])
			if len(parts) > 5:
				MOL['residue_chain'].append(parts[3])
			if len(parts) > 6:
				MOL['residue_sub_type'].append(parts[3])
			if len(parts) > 7:
				MOL['residue_inter_bonds'].append(parts[3])
			if len(parts) > 8:
				MOL['residue_status_bits'].append(parts[3])
			if len(parts) > 9:
				MOL['residue_comment'].append(parts[3])

		else:
			# unknown section
			# silence is golden
			pass

	if not check_last_section(section):
		return False

	print('Done.')
	return MOL

def write(MOL, mol2_file):
	fp = open(mol2_file, 'w+')
	fp.write('@<TRIPOS>MOLECULE\n')
	molecstr = 	"{title}\n" \
				"{no_atoms:>5d} {no_bonds:>5d} {no_residues:>5d}\n" \
				"{type}\n" \
				"{charge_type}\n\n"

	fp.write(molecstr.format(**MOL))

	fp.write('@<TRIPOS>ATOM\n')

	for i in range(MOL['no_atoms']):
		resid = MOL['atom_resid'][i]
		atom = {
			'id' : i + 1,
			'name': MOL['atom_name'][i],
			'x': MOL['atom_x'][i],
			'y': MOL['atom_y'][i],
			'z': MOL['atom_z'][i],
			'type': MOL['atom_type'][i],
			'resid': MOL['atom_resid'][i] + 1,
			'resname': MOL['residue_name'][resid],
			'charge': MOL['atom_q'][i]
		}
		atomstr =	"{id:>7d} {name:<5}  " \
					"{x:>7.4f}  {y:>7.4f}  {z:>7.4f}   {type:>3} " \
					"{resid:>3} {resname:<5}   {charge:>11.6f}\n"
		fp.write(atomstr.format(**atom))

	fp.write('@<TRIPOS>BOND\n')
	for i in range(MOL['no_bonds']):
		bond = {
			'id' : i + 1,
			'from': MOL['bond_from'][i] + 1,
			'to': MOL['bond_to'][i] + 1,
			'type': MOL['bond_type'][i],
		}
		bondstr =	"{id:>7d}  {from:>7d}  {to:>7d}   {type:>3} \n"
		fp.write(bondstr.format(**bond))

	fp.write('@<TRIPOS>SUBSTRUCTURE\n')
	for i in range(MOL['no_residues']):
		resid = MOL['atom_resid'][i]
		subst = {
			'id' : i + 1,
			'name': MOL['residue_name'][i],
			'root': MOL['residue_start'][i] + 1,
			'type': MOL['residue_type'][i],
		}
		resstr =	"{id:>7d}  {name:>7}  {root:>7d}   {type:>7} \n"
		fp.write(resstr.format(**subst))

	fp.close()
	print('%s written.' %mol2_file)


def build(MOL):

	if not MOL['type']:
		MOL['type'] = 'SMALL'

	if not MOL['charge_type']:
		MOL['charge_type'] = 'USER_CHARGES'

	if len(MOL['atom_resname']) == 0:
		for r, st in enumerate(MOL['residue_start']):
			res = MOL['residue_name'][r]

			end = MOL['no_atoms']
			if len(MOL['residue_start']) > r + 1:
				end = MOL['residue_start'][r+1]

			for i in range(st, end):
				MOL['atom_resid'].append(r)
				MOL['atom_resname'].append(res)

	if len(MOL['bond_type']) == 0:
		for i in range(MOL['no_bonds']):
			MOL['bond_type'].append("1")

	if len(MOL['residue_type']) == 0:
		for i in range(MOL['no_residues']):
			MOL['residue_type'].append("****")

	return MOL 
