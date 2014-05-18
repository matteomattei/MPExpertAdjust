rmdir build /s /q
rmdir MPExpertAdjust /s /q
del /s /q mpexpertadjust_portable.exe
C:\python34\python.exe setup.py build
"C:\Program Files\NSIS\makensis.exe" compile.nsi