
from ezzgui.window import Window
from src.program import Program

program = Program()
program.win = Window(size=program.WIN_SIZE, name=program.PROGRAM_NAME)

program.on_create()

program.win.run()