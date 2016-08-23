import time
import sys
import subprocess
import shutil
import os
import zipfile
import rna_design.email_client

def run_thread(nstruct, sequence, fmt, mutation_list, insertion_list, email):

    args = []
    if server_state == "release":
        args.append( 'rna_thread_and_minimize.linuxclangrelease' )
    else:
        args.append( '/Users/amw579/Rosetta/main/source/bin/rna_thread_and_minimize.macosclangrelease' )
    
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
                            
    subprocess.call( args )


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
    def __init__(self, sequence, pdb_file):
        self.sequence, self.pdb_file = sequence , pdb_file


def get_top_clusters():
    # TODO check for max number to format pdb num
    f = open("rna_RNA.sequence_recovery.txt")
    lines = f.readlines()
    f.close()

    native = ""
    for l in lines:
        spl = l.split()
        if len(spl) < 2:
            break
        native += spl[0]

    f = open("rna_RNA.pack.txt")
    lines = f.readlines()
    f.close()

    clusters = []
    f = open('summary.txt', 'w')
    f.write("model  rosetta energy  sequence  % sequence recovery\n")
    for i,l in enumerate(lines):
        spl = l.split()
        same = 0.0
        for j in range(len(spl[1])):
            if native[j] == spl[1][j]:
                same += 1
        percent = (same / float(len(native)))*100

        f.write(format_pdb_num(i+1) + " " + spl[0] + " " + spl[1] + " " + str(percent) + "\n")
    f.close()

    for i,l in enumerate(lines):
        spl = l.split()
        if len(clusters) == 0:
            clusters.append(SequenceCluster(spl[1], format_pdb_num(i+1)))
            continue

        found = 0
        for c in clusters:
            if spl[1] == c.sequence:
                found = 1
                break

        if not found:
            clusters.append(SequenceCluster(spl[1], format_pdb_num(i+1)))
            if len(clusters) > 4:
                break

    # in case you dont get to 5
    for i,l in enumerate(lines):
        spl = l.split()
        if i == 0:
            continue
        clusters.append(SequenceCluster(spl[1], format_pdb_num(i+1)))
        if len(clusters) > 4:
            break

    for i,c in enumerate(clusters):
        if server_state == "release":
            subprocess.call("pymol -pc "+\
                             c.pdb_file + " -d \" rr(); ray 320, 240; png test.png; quit\"",
                             shell=True)
        else:
            subprocess.call("/Applications/MacPyMOL.app/Contents/MacOS/MacPyMOL -pc "+\
                             c.pdb_file + " -d \" rr(); ray 320, 240; png test.png; quit\"",
                             shell=True)


        subprocess.call("convert test.png -trim cluster_" + str(i) + ".png",
                        shell=True)


    shutil.copy('../../output_README', 'README')

    f = zipfile.ZipFile("all.zip", "w")
    for name in os.listdir('.'):
        if name[-4:] != '.pdb' or name[:3] == 'rna':
            continue
        f.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
    f.write("summary.txt", os.path.basename("summary.txt"), zipfile.ZIP_DEFLATED)
    f.write("README",  os.path.basename("README"), zipfile.ZIP_DEFLATED)
    f.close()

def write_fa_file():
    f = open("rna_RNA.pack.txt")
    lines = f.readlines()
    f.close()

    f = open("sequence.fa", "w")
    for i,l in enumerate(lines):
        spl = l.split()
        f.write("> " + str(i) + "\n")
        f.write(spl[1] + "\n")
    f.close()


def generate_weblogo():
    write_fa_file()
    subprocess.call("weblogo -F png --resolution 600 --color green C 'Cytosine' --color red G 'Guanine' --color orange A 'Ade' --color blue U 'Ura' --errorbars NO < sequence.fa > weblogo.png",shell=True)


def write_error_file(error):
    f = open("ERROR", "w")
    f.write(error + ', an email has been sent to the administrator, please email jyesselm@stanford.edu if you have questions')
    f.close()

def update_jobs_file(lines):
    f = open("jobs.dat", "w")
    for l in lines:
        f.write(l)
    f.close()


server_state = "development"
if len(sys.argv) > 1:
    server_state = sys.argv[1]
if server_state not in ("development","release"):
    raise SystemError("ERROR: Only can do development or release")

fr = open("run_jobs", "a")

while True:


    f = open("jobs.dat")
    lines = f.readlines()
    f.close()

    if len(lines) == 0:
        time.sleep(60)
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
        write_error_file('rna_thread_and_minimize failed')
        os.chdir("../..")
        update_jobs_file(lines)
        continue

    get_top_clusters()
    try:
        get_top_clusters()
    except:
        write_error_file('generating top models failed')
        os.chdir("../..")
        update_jobs_file(lines)
        continue

    try:
        generate_weblogo()
    except:
        write_error_file('generating weblogo failed')
        os.chdir("../..")
        update_jobs_file(lines)
        continue

    os.chdir("../..")
    print "job completed"

    if email is not None:
        rna_design.email_client.send_email(email, job_dir[5:])

    fr.write(cl)
    update_jobs_file(lines)

