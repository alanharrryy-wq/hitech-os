@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo [LEGACY] Este acceso ahora ejecuta el self-test de Prisma Cloud Center.
call "%~dp001_SELF_TEST_PRISMA_CLOUD_CENTER.cmd"
