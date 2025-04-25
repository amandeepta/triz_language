; ModuleID = "my_module"
target triple = "x86_64-pc-windows-msvc"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

define i32 @"hel"(i32 %".1", i32 %".2")
{
hel_entry:
  %"b" = alloca i32
  store i32 %".1", i32* %"b"
  %"c" = alloca i32
  store i32 %".2", i32* %"c"
  %".6" = load i32, i32* %"b"
  %".7" = load i32, i32* %"c"
  %".8" = add i32 %".6", %".7"
  ret i32 %".8"
}

define i8* @"s"()
{
s_entry:
  %".2" = bitcast [6 x i8]* @".str_3" to i8*
  %".3" = bitcast [4 x i8]* @"print_fmt_1" to i8*
  %".4" = call i32 (i8*, ...) @"printf"(i8* %".3", i8* %".2")
  %".5" = bitcast [6 x i8]* @".str_5" to i8*
  ret i8* %".5"
}

declare i32 @"printf"(i8* %".1", ...)

@".str_3" = internal constant [6 x i8] c"hello\00"
@"print_fmt_1" = internal constant [4 x i8] c"%s\0a\00"
@".str_5" = internal constant [6 x i8] c"hello\00"
define i32 @"ma"()
{
ma_entry:
  %".2" = alloca i32
  store i32 10, i32* %".2"
  %".4" = alloca i32
  store i32 20, i32* %".4"
  %".6" = load i32, i32* %".2"
  %".7" = load i32, i32* %".4"
  %".8" = call i32 @"hel"(i32 %".6", i32 %".7")
  %".9" = alloca i32
  store i32 %".8", i32* %".9"
  %".11" = bitcast [11 x i8]* @".str_7" to i8*
  %".12" = load i32, i32* %".9"
  %".13" = bitcast [7 x i8]* @"print_fmt_2" to i8*
  %".14" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %".11", i32 %".12")
  ret i32 0
}

@".str_7" = internal constant [11 x i8] c"hello aman\00"
@"print_fmt_2" = internal constant [7 x i8] c"%s %d\0a\00"