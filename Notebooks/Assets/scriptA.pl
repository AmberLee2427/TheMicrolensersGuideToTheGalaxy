#!/usr/bin/perl -w

use strict;
use POSIX;

#my $mmin=log10(31.7828133);
#my $mmax=log10(3178.28133);
my $mmin=log10(.1);
my $mmax=log10(100.);


#idrm fields
#my @rundes=("kgrizuniform");
#jsut a descriptive name, this unique from previous descriptions
my @rundes=("kgriz_uf_ffp_01_100");
#my @rl=(4000,4000,4000,2000,2000,2000,2000,2000,2000,2000);
#rl is number of simulated events in a subrun
my @rl=(10000);
#my @nr=(800,600,400,300,200,100,50,25,10,10);
#nr is number of subruns
my @nr=(1);

#max min semimajor axis
my $amin=log10(0.3);
my $amax=$amin+2;

#my $amin=1;
#my $amax=2;

#inclination, period, semimajor, mass
my $inc; my $p; my $a; my $mass;
#pfile is filename produced
my $pfile;

#just pi
my $pi=4.0*atan(1);

#figre out later
my $nl=$rl[0];
my $nf=$nr[0];


#for r less than length of rundes
for (my $r=0; $r<@rundes; $r++)
{
    my $dir = "${rundes[$r]}";
    #make dir with rundes as name in directory you run from
    if(! -d $dir)
    {
        mkdir($dir);
    }
    #XXX probably need to check
    open(FLD,"<$ENV{'GULLS_BASE_DIR'}/kgriz/KgrizVRIw.sources") || die "Could not open sources file\n";
    #open(FLD,"</home/penny/dmabuls/kgriz/KgrizVRIw.sources") || die "Could not open sources file\n";

    #rundes.sightline.subrun or some combo
    #looping line over list of sightlines or fields
    
    #perl function to read succesive lines from file
    while(my $line=<FLD>)
    {
	#remvoes eol
	chomp($line);
	#split lines by spaces into array
	my @data = split(' ',$line);
	#if length of aray is greater than7, things didnt split right or not right number of columns
	if(@data!=7){next;}
	#make f equal to first element of array (field number)
	my $f = $data[0];
	
	#gen filename base
	my $base = "$dir/${rundes[$r]}.planets.$f.";
	
	print "Writing $base files with $nl lines\n";

	#loop over number of subruns
	for(my $i=0;$i<$nf;$i++)
	{
	    
	    $pfile = "$base$i";
	    #if file exists, don't bother generating
	    if( -e $pfile){next;}
	    #other open up and write to file
	    open(OUT,">$pfile") || die "Could not open output file $pfile\n";
	    
	    #now loop over the number of events generated
	    for(my $j=0;$j<$nl;$j++)
	    {
		$a = 10**($amin + ($amax-$amin)*rand());
		$mass = 3.00374072e-6*10**($mmin + rand()*($mmax-$mmin));
		#$a = 1+int(3*rand())/2;
		my $rnd = rand();
		$inc = 180*($rnd<0.5?acos(2*$rnd):-acos(2-2*$rnd))/$pi;
		#$inc = -90.0 + 180.0*rand();
		$p = 360.0*rand();
		print OUT "$mass $a $inc $p\n";
	    } #end for nlines

	    close(OUT);
	} #end for nfiles
    } #end for fields
    close(FLD);
} #end for rundes

