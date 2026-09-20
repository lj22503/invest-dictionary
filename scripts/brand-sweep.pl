#!/usr/bin/perl
# Brand sweep v1 — plan Task 6/7 共用扩展 sed 模式
# Usage: perl scripts/brand-sweep.pl <dir> [--recursive]
#   例: perl scripts/brand-sweep.pl web --recursive
#       perl scripts/brand-sweep.pl web/terms
use strict;
use warnings;
use utf8;
use File::Find;

my $dir = shift @ARGV || 'web/terms';

my @files;
if ($dir =~ /terms$/) {
  # 单层扫（terms 子目录）
  opendir(my $dh, $dir) or die "Cannot open $dir: $!";
  @files = map { "$dir/$_" }
    sort grep { /\.html$/ && !/\.bak-/ } readdir($dh);
  closedir($dh);
} else {
  # 递归扫（web/ 根，处理 index.html + subdirs）
  find(
    { wanted => sub {
        return unless /\.html$/;
        return if /\.bak-/;
        push @files, $File::Find::name;
      },
      no_chdir => 1,
    },
    $dir
  );
  @files = sort @files;
}

my $count = 0;
for my $path ( @files ) {
  next unless -f $path;

  open my $in,  '<:encoding(UTF-8)', $path or die "Cannot read $path: $!";
  local $/;
  my $c = <$in>;
  close $in;

  # === A. 朱砂红 hex + rgba ===
  $c =~ s/#C43A31/#F97316/gi;
  $c =~ s/#A33028/#E05E0A/gi;
  $c =~ s/#a92e26/#E05E0A/g;
  $c =~ s/rgba\(\s*196\s*,\s*58\s*,\s*49\s*,/rgba(249,115,22,/g;
  $c =~ s/rgba\(\s*184\s*,\s*34\s*,\s*30\s*,/rgba(249,115,22,/g;

  # === B. 米色 hex ===
  $c =~ s/#F5F2EC/#FFFFFF/gi;
  $c =~ s/#f5efe0/#FFFFFF/g;
  $c =~ s/#faf6ee/#FFFFFF/g;
  $c =~ s/#fdfaf4/#FFFFFF/g;
  $c =~ s/#f8f8f8/#FFFFFF/g;
  $c =~ s/#f0f0f0/#FFFFFF/g;
  $c =~ s/#2C2C2C/#3A332C/gi;
  $c =~ s/#3a3a3a/#3A332C/g;
  $c =~ s/#5A5A5A/#8A7D70/gi;
  $c =~ s/#5a4a3a/#8A7D70/g;
  $c =~ s/#4a4035/#3A332C/g;
  $c =~ s/#6b5e4e/#8A7D70/g;
  $c =~ s/#8b7a65/#8A7D70/g;
  $c =~ s/#6b5040/#8A7D70/g;
  $c =~ s/#b8a58e/#8A7D70/g;
  $c =~ s/#D9D4CC/rgba(36,22,16,0.10)/gi;
  $c =~ s/#c4b5a0/rgba(36,22,16,0.10)/g;
  $c =~ s/#444\b/#3A332C/g;
  $c =~ s/#666\b/#8A7D70/g;
  $c =~ s/#888\b/#8A7D70/g;
  $c =~ s/#999\b/#8A7D70/g;
  $c =~ s/#bbb\b/rgba(36,22,16,0.10)/g;
  $c =~ s/#ddd\b/rgba(36,22,16,0.10)/g;

  # === C. 老国风橙 ===
  $c =~ s/#e8784a/#F97316/gi;
  $c =~ s/#d4745c/#F97316/gi;
  $c =~ s/rgba\(\s*232\s*,\s*120\s*,\s*74\s*,/rgba(249,115,22,/g;

  # === D. 米色 background-image rgba → 透明 ===
  $c =~ s/rgba\(\s*180\s*,\s*160\s*,\s*130\s*,\s*[\d.]+\s*\)/rgba(0,0,0,0)/g;
  $c =~ s/rgba\(\s*160\s*,\s*140\s*,\s*110\s*,\s*[\d.]+\s*\)/rgba(0,0,0,0)/g;
  $c =~ s/rgba\(\s*180\s*,\s*155\s*,\s*120\s*,\s*[\d.]+\s*\)/rgba(0,0,0,0)/g;
  $c =~ s/rgba\(\s*230\s*,\s*215\s*,\s*190\s*,\s*[\d.]+\s*\)/rgba(0,0,0,0)/g;
  $c =~ s/rgba\(\s*220\s*,\s*205\s*,\s*175\s*,\s*[\d.]+\s*\)/rgba(0,0,0,0)/g;

  # === E. 米色阴影 → 暖墨 ===
  $c =~ s/rgba\(\s*60\s*,\s*45\s*,\s*25\s*,/rgba(36,22,16,/g;

  # === F. 楷体/仿宋删除（font-family 段智能清洗 + 追加 emoji） ===
  $c =~ s{(font-family\s*:\s*)([^;]+?)(;)}{
    my ($pre, $chain, $suf) = ($1, $2, $3);
    $chain = _clean_font_chain($chain);
    $pre . $chain . $suf;
  }ges;

  sub _clean_font_chain {
    my $chain = shift;
    my $orig = $chain;

    # inline style 属性里 CSS 用 &quot; encode 引号；解码后再做楷体匹配
    my $decoded = $chain;
    $decoded =~ s/&quot;/"/g;

    # 中文楷体项（用 unicode codepoint 避免 Windows perl 编码问题）
    # 楷=\x{6977} 体=\x{4F53} 仿=\x{4EFF} 宋=\x{5B8B}
    $decoded =~ s/"[^"]*(?:\x{6977}\x{4F53}|\x{4EFF}\x{5B8B})[^"]*",?\s*//g;
    # 英文 KaiTi 系列字面项
    $decoded =~ s/"[^"]*(?:KaiTi|STKaiti|FangSong|STFangsong)[^"]*",?\s*//g;
    # 裸英文标识符
    $decoded =~ s/\b(?:KaiTi|STKaiti|FangSong|STFangsong)\b,?\s*//g;
    # 合并多余逗号
    $decoded =~ s/,\s*,/,/g;
    $decoded =~ s/,\s*\)/)/g;
    $decoded =~ s/\(\s*,/(/g;
    $decoded =~ s/,\s*$/ /;

    # 追加 emoji 字体（如缺）
    if ($decoded !~ /Segoe UI Emoji/) {
      $decoded .= ', "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji"';
    }

    # 如果原 chain 用了 HTML encode，重新 encode（保持 inline style 合法）
    if ($orig =~ /&quot;/ && $decoded =~ /"/) {
      $decoded =~ s/"/&quot;/g;
    }

    return $decoded;
  }

  # === G. theme-color meta ===
  $c =~ s/meta name="theme-color" content="#c43a31"/meta name="theme-color" content="#F97316"/g;

  # === H. inline style 残段（被前次 sweep 拆 font-family 后遗留的 broken CSS 段） ===
  $c =~ s/KaiTi&quot;,&quot;楷体&quot;,&quot;PingFang SC&quot;,sans-serif//g;
  $c =~ s/,KaiTi&quot;,&quot;楷体&quot;,&quot;PingFang SC&quot;,sans-serif//g;

  open my $out, '>:encoding(UTF-8)', $path or die "Cannot write $path: $!";
  print $out $c;
  close $out;
  $count++;
}

print "Processed $count files in $dir\n";
