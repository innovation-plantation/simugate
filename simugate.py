import exercises.ttl_exercise
import exercises.ff_exercise
import circuit
import gui
import tkinter

def launch_exercise(exercise):
    circuit.Figure.default_canvas = None
    main_window.destroy()
    exercise()

def gui_launch(exercise=None):
    gui.do_gui()
    main_window.destroy()
    if exercise: exercise()

main_window = tkinter.Tk()
tkinter.Button(main_window,text="Flip Flop Exercise",command = lambda: launch_exercise(exercises.ff_exercise.exercise)).pack(fill='x')
tkinter.Button(main_window,text="Transistors Exercise",command = lambda: launch_exercise(exercises.ttl_exercise.exercise)).pack(fill='x')
tkinter.Button(main_window,text="Launch Digital Schematic Editor",command = gui_launch).pack(fill='x')
tkinter.Button(main_window,text="Flip Flop Exercise within editor",command = lambda: gui_launch(exercises.ff_exercise.exercise)).pack(fill='x')
tkinter.Button(main_window,text="Transistors Exercise within editor",command = lambda: gui_launch(exercises.ttl_exercise.exercise)).pack(fill='x')
tkinter.mainloop()



