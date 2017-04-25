#!/usr/bin/perl

my %tools = qw(
    wala /cub0/balliet/pidgin-latest/WALA-dontuse
    accrue /cub0/balliet/pidgin-latest/accrue-bytecode
    soot --tool_path=/cub0/balliet/lambda/soot
);
my %tests = map { ($_, undef) } qw(callgraph slicing);
foreach(keys %tools) {
    my $u = uc;
    $tools{$_} = $ENV{$u} if(exists $ENV{$u});
}

my @cmd = qw(python setup.py -v --log_output go.log);
my @k = ();
push @cmd, map {
    if(/^\w+$/) {
        my $l = lc;
        if(exists $tools{$l}) {
            ("--tool=$_", "--tool_path=$tools{$l}");
        } elsif(exists $tests{$l}) {
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

while(<log_run/*>) {
    unlink;
}
my $r = system @cmd;
while(<log_run/*>) {
    if(open F, $_) {
        print <F>;
        close F;
    }
}    
exit $r >> 16;

