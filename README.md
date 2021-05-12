# Running-Blasts-chtc
Information on how to run BLASTs on the CHTC at UW-Madison

## Running one Blast
### 1. Get your files
Get BLAST from NCBI using wget- use latest linux version for chtc (check BLAST website for latest version):
**Note: BLAST program is about ~243 MB, so you need to use large file storage SQUID. See CHTC website for more info https://chtc.cs.wisc.edu/file-avail-squid.shtml**

change to squid directory after logging into chtc:

    cd /squid/username/
 
get blast program:

    wget https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.10.1+-x64-linux.tar.gz
    
Transfer your fasta files using wget if downloading from a website or the scp command or filezilla if transferring from your computer. Again if larger than 100 MB, use squid, otherwise you can download to your home directory.

Example using scp:

    scp your_local_dir/example.fa username@submit2.chtc.wisc.edu:example.fa
    
### 2. make executable file
Open file in nano

    nano blast.sh
    
Configure file:

    #!/bin/bash
    
    #Unzip the tarred BLAST program
    tar -xzf ncbi-blast-2.10.1+-x64-linux.tar.gz
    
    #Format your Blast database (this is used as the subject against your query sequence). -dbtype can be prot or nucl
    ncbi-blast-2.10.1+/bin/makeblastdb -in sub.fasta -dbtype prot 

    #This makes several database files which then need to be moved into 1 folder so they can be called together in the submission file.
    #sub.fasta.00.phr  sub.fasta.00.pin  sub.fasta.00.psq  sub.fasta.01.phr  sub.fasta.01.pin  sub.fasta.01.psq  sub.fasta.pal
    
    # Run blast: blastp: blast on protein sequences; blastn: blast on nucleotide sequences; -num_threads: number of computer cores- this should match what you put in sub file; -db: database fasta file; -query: query fasta; -out: output name; -outfmt: 6 is tab-delimited format, but there are other formats that you can check
    ncbi-blast-2.10.1+/bin/blastp -num_threads X -db sub.fasta -query query.fasta -out subvsquery_results.txt -outfmt 6
    
### 3. Configure the submission file
Open file in nano

    nano blast.sub

Configure sub file. Use this configuration as an example:

    # blast.sub
    # Specify the HTCondor Universe (vanilla is the default and is used
    #  for almost all jobs), the desired name of the HTCondor log file,
    #  and the desired name of the standard error file.
    #  Wherever you see $(Cluster), HTCondor will insert the queue number
    #  assigned to this set of jobs at the time of submission.
    #  $(Process) will be a integer number for each job, starting with "0"
    #  and increasing for the relevant number of jobs.
    #
    universe = vanilla
    log = blast1_$(Cluster).log
    error = blast1_$(Cluster)_$(Process).err
    #
    # Specify your executable (single binary or a script that runs several
    #  commands), arguments, and a files for HTCondor to store standard
    #  output (or "screen output").
    # executable should be whatever you named the executable file
    executable = blast.sh
    # arguments = 
    #
    # Specify that HTCondor should transfer files to and from the
    #  computer where each job runs. The last of these lines *would* be
    #  used if there were any other files needed for the executable to run.
    #
    should_transfer_files = YES
    when_to_transfer_output = ON_EXIT
    # transfer your fasta files and the blast program via squid
    transfer_input_files = sub.fasta,query.fasta,http://proxy.chtc.wisc.edu/SQUID/bmoore22/ncbi-blast-2.10.1+-x64-linux.tar.gz
    # 
    # to transfer only the contents of folder: foldername/ 
    # to transfer contents of folder and folder: foldername
    #
    # Tell HTCondor what amount of compute resources
    #  each job will need on the computer where it runs.
    request_cpus = X # this should match the -num_threads argument in the executable file
    request_memory = 5GB 
    request_disk = 3GB
    #
    # Tell HTCondor to run 1 instances of our job:
    queue 1
    
### 4. Submit the .sub file to HTCondor

    condor_submit blast.sub
    
### 5. Check if your job is running

Check status

    condor_q
    
If the job is held or idle you can see why here:

    condor_q -better-a
    
## Running multiple blasts on chtc
You may want to either a) run many blasts at once, or b) break up one large blast into several to run in parallel

### 1. Dividing fasta file
If you are breaking up a fasta file, then use this python script to divide the file, otherwise skip to step 2

Clone this repository in your directory to get the FastaManager.py script. You will have to set up a key on chtc before you will be able to clone.

    git clone https://github.com/HiroshiLab/Running-Blasts-chtc.git
    
Divide fasta file. flags: -f <function> -fasta <fasta file> -by <number how many times to divide

    python FastaManager.py -f divide -fasta fasta.mod.fa -by 5
    
this divides the file by 5 times

### 2. put divided fasta files into a list:

    ls fasta.mod.fa_* > blast_list.txt
    
### 3. Make executable file:

Open file in nano

    nano blast1.sh
    
Configure file:

    #!/bin/bash
    
    # Unzip the tarred BLAST program
    tar -xzf ncbi-blast-2.10.1+-x64-linux.tar.gz
    # Make database for each divided fasta file (this only takes a few seconds)-remmeber to choose prot or nucl
    for i in fasta.mod.fa_*; do echo $i; ncbi-blast-2.9.0+/bin/makeblastdb -in $i -dbtype nucl; done
    # blast each
    ncbi-blast-2.9.0+/bin/blastp 

### 4. Create a new .sub file

    # blast1.sub
    #
    universe = vanilla
    log = blast1_$(Cluster).log
    error = blast1_$(Cluster)_$(Process).err
    #
    executable =  blast1.sh
    #  $(bl) is the filename that changes in the loop from the blast_list.txt
    # thus each -db and -out will change according to the blast_list.txt
    arguments = -db $(bl) -query query.fa -out $(bl)vs.Q_results.txt
    should_transfer_files = YES
    when_to_transfer_output = ON_EXIT
    # this tells HTCondor to transfer everything from bl_db/ folder and the join.faa file
    transfer_input_files = query.fa
    #
    request_cpus = 1
    request_memory = 5GB
    request_disk = 3GB
    ##
    # Tell condor you want to queue up files in a list
    queue bl from blast_list.txt
    
### 5. Submit the .sub file to HTCondor

    condor_submit blast.sub
    
## Changing the submit file for multiple blasts so results go in their own folder
If you are runnning a very large number of blasts or if you want results to be put in their own folder

### 1. Make new submit file:

    nano blast4.sub
    
    # blast3.sub
    ##
    universe = vanilla
    log = blast1_$(Cluster).log
    error = blast1_$(Cluster)_$(Process).err
    executable = ncbi-blast-2.9.0+/bin/blastn
    # output will go in folder bl_db/
    arguments = -db $(bl) -query Joinvillea_ascendens_subsp._gabra.faa -out bl_db/$(bl)_Joinvi_results.txt
    should_transfer_files = YES
    when_to_transfer_output = ON_EXIT
    # Here you are telling condor to transfer just the given blast file and database for this specific job, not all
    transfer_input_files = bl_db/$(bl), bl_db/$(bl).nhr, bl_db/$(bl).nin, bl_db/$(bl).nsq, Joinvillea_ascendens_subsp._gabra.faa
    request_cpus = 1
    request_memory = 5GB
    request_disk = 500MB
    ##
    # Tell condor you want to queue up files in a list
    queue bl from blast_list.txt

### 2. Submit the .sub file to HTCondor

    condor_submit blast.sub
    
## Get recipricol best match from BLAST output
Note: the input is your blast output from format 6.

    python get_recipricol.py blast.out

