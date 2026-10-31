@echo off
REM HanTone 一键构建脚本（Windows）
REM 用法: build.bat [test|build|clean]

setlocal
set PYTHON=python

if "%1"=="" goto test
if "%1"=="test" goto test
if "%1"=="build" goto build
if "%1"=="clean" goto clean
echo 用法: build.bat [test|build|clean]
exit /b 1

:test
echo ==^> 运行单元测试
%PYTHON% -m unittest discover -s tests -v
goto end

:build
echo ==^> 构建分发包
%PYTHON% -m pip install --upgrade build
%PYTHON% -m build
echo ==^> 产物位于 dist\
dir dist
goto end

:clean
echo ==^> 清理构建产物
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
goto end

:end
endlocal
