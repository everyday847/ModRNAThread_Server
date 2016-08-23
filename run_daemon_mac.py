import time
import subprocess
import sys
import os
import zipfile
import rna_design.email_client

from pymol import cmd
cmd.do("run /Users/amw579/Pymol_DasLab/pymol_daslab.py")

def run_thread(nstruct, sequence, fmt, mutation_list, insertion_list, email):
   
    args = [ '/Users/amw579/Rosetta/main/source/bin/rna_thread_and_minimize.macosclangrelease' ]
    args.extend( ( '-s', 'rna.pdb', '-nstruct', str(nstruct), '-score:weights', 'rna_minimize' ) )
        
    if len( sequence ) > 0:
        args.append( '-seq' )
        args.append( sequence )
        
    if fmt != "DEFAULT":
        args.append( '-input_sequence_type' )
        args.append( fmt )
    
    if len( mutation_list ) > 0:
        args.append( '-mutation_list' )
        args.append( mutation_list )

    if len( insertion_list ) > 0:
        args.append( '-insertion_list' )
        args.append( insertion_list )
    
    f = open( "out.txt", "w" )
    subprocess.call( args, stdout=f )
  
def format_pdb_num(num):
    s = "S_"

    if num < 1000:
        s += "0"
    if num < 100:
        s += "0"
    if num < 10:
        s += "0"
    s += str(num)
    return s + ".pdb"


class SequenceCluster(object):
    def __init__(self, score, pdb_file):
        self.score, self.pdb_file = score, pdb_file


def lines_from( fn ):
    f = open( fn )
    try:
        lines = f.readlines()
    except:
        print "could not open", fn
    f.close()
    return lines

def output_png( pdb, num ):
    try:
        subprocess.call(["pymol", "-pc",  pdb, "-d",  "orient all; rr(); ray 320, 240; png test.png; quit"] )
    except:
        e = sys.exc_info()[0]
        print e
    
	try:
        subprocess.call(["convert", "test.png", "-trim", "cluster_%s.png" % str(num) ])
    except:
        e = sys.exc_info()[0]
        print e
        print "convert failed on", pdb, num


def get_top_clusters():
    
    # score vs rmsd for all!
    f = open("score.sc")
    lines = f.readlines()
    f.close()
    lines.pop(0)

    min_energy = 10000
    max_energy = -1000

    ind_rms = 0
    for l in lines:
        spl = l.split()
        if spl[1] == "total_score":
            # label line
            ind_rms = spl.index( "rms_from_starting" )
        break
    lines.pop(0)

    energies = [ float(line.split()[1]) for line in lines ] 
    RMSDs =    [ float(line.split()[ind_rms]) for line in lines ] 
    
    import matplotlib.pyplot as plt
    plt.scatter( np.array( RMSDs ), np.array( energies ) )
    plt.savefig( "svr.png" )


    # TODO: an actual clustering procedure (this just gives you each decoy)
    lines = [l for l in lines_from( "score.sc" ) if l[0:5] == "SCORE" ]#and l[7:9] != "tot"]
    clusters = []
    for i,l in enumerate(lines):
        if i == 0: continue
        
        print i,l
        spl = l.split()
        if len(clusters) == 0:
            print "appending to clusters"
            # use i, not i+1, since score term names line is 0
            clusters.append(SequenceCluster(spl[1], "%s.pdb" % spl[-1] )) #format_pdb_num(i)))
            continue

        found = False
        # deactivate score repetition - output everything for now
        # (as single mutation runs will be deterministic)
        #for c in clusters:
        #    if spl[1] == c.score:
        #        found = True
        #        break

        if not found:
            clusters.append(SequenceCluster(spl[1], "%s.pdb" % spl[-1] )) #format_pdb_num(i))) 
            if len(clusters) > 4:
                break

    for i,c in enumerate(clusters):
        output_png( c.pdb_file, i+1 )

    f = zipfile.ZipFile("all.zip", "w")
    for name in os.listdir('.'):
        if name[-4:] != '.pdb':
            continue
        f.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
    f.close()


def write_error_file(error):
    f = open("ERROR", "w")
    f.write(error + ', an email has been sent to the administrator, please email amw579@stanford.edu if you have questions')
    f.close()

def update_jobs_file(lines):
    f = open("jobs.dat", "w")
    for l in lines:
        f.write(l)
    f.close()

if __name__ == '__main__' :
    fr = open("run_jobs", "a")

    while True:
        f = open("jobs.dat")
        lines = f.readlines()
        f.close()
                
        if len(lines) == 0:
            time.sleep(5)
            continue
        
        print "job detected!"
    
        spl = lines[0].split(" | ")
        cl = lines.pop(0)
            
        job_dir = spl[0]
        nstruct = int(spl[1])
        sequence=spl[2].rstrip()
        fmt=spl[3].rstrip()
        mutation_list=spl[4].rstrip()
        insertion_list=spl[5].rstrip()
        email=spl[6].rstrip()
    
        os.chdir(job_dir)
        try:
            run_thread(int(nstruct), sequence, fmt, mutation_list, insertion_list, email)
        except:
            print nstruct, "|%s|" % sequence, "|%s|" % fmt, "|%s|" % mutation_list, "|%s|" % insertion_list, email
            write_error_file('rna_thread_and_minimize failed')
            os.chdir("../..")
            update_jobs_file(lines)
            continue
        
        try:
            get_top_clusters()
        except:
            write_error_file('generating top models failed')
            os.chdir("../..")
            update_jobs_file(lines)
            continue
        
        
        os.chdir("../..")
        print "job completed"
                
        if email is not None:
            print email
            #rna_design.email_client.send_email(email, job_dir[5:])
    
        fr.write(cl)
        update_jobs_file(lines)

