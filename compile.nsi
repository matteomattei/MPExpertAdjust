!define exe             'mpexpertadjust_portable.exe'
;!define icon            'wp.ico'

!define compressor      'lzma'  ;one of 'zlib', 'bzip2', 'lzma'

; - - - - do not edit below this line, normaly - - - -
!ifdef compressor
    SetCompressor ${compressor}
!else
    SetCompress Off
!endif
Name ${exe}
OutFile ${exe}
SilentInstall silent
!ifdef icon
    Icon ${icon}
!endif

Section
	SetOutPath '$EXEDIR\MPEXPERTADJUST-Portable'
	SetOverwrite on
	File /r build\exe.win32-3.4\*.*
	SetOutPath '$EXEDIR\'
	;nsExec::Exec "$EXEDIR\MPEXPERTADJUST-Portable\mpexpertadjust.exe"
	ExecWait "$EXEDIR\MPEXPERTADJUST-Portable\mpexpertadjust.exe"
	RMDir /r '$EXEDIR\MPEXPERTADJUST-Portable'
SectionEnd