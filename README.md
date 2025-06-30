to run the app directly using an exe
goto run_app_directly folder and double click the .exe file
1. Kanpressor.exe - images can be compressed and converted from one format to the other
   formats -  ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".heic"
3. KanVCompress.exe - video compressor maintaining the same quality

========================================================

to create a .exe standalone app
pyinstaller --onefile --icon=app.ico --hidden-import=pillow_heif Kanpressor.py

========================================================

to run using code 
python Kanpressor.py
