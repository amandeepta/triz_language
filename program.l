; ModuleID = "my_module"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
main_entry:
}

define i32 @"te"(i32 %".1", i32 %".2")
{
te_entry:
  %"i" = alloca i32
  store i32 %".1", i32* %"i"
  %"j" = alloca i32
  store i32 %".2", i32* %"j"
  %".6" = load i32, i32* %"i"
  %".7" = load i32, i32* %"j"
  %".8" = add i32 %".6", %".7"
  ret i32 %".8"
}

define i32 @"check"()
{
check_entry:
  %".2" = alloca i32
  store i32 10, i32* %".2"
  %".4" = alloca i32
  store i32 20, i32* %".4"
  %".6" = load i32, i32* %".2"
  %".7" = load i32, i32* %".4"
  %".8" = call i32 @"te"(i32 %".6", i32 %".7")
  ret i32 %".8"
}
