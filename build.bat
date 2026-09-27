@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo [1/3] 生成图标...
py -3 make_icon.py || goto :err

echo [2/3] 打包 txt2md.exe ...
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name txt2md ^
  --icon icon.ico ^
  --collect-all customtkinter ^
  --hidden-import pystray._win32 ^
  app.py || goto :err

echo [3/3] 复制随附文件到 dist ...
copy /y prompt.md dist\prompt.md >nul
copy /y config.example.json dist\config.example.json >nul

echo.
echo 完成！可执行文件：dist\txt2md.exe
echo 提示：首次运行会生成 config.json，填好自己的 API Key 即可。
pause
exit /b 0

:err
echo.
echo 打包失败，请查看上面的错误信息。
pause
exit /b 1
