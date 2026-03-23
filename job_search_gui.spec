# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['job_search_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('job_search_app', 'job_search_app'),
    ],
    hiddenimports=[
        'job_search',
        # job_search_app package
        'job_search_app',
        'job_search_app.constants',
        'job_search_app.styles',
        'job_search_app.config',
        'job_search_app.status_tracker',
        'job_search_app.widgets',
        'job_search_app.widgets.searchable_multiselect',
        'job_search_app.widgets.job_detail_panel',
        'job_search_app.tabs',
        'job_search_app.tabs.config_tab',
        'job_search_app.tabs.prefs_tab',
        'job_search_app.tabs.cv_tab',
        'job_search_app.tabs.skills_tab',
        'job_search_app.tabs.results_tab',
        # pdfplumber / pdfminer
        'pdfplumber',
        'pdfminer',
        'pdfminer.high_level',
        'pdfminer.layout',
        'pdfminer.pdfpage',
        'pdfminer.pdfinterp',
        'pdfminer.converter',
        'pdfminer.pdfdocument',
        'pdfminer.pdfparser',
        # python-docx
        'docx',
        'docx.oxml',
        'docx.oxml.ns',
        # numpy (required by pandas)
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        # pandas / openpyxl
        'pandas',
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.utils',
        # stdlib extras that PyInstaller sometimes misses
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkPDFViewer',
        'docx2pdf',
        'matplotlib',
        'scipy',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AI Job Search',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # add an .ico path here if you have one
)
