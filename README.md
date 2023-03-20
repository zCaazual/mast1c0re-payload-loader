# mast1c0re-payload-loader

PS4-PS5  mast1c0re payload loader
All credits to @_mccaulay

I just made the UI.

You can rename and customize the folders and payloads to how you want.

They are created dynamically so you can group them and display them how you want without touching the code itself.

All user made folders "Must" be creaded inside the "Elf" folder.

If you only want to use the payloads you use for your FW you can simply remove the others.

I tried to make it as user friendly as possible.

The UI itself will change color depending on your "System" theme setting.

For example if you are using the "Dark Mode" theme the UI will be dark.

If you are using the "Light Mode" theme the UI will be white.

A small issue with the canvas i was creating to display the buttons is set to a hardcoded color.

If you use the "light Mode" theme on your computer you can simply change line "263" 

subfolder_canvas = customtkinter.CTkCanvas(tab, height=300, width=570, bg="#292726", highlightthickness=0)

To this 

subfolder_canvas = customtkinter.CTkCanvas(tab, height=300, width=570, bg="white", highlightthickness=0)

You will need to install the custom tkinter lib to compile.

Install > pip install customtkinter

Open cmd inside the same folder as the payload loader.py.

For compilation im using pyinstaller > pyinstaller --noconfirm --onedir --noconsole --add-data "C:\Users\username\AppData\Local\Programs\Python\Python311\Lib\site-packages/customtkinter;customtkinter/" "payload loader.py"

You must include the full path to the custom tkinter lib.

If you dont want to compile it, simply install the dependencies and run the code from the cmd terminal.

Open cmd in the same dir as the payload loader.py.

Run with > python "payload loader.py"
![image1](https://user-images.githubusercontent.com/100888891/226332981-0b5b87c1-71e8-41e2-8b20-8eedc83d11f3.png)

![image2](https://user-images.githubusercontent.com/100888891/226333020-6b84e9f7-9c09-4c09-a998-c1cf3530c78b.png)



