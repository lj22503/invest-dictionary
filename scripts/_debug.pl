use utf8;
use open ':std', ':utf8';
binmode STDIN, ':utf8';
binmode STDOUT, ':utf8';
binmode STDERR, ':utf8';

# Test 1: direct codepoint match
my $s = q{"KaiTi","楷体","PingFang SC",sans-serif};
print "Before: $s\n";
$s =~ s/"[^"]*\x{6977}\x{4F53}[^"]*",?\s*//g;
print "After codepoint: [$s]\n";

# Test 2: HTML-encoded
my $s2 = q{&quot;KaiTi&quot;,&quot;楷体&quot;,&quot;PingFang SC&quot;,sans-serif};
print "Before2: $s2\n";
my $d = $s2;
$d =~ s/&quot;/"/g;
print "Decoded: [$d]\n";
$d =~ s/"[^"]*\x{6977}\x{4F53}[^"]*",?\s*//g;
print "After codepoint: [$d]\n";

# Test 3: check if perl sees 楷体 as 2 chars
my $len = length("楷体");
print "len(楷体) = $len (expect 2)\n";

# Test 4: regex character class with \x
my $s3 = "楷体abc";
if ($s3 =~ /\x{6977}\x{4F53}/) {
  print "Test4: MATCH\n";
} else {
  print "Test4: NO MATCH\n";
}
