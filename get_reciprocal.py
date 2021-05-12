import sys
def get_recipricol(blast,idenT,expcT):
    inp = open(blast, "r") #get file
    inl = inp.readline()         #read first line of file
    #get and define best matches for query and subject seperately
    BMQ= {}
    BMS= {}
    while inl != "":
        L = inl.split("/t")
        q = L[0]            #query
        s = L[1]            #subject
        p = float(L[2])     #percent identity
        E = float(L[-2])    #e-value
        
        if p >= idenT and E < expcT:  #p and E filters
        	# if original e-val is higher than new, replace
            if q not in BMQ or BMQ[q][1] > E:  #update BMQ if q does not exist
                BMQ = [s,E]                   # or original e higher than new e
            # Do the same for BMS[s]
            if s not in BMS or BMS[s][1] > E:
                BMS = [q,E]
                
        inl = inp.readline()
    #now check for reciprocal best match and output
    output = open(blast+".recipricol","w")
    for q in BMQ:
        s = BMQ[q][0]
        if s in BMS:
            if q == BMS[s]:
                output.write("%s\t%s\n" % (q,s))
    inp.close()
    output.close()
    print ("Done!")

inp= sys.argv[1]
idenT = 60
expcT = 1e-10
get_recipricol(inp, idenT, expcT)    
