#!/usr/bin/perl
# Task 6 extended sweep — 扩 plan 14 模式覆盖米色/楷体/老国风/朱砂红 rgba
# 2026-09-20 · user 发现 plan sed 漏了米色 rgba + 楷体 + 老国风橙
use strict;
use warnings;
use utf8;

my $dir = 'web/terms';
opendir(my $dh, $dir) or die "Cannot open $dir: $!";
my @files = sort grep { /\.html$/ && !/\.bak-/ } readdir($dh);
closedir($dh);

my $count = 0;
for my $f ( @files ) {
  my $path = "$dir/$f";
  open my $in,  '<:raw', $path or die "Cannot read $path: $!";
  local $/;
  my $c = <$in>;
  close $in;

  # === A. 朱砂红 hex + rgba ===
  $c =~ s/#C43A31/#F97316/gi;
  $c =~ s/#A33028/#E05E0A/gi;
  $c =~ s/#a92e26/#E05E0A/g;
  $c =~ s/rgba\(\s*196\s*,\s*58\s*,\s*49\s*,/rgba(249,115,22,/g;
  $c =~ s/rgba\(\s*184\s*,\s*34\s*,\s*30\s*,/rgba(249,115,22,/g;

  # === B. 米色 hex（背景/卡面/文字/辅助） ===
  $c =~ s/#F5F2EC/#FFFFFF/gi;
  $c =~ s/#f5efe0/#FFFFFF/g;
  $c =~ s/#faf6ee/#FFFFFF/gi;
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

  # === C. 老国风橙（hex + rgba） ===
  $c =~ s/#e8784a/#F97316/gi;
  $c =~ s/#d4745c/#F97316/gi;
  $c =~ s/rgba\(\s*232\s*,\s*120\s*,\s*74\s*,/rgba(249,115,22,/g;

  # === D. 米色 background-image rgba（宣纸光斑/横线）→ 透明 ===
  $c =~ s/rgba\(\s*180\s*,\s*160\s*,\s*130\s*,\s*[\d.]+\s*\)/rgba(0,0,0,0)/g;
  $c =~ s/rgba\(\s*160\s*,\s*140\s*,\s*110\s*,\s*[\d.]+\s*\)/rgba(0,0,0,0)/g;
  $c =~ s/rgba\(\s*180\s*,\s*155\s*,\s*120\s*,\s*[\d.]+\s*\)/rgba(0,0,0,0)/g;
  $c =~ s/rgba\(\s*230\s*,\s*215\s*,\s*190\s*,\s*[\d.]+\s*\)/rgba(0,0,0,0)/g;
  $c =~ s/rgba\(\s*220\s*,\s*205\s*,\s*175\s*,\s*[\d.]+\s*\)/rgba(0,0,0,0)/g;

  # === E. 米色阴影（暖棕）→ 暖墨 ===
  $c =~ s/rgba\(\s*60\s*,\s*45\s*,\s*25\s*,/rgba(36,22,16,/g;

  # === F. 楷体/仿宋删除（多行匹配，末尾带逗号+空白） ===
  $c =~ s/"KaiTi",\s*"楷体",\s*"STKaiti",\s*"FangSong",\s*"仿宋",\s*"STFangsong",\s*//gs;
  $c =~ s/"KaiTi",\s*"楷体",\s*"STKaiti",\s*//gs;
  $c =~ s/"FangSong",\s*"仿宋",\s*//gs;
  $c =~ s/"KaiTi",\s*"楷体",\s*//gs;

  # === G. theme-color meta ===
  $c =~ s/meta name="theme-color" content="#c43a31"/meta name="theme-color" content="#F97316"/g;

  open my $out, '>:raw', $path or die "Cannot write $path: $!";
  print $out $c;
  close $out;
  $count++;
}

print "Processed $count files\n";
