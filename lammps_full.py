import math
import openmol

BOX_BUFFER = 1.0	# A

def initialize():
	MOL = openmol.initialize()
	MOL['source_format'] = "LAMMPS FULL"

	MOL['no_bond_types'] = 0
	MOL['no_angle_types'] = 0
	MOL['no_dihed_types'] = 0
	MOL['unique_atom_mass'] = []
	MOL['FF_bond_k'] = []
	MOL['FF_angle_k'] = []
	MOL['FF_dihed_k'] = []
	MOL['FF_lj_epsilon'] = []
	MOL['FF_lj_sigma'] = []
	return MOL 


def build(MOL):
	MOL = dict(initialize(), **MOL)

	# build residue id and name list
	if len(MOL['atom_resname']) == 0:
		for r, st in enumerate(MOL['residue_start']):
			res = MOL['residue_name'][r]

			end = MOL['no_atoms']
			if len(MOL['residue_start']) > r + 1:
				end = MOL['residue_start'][r+1]

			for i in range(st, end):
				MOL['atom_resid'].append(r)
				MOL['atom_resname'].append(res)

	# using parm7 data
	MOL['no_bond_types'] = len(MOL['FF_bond_k'])
	MOL['no_angle_types'] = len(MOL['FF_angle_k'])
	MOL['no_dihed_types'] = len(MOL['FF_dihed_k'])

	# if we have individual atom masses list, build type's masses
	if len(MOL['unique_atom_mass']) == 0 and len(MOL['atom_mass']):
		for unique_atom in MOL['unique_atom_types']:
			i = MOL['atom_type'].index(unique_atom)
			MOL['unique_atom_mass'].append(MOL['atom_mass'][i])

	if len(MOL['unique_atom_mass']) != MOL['no_atom_types']:
		print('LAMMPS Build Error: fail to build mass list, length mismatch.')

	# use PARM7: if we have A, B coeffs, build epsilon, sigma
	if len(MOL['FF_lj_acoeff']) and len(MOL['FF_lj_sigma']) != len(MOL['unique_atom_types']):
		if not MOL.get('FF_lj_parm_index', False):
			print('LAMMPS Build Error: non bonded parm indices not found.')

		else:
			for i in range(MOL['no_atom_types']):
				j = MOL['FF_lj_parm_index'][i * (MOL['no_atom_types'] + 1)] - 1

				A = MOL['FF_lj_acoeff'][j]
				B = MOL['FF_lj_bcoeff'][j]

				if A == 0.0:
					eps = 0.0
				else:
					eps = 0.25 * B**2 / A

				if B == 0.0:
					sigma = 0.0
				else:
					sigma = (A / B)**(1.0/6.0)

				MOL['FF_lj_epsilon'].append(eps)
				MOL['FF_lj_sigma'].append(sigma)

	if len(MOL['FF_lj_epsilon']) != MOL['no_atom_types'] or len(MOL['FF_lj_sigma']) != MOL['no_atom_types']:
		print('LAMMPS Build Error: fail to build pair coeffs, length mismatch.')

	MOL['_lammps_built'] = True
	return MOL 


def write(MOL, data_file):
	if not MOL.get('_lammps_built', False):
		print('Warning: MOL not getting build() for LAMMPS likely to fail while writing.')

	fp = open(data_file, 'w+')
	
	fp.write("%s\n\n" %MOL['title'])

	# counts
	fp.write("%d atoms\n" %MOL['no_atoms'])
	fp.write("%d bonds\n" %MOL['no_bonds'])
	fp.write("%d angles\n" %MOL['no_angles'])
	fp.write("%d diherdrals\n" %MOL['no_diheds'])
	fp.write("0 impropers\n\n")	# todo: fix it

	# types
	fp.write("%d atom types\n" %MOL['no_atom_types'])
	fp.write("%d bond types\n" %MOL['no_bond_types'])
	fp.write("%d angle types\n" %MOL['no_angle_types'])
	fp.write("%d dihedral types\n\n" %MOL['no_dihed_types'])

	# box info
	if MOL['box_x'] == 0.0:
		xlo = min(MOL['atom_x']) - BOX_BUFFER
		xhi = max(MOL['atom_x']) + BOX_BUFFER
	else:
		xlo = 0.0
		xhi = MOL['box_x']

	if MOL['box_y'] == 0.0:
		ylo = min(MOL['atom_y']) - BOX_BUFFER
		yhi = max(MOL['atom_y']) + BOX_BUFFER
	else:
		ylo = 0.0
		yhi = MOL['box_y']

	if MOL['box_z'] == 0.0:
		zlo = min(MOL['atom_z']) - BOX_BUFFER
		zhi = max(MOL['atom_z']) + BOX_BUFFER
	else:
		zlo = 0.0
		zhi = MOL['box_z']

	fp.write("%8.4f  %8.4f    xlo  xhi\n" %(xlo, xhi))
	fp.write("%8.4f  %8.4f    ylo  yhi\n" %(ylo, yhi))
	fp.write("%8.4f  %8.4f    zlo  zhi\n" %(zlo, zhi))

	# mass
	fp.write("\nMasses\n\n")
	for i in range(MOL['no_atom_types']):
		fp.write('%3d  %6.3f   # %s\n'
			%(i+1, MOL['unique_atom_mass'][i], MOL['unique_atom_types'][i]))

	# pair coeff
	fp.write("\nPair Coeffs\n\n")
	for i in range(MOL['no_atom_types']):
		fp.write('%3d  %10.4f   %10.4f   # %s\n'
			%(i+1, MOL['FF_lj_epsilon'][i], MOL['FF_lj_sigma'][i], MOL['unique_atom_types'][i]))

	# bond coeff
	fp.write("\nBond Coeffs\n\n")
	for i in range(MOL['no_bond_types']):
		fp.write('%3d  %6.3f   %6.3f\n'
			%(i+1, MOL['FF_bond_k'][i], MOL['FF_bond_eq'][i]))

	# angle coeff
	fp.write("\nAngle Coeffs\n\n")
	for i in range(MOL['no_angle_types']):
		fp.write('%3d  %6.3f  %6.3f\n'
			%(i+1, MOL['FF_angle_k'][i], math.degrees(MOL['FF_angle_eq'][i])))

	# dihed coeffs
	fp.write("\nDihedral Coeffs\n\n")
	for i in range(MOL['no_dihed_types']):
		fp.write('%3d  %6.3f  %d  %d\n'
			%(i+1, MOL['FF_dihed_k'][i], int(math.cos(MOL['FF_dihed_phase'][i])), int(MOL['FF_dihed_periodicity'][i])))

	# atoms
	fp.write("\nAtoms\n\n")

	for i in range(MOL['no_atoms']):
		resid = MOL['atom_resid'][i]
		atom = {
			'id' : i + 1,
			'name': MOL['atom_name'][i],
			'x': MOL['atom_x'][i],
			'y': MOL['atom_y'][i],
			'z': MOL['atom_z'][i],
			'type': MOL['atom_type_index'][i] + 1,
			'resid': MOL['atom_resid'][i] + 1,
			'charge': MOL['atom_q'][i]
		}

		atomstr =	"{id:>7d} {resid:>4d} {type:>3} {charge:>11.6f}  " \
					"{x:>7.4f}  {y:>7.4f}  {z:>7.4f} \n"

		fp.write(atomstr.format(**atom))

	# bonds
	fp.write("\nBonds\n\n")

	for i in range(MOL['no_bonds']):
		bond = {
			'id' : i + 1,
			'from': MOL['bond_from'][i] + 1,
			'to': MOL['bond_to'][i] + 1,
			'type': MOL['bond_ff_index'][i] + 1,
		}
		bondstr =	"{id:>7d}  {type:>5d}  {from:>7d}  {to:>7d} \n"
		fp.write(bondstr.format(**bond))

	# angles
	fp.write("\nAngles\n\n")

	for i in range(MOL['no_angles']):
		angle = {
			'id' : i + 1,
			'a': MOL['angle_a'][i] + 1,
			'b': MOL['angle_b'][i] + 1,
			'c': MOL['angle_c'][i] + 1,
			'type': MOL['angle_ff_index'][i] + 1,
		}
		anglestr =	"{id:>7d}  {type:>3d}  {a:>5d}  {b:>5d}  {c:>5d} \n"
		fp.write(anglestr.format(**angle))


	# diheds
	fp.write("\nDihedrals\n\n")

	for i in range(MOL['no_diheds']):
		dihed = {
			'id' : i + 1,
			'a': MOL['dihed_a'][i] + 1,
			'b': MOL['dihed_b'][i] + 1,
			'c': MOL['dihed_c'][i] + 1,
			'd': MOL['dihed_d'][i] + 1,
			'type': MOL['dihed_ff_index'][i] + 1,
		}
		dihedstr =	"{id:>7d}  {type:>3d}  {a:>5d}  {b:>5d}  {c:>5d}  {d:>5d} \n"
		fp.write(dihedstr.format(**dihed))


	fp.close()
	print('%s written.' %data_file)