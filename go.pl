#!/usr/bin/perl

my %tools = qw(
    wala /cub0/balliet/pidgin-latest/WALA-dontuse
    accrue /cub0/balliet/pidgin-latest/accrue-bytecode
    soot /cub0/balliet/lambda/soot
    joana /cub0/balliet/lambda/joana
);
my %tests = map { ($_, undef) } qw(callgraph slicing);
foreach(keys %tools) {
    my $u = uc;
    $tools{$_} = $ENV{$u} if(exists $ENV{$u});
}

my @cmd = qw(python run.py -v);
my @k = ();
push @cmd, map {
    if(/^\w+$/) {
        my $l = lc;
        if(exists $tools{$l}) {
            ("--tool=$_=$tools{$l}");
        } elsif(exists $tests{$l} || $l =~ /^([a-z]+)_/ && exists $tests{$1}) {
           push @k, "test_$l";
           ();
        } elsif(-d "src/apps/$_") {
            ("--app=$_");
        } else {
            $_;
        }
    } else {
        $_;
    }
} @ARGV;
push @cmd, "-k", join(' or ', @k) if(@k);
print "=> ", join(' ',map { "'$_'" } @cmd), "\n";
exec @cmd;
