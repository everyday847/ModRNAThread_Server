import time
import subprocess
import os
import zipfile
import rna_design.email_client



def run_thread(nstruct, sequence, fmt, mutation_list, insertion_list, email):
   
    args = [ '/Users/amw579/Rosetta/main/source/bin/rna_thread_and_minimize.macosclangrelease' ]
        
    print args
    #args.extend( ( '-s', 'data/cb5b40cb322d6ba00a9ddb3c0934b46b/rna.pdb', '-nstruct', str(nstruct), '-score:weights', 'rna_minimize' ) )
    args.extend( ( '-s', 'rna.pdb', '-nstruct', str(nstruct), '-score:weights', 'rna_minimize' ) )
        
    print args
    if len( sequence ) > 0:
        args.append( '-seq' )
        args.append( sequence )
        
    print args
    if fmt != "DEFAULT":
        args.append( '-input_sequence_type' )
        args.append( fmt )
    
    print args
    if len( mutation_list ) > 0:
        args.append( '-mutation_list' )
        args.append( mutation_list )

    print args
    if len( insertion_list ) > 0:
        args.append( '-insertion_list' )
        args.append( insertion_list )
    
    print args

    f = open( "out.txt", "w" )
    subprocess.call( args ), stdout=f )
  
run_thread( 10, "", "DEFAULT", "19,c", "34,gau", "" )
