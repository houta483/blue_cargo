import pyautogui

startButton = pyautogui.locateCenterOnScreen('asdf.png', confidence=0.9)
x_coordinate = startButton[0] - 720
y_coordinate = startButton[1] - 30
pyautogui.moveTo(startButton, duration=2)
