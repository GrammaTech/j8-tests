#!/usr/bin/perl

my %tools = qw(
    wala /cub0/balliet/pidgin-latest/WALA-dontuse
    accrue /cub0/balliet/pidgin-latest/accrue-bytecode
    soot --tool_path=/cub0/balliet/lambda/soot
);
foreach(keys %tools) {
    my $u = uc;
    $tools{$_} = $ENV{$u} if(exists $ENV{$u});
}

my @cmd = qw(python setup.py -v --log_output go.log);
push @cmd, map {
    if(/^\w+$/) {
        my $l = lc $_;
        if(exists $tools{$l}) {
            ("--tool=$_", "--tool_path=$tools{$l}");
        } elsif(-d "src/apps/$_") {
            ("--app=$_");
        } else {
            $_;
        }
    } else {
        $_;
    }
} @ARGV;
print "=> ", join(' ',@cmd), "\n";

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

