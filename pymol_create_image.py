import sys
argv = sys.argv#[sys.argv.index('--') + 1:]
print argv
from pymol import cmd
pdb = argv[0]
cmd.load(pdb)
cmd.do('rr()')
cmd.orient()
#cmd.set('antialias', 2)
#cmd.viewport(320, 240)
cmd.ray(320, 240 )
cmd.png('test.png')
