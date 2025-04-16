; ModuleID = "my_module"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
main_entry:
  %".2" = bitcast [6 x i8]* @".str_2" to i8*
  %".3" = bitcast [4 x i8]* @"print_fmt_1" to i8*
  %".4" = call i32 (i8*, ...) @"printf"(i8* %".3", i8* %".2")
  ret i32 0
}

declare i32 @"printf"(i8* %".1", ...)

@".str_2" = internal constant [6 x i8] c"hello\00"
@"print_fmt_1" = internal constant [4 x i8] c"%s\0a\00"