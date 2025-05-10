; ModuleID = "my_module"
target triple = "x86_64-pc-windows-msvc"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

define i32 @"main"()
{
main_entry:
  %".2" = bitcast [2 x i8]* @".str_2" to i8*
  %".3" = bitcast [4 x i8]* @"print_fmt_1" to i8*
  %".4" = call i32 (i8*, ...) @"printf"(i8* %".3", i8* %".2")
  ret i32 0
}

declare i32 @"printf"(i8* %".1", ...)

@".str_2" = internal constant [2 x i8] c"1\00"
@"print_fmt_1" = internal constant [4 x i8] c"%s\0a\00"