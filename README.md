# Running-Blasts-chtc
Information on how to run BLASTs on the CHTC at UW-Madison

## Running one Blast
### 1. Get your files
Get BLAST from NCBI:

    wget http://proxy.chtc.wisc.edu/SQUID/osgschool19/ncbi-blast-2.9.0+-x64-linux.tar.gz
    
Transfer your files using wget if downloading or the scp command or filezilla if transferring from your computer

    scp your_local_dir/example.fa username@submit2.chtc.wisc.edu:example.fa
    
### 2. Unzip and format
Unzip the tarred BLAST program

    tar -xzf ncbi-blast-2.9.0+-x64-linux.tar.gz
    
Format your Blast database (this is used as the subject against your query sequence). -dbtype can be prot or nucl

    ncbi-blast-2.9.0+/bin/makeblastdb -in egu.fasta -dbtype prot 

This makes several database files which then need to be moved into 1 folder so they can be called together in the submission file.

    egu.fasta.00.phr  egu.fasta.00.pin  egu.fasta.00.psq  egu.fasta.01.phr  egu.fasta.01.pin  egu.fasta.01.psq  egu.fasta.pal
    
    mkdir egu.fasta1
    
    mv egu.fasta* egu.fasta1/
    
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
    #
    executable = ncbi-blast-2.9.0+/bin/blastp
    arguments = -db egu.fasta -query Streptochaeta_maker_max_proteins_V1.fasta -out JoinvsStreptoch_results.txt
    #
    # Specify that HTCondor should transfer files to and from the
    #  computer where each job runs. The last of these lines *would* be
    #  used if there were any other files needed for the executable to run.
    #
    should_transfer_files = YES
    when_to_transfer_output = ON_EXIT
    transfer_input_files = egu.fasta1/,Streptochaeta_maker_max_proteins_V1.fasta
    # 
    # to transfer only the contents of folder: foldername/ 
    # to transfer contents of folder and folder: foldername
    #
    # Tell HTCondor what amount of compute resources
    #  each job will need on the computer where it runs.
    request_cpus = 1
    request_memory = 10GB
    request_disk = 500MB
    #
    # Tell HTCondor to run 1 instances of our job:
    queue 1
    
### 4. Submit the .sub file to HTCondor

    condor_submit blast.sub
    
## Running multiple blasts on chtc
You may want to either a) run many blasts at once, or b) break up one large blast into several to run in parallel

### 1. Dividing fasta file
If you are breaking up a fasta file, then use this python script to divide the file, otherwise skip to step 2

Clone this repository in your directory to get the FastaManager.py script. You will have to set up a key on chtc before you will be able to clone.

    git clone https://github.com/HiroshiLab/Running-Blasts-chtc.git
    
Divide fasta file. flags: -f <function> -fasta <fasta file> -by <number how many times to divide

    python FastaManager.py -f divide -fasta fasta.mod.fa -by 5
    
this divides the file by 5 times

### 2. Create a new .sub file

    


